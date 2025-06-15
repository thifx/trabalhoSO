from multiprocessing import shared_memory
from global_configs import robot_dtype,tabuleiro_linhas, tabuleiro_colunas,tabuleiro_dtype
import os
import threading
import numpy as np
import time

class Robot:
    def __init__(self, idx, shm_name_robots, shm_name_grid, robots_mutex, game_over_flag, linhas=tabuleiro_linhas, colunas=tabuleiro_colunas):
        self.idx = idx
        self.linhas = linhas
        self.colunas = colunas

        self.game_over_flag = game_over_flag
        self.robots_mutex = robots_mutex

        self.shm_robots = shared_memory.SharedMemory(name=shm_name_robots)
        self.shm_grid = shared_memory.SharedMemory(name=shm_name_grid)

        self.robots = np.ndarray((4,), dtype=robot_dtype, buffer=self.shm_robots.buf)
        self.grid = np.ndarray((self.linhas, self.colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)

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

        thread1 = threading.Thread(target=self.sense_act, name="sense_act")
        thread2 = threading.Thread(target=self.housekeeping, name="housekeeping")

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

    def sense_act(self):
        # Implementação do thread sense_act
        pass

    def housekeeping(self):
        while self.status != 0 and self.game_over_flag.value == 0:
            time.sleep(0.2)

            self.robots_mutex.acquire()
            try:
                energia = self.robots[self.idx]['energy']
                energia = max(0, energia - 1)
                self.robots[self.idx]['energy'] = energia
                if energia == 0:
                    self.robots[self.idx]['status'] = 0
                    print(f"[HK] Robô {self.robot_id} morreu por falta de energia")

                else:
                    self.robots[self.idx]['status'] = 1
                status_array = self.robots['status']
                vivos = np.sum(status_array == 1)
                print(f"[HK] Robô {self.robot_id}: energia {energia}, robôs vivos: {vivos}")

                if vivos == 1 and self.robots[self.idx]['status'] == 1:
                    print(f"[HK] Robô {self.robot_id} é o vencedor! Fim do jogo.")
                    self.game_over_flag.value = 1
                    return
                
                if self.robots[self.idx]['status'] == 0 or self.game_over_flag.value == 1:
                    return
            finally:
                self.robots_mutex.release()