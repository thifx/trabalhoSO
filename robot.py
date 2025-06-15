from multiprocessing import shared_memory
from global_configs import *
import os
import threading
import numpy as np
import time
import random

class Robot:
    def __init__(self, idx, shm_name_robots, shm_name_grid, robots_mutex,grid_mutex,baterias_dict_mutex, game_over_flag):
        self.idx = idx
        self.movimentos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        self.game_over_flag = game_over_flag
        self.robots_mutex = robots_mutex
        self.grid_mutex = grid_mutex
        self.baterias_dict_mutex = baterias_dict_mutex

        self.shm_robots = shared_memory.SharedMemory(name=shm_name_robots)
        self.shm_grid = shared_memory.SharedMemory(name=shm_name_grid)

        self.robots = np.ndarray((num_robots,), dtype=robot_dtype, buffer=self.shm_robots.buf)
        self.grid = np.ndarray((linhas, colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)

    def __call__(self):
        self.run()
    
    def run(self):
        robot = self.robots[self.idx]
        self.robot_id = os.getpid()
        self.strength = robot['strength']
        self.energy = robot['energy']
        self.speed = robot['speed']
        self.status = robot['status']
        self.pos = int(robot['pos'][0]), int(robot['pos'][1])
        self.type = robot['type']

        print(f"Robot {self.robot_id} of type {self.type} started with strength {self.strength}, energy {self.energy}, speed {self.speed}, status {self.status}, position {self.pos}")
        logger

        thread1 = threading.Thread(target=self.sense_act, name="sense_act")
        thread2 = threading.Thread(target=self.housekeeping, name="housekeeping")

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

    def sense_act(self):
        while self.status != 0 and self.game_over_flag.value == 0:
            time.sleep(1 / self.speed)

            pos_x_to_sum, pos_y_to_sum = random.choice(self.movimentos) # Escolhe um movimento aleatório
            current_pos_x, current_pos_y = self.pos[0], self.pos[1]
            
            if self.valid_move(current_pos_x + pos_x_to_sum, current_pos_y + pos_y_to_sum) is not None:
                with self.grid_mutex:
                    conteudo_celula_movimento = self.grid[current_pos_x + pos_x_to_sum, current_pos_y + pos_y_to_sum]
                    #Apenas andando
                    nova_pos_x, nova_pos_y = current_pos_x + pos_x_to_sum, current_pos_y + pos_y_to_sum
                    self.grid[current_pos_x, current_pos_y] = 0
                    self.grid[nova_pos_x, nova_pos_y] = 10
                    self.pos = (nova_pos_x, nova_pos_y)
                    self.robots[self.idx]['pos'] = self.pos

    def housekeeping(self):
        while self.status != 0 and self.game_over_flag.value == 0:
            time.sleep(0.2)

            self.robots_mutex.acquire()
            try:
                energia = self.robots[self.idx]['energy']
                energia = max(0, energia - 1)
                self.energy = energia
                self.robots[self.idx]['energy'] = energia
                if energia == 0:
                    self.robots[self.idx]['status'] = 0
                    self.status = 0
                    print(f"[HK] Robô {self.robot_id} morreu por falta de energia")
                    logger.info(f"Robô {self.robot_id} morreu por falta de energia")
                else:
                    self.robots[self.idx]['status'] = 1
                    self.status = 1
                
                #Verificar os robos vivos e se existe algum vencedor
                status_array = self.robots['status']
                vivos = np.sum(status_array == 1)
                print(f"[HK] Robô {self.robot_id}: energia {energia}, robôs vivos: {vivos}")
                logger.info(f"Robô {self.robot_id}: energia {energia}, robôs vivos: {vivos}")

                if vivos == 1 and self.robots[self.idx]['status'] == 1:
                    print(f"[HK] Robô {self.robot_id} é o vencedor! Fim do jogo.")
                    logger.info(f"Robô {self.robot_id}: energia {energia}, robôs vivos: {vivos}")
                    self.game_over_flag.value = 1
                    return
                
                if self.robots[self.idx]['status'] == 0 or self.game_over_flag.value == 1:
                    return
            finally:
                self.robots_mutex.release()

    def valid_move(self, pos_x, pos_y):
            if pos_x < 0 or pos_x >= linhas or pos_y < 0 or pos_y >= colunas:
                return None
        
            valor_do_tabuleiro = self.grid[pos_x, pos_y]
            if valor_do_tabuleiro == 1:
                return None
            return valor_do_tabuleiro