from multiprocessing import shared_memory
from global_configs import *
import os
import threading
import numpy as np
import time
import random
import math

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
        while self.robots[self.idx]['status'] != 0 and self.game_over_flag.value == 0:
            time.sleep(1/self.speed)
            with self.grid_mutex:
                # Escolhe um movimento aleatório
                #pos_x_to_sum, pos_y_to_sum = random.choice(self.movimentos) 
                current_pos_x, current_pos_y = self.pos[0], self.pos[1]
                nova_pos_x, nova_pos_y = self.achar_melhor_proxima_posicao()
                #nova_pos_x,nova_pos_y = current_pos_x + pos_x_to_sum,current_pos_y + pos_y_to_sum
                
                if self.valid_move(nova_pos_x, nova_pos_y) is not None:
                        conteudo_celula_movimento = self.grid[nova_pos_x, nova_pos_y]
                        
                        if conteudo_celula_movimento == 0:# Espaço vazio
                            self.mover_robo_celula_vazia((nova_pos_x, nova_pos_y))

                        elif conteudo_celula_movimento == 2:# Energia
                            self.coletar_bateria(nova_pos_x, nova_pos_y, current_pos_x, current_pos_y, logger)

                        elif conteudo_celula_movimento == 10 or conteudo_celula_movimento==99: #Algum outro robô
                            self.duelo(nova_pos_x, nova_pos_y, current_pos_x, current_pos_y, logger)

    def achar_melhor_proxima_posicao(self):
        enemy_pos = [tuple(pos) for pos in np.argwhere(self.grid == 10 ) if tuple(pos) != tuple(self.pos)]
        battery_pos = [tuple(pos) for pos in np.argwhere(self.grid == 2 )]
        
        if self.robots[self.idx]['energy'] < 15 and battery_pos:
            closest_battery = None
            min_distance = float('inf')
            my_pos = self.robots[self.idx]['pos']

            for battery in battery_pos:
                distance = self.distance(my_pos[0], my_pos[1], battery[0], battery[1])
                if distance < min_distance:
                    min_distance = distance
                    closest_battery = battery

            if closest_battery is not None:
                pos_x, pos_y = closest_battery
                my_x, my_y = my_pos
                distancex = pos_x - my_x
                distancey = pos_y - my_y

                if abs(distancex) > 0:
                    step_x = int(np.sign(distancex))
                    new_x = my_x + step_x
                    new_y = my_y
                else:
                    step_y = int(np.sign(distancey))
                    new_x = my_x
                    new_y = my_y + step_y

                if self.valid_move(new_x, new_y) is None:
                    choice = random.choice(self.movimentos)
                    return (my_pos[0] + choice[0], my_pos[1] + choice[1])
                else:
                    return (new_x, new_y)
                    
        for robot in self.robots:
            if robot['type'] == 99 and robot['status'] != 0:
                enemy_pos.append(tuple(robot['pos'])) 

        my_pos = self.robots[self.idx]['pos']

        minor_e_dist = float('inf')
        enemy_selected = None

        for enemy in enemy_pos:
            distance = self.distance(my_pos[0], my_pos[1], enemy[0], enemy[1])
            if distance < minor_e_dist:
                minor_e_dist = distance
                enemy_selected = (enemy[0], enemy[1])

        if enemy_selected is None:
            choice = random.choice(self.movimentos)
            return (my_pos[0] + choice[0], my_pos[1] + choice[1])

        pos_x, pos_y = enemy_selected
        my_x, my_y = my_pos
        distancex = pos_x - my_x
        distancey = pos_y - my_y

        if abs(distancex) > 0:
            step_x = int(np.sign(distancex))
            new_x = my_x + step_x
            new_y = my_y
        else:
            step_y = int(np.sign(distancey))
            new_x = my_x
            new_y = my_y + step_y

        if (self.encontrar_robo_por_posicao((new_x, new_y)) is not None):
            robo_inimigo = self.encontrar_robo_por_posicao((new_x, new_y))
            if robo_inimigo['status'] == 0:
                choice = random.choice(self.movimentos)
                return (my_pos[0] + choice[0], my_pos[1] + choice[1])

        if self.valid_move(new_x, new_y) is None:
            choice = random.choice(self.movimentos)
            return (my_pos[0] + choice[0], my_pos[1] + choice[1])

        return (new_x, new_y)

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def housekeeping(self):
        while self.robots[self.idx]['status'] != 0 and self.game_over_flag.value == 0:
            time.sleep(0.1)

            self.robots_mutex.acquire()
            try:
                energia = self.robots[self.idx]['energy']
                energia = max(0, energia - 1)
                self.robots[self.idx]['energy'] = energia
                self.energy = self.robots[self.idx]['energy']
                if energia == 0:
                    self.robots[self.idx]['status'] = 0
                    self.status = self.robots[self.idx]['status']
                    print(f"[HK] Robô {self.robot_id} morreu por falta de energia")
                    logger.info(f"Robô {self.robot_id} morreu por falta de energia")
                else:
                    self.robots[self.idx]['status'] = 1
                    self.status = self.robots[self.idx]['status']
                
                #Verificar os robos vivos e se existe algum vencedor
                status_array = self.robots['status']
                vivos = np.sum(status_array == 1)
                print(f"[HK] Robô {self.robot_id}: energia {energia}, robôs vivos: {vivos}")
                logger.info(f"Robô {self.robot_id}: energia {energia}, robôs vivos: {vivos}")

                if vivos == 1 and self.robots[self.idx]['status'] == 1:
                    print(f"[HK] VENCEDOR! Robô {self.robot_id} é o grande ganhador! Fim do jogo.")
                    logger.info(f"[HK] VENCEDOR! Robô {self.robot_id} é o grande ganhador! Fim do jogo.")
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
    
    def encontrar_robo_por_posicao(self, posicao):
        for robo in self.robots:
            if tuple(robo['pos']) == tuple(posicao) and robo['status'] != 0:
                return robo
        return None
    
    def calcular_forca_duelo(self,forca,energia):
        return 2 * forca + energia
    
    def mover_robo_celula_vazia(self, nova_pos):
        current_x, current_y = self.pos
        nova_x, nova_y = nova_pos

        self.grid[current_x, current_y] = 0
        self.grid[nova_x, nova_y] = 10

        with self.robots_mutex:
            print(f"[SA] Robô {self.robot_id} se moveu da posição ({current_x}, {current_y}) para ({nova_x}, {nova_y})")
            logger.info(f"Robô {self.robot_id} se moveu da posição ({current_x}, {current_y}) para ({nova_x}, {nova_y})")
            self.robots[self.idx]['pos'] = nova_pos
            self.pos = nova_pos

    def coletar_bateria(self, nova_pos_x, nova_pos_y, current_pos_x, current_pos_y, logger):
        print(f"[SA] Robô {self.robot_id} encontrou uma bateria na posição ({nova_pos_x}, {nova_pos_y})")
        logger.info(f"Robô {self.robot_id} encontrou uma bateria na posição ({nova_pos_x}, {nova_pos_y})")

        key = f"{nova_pos_x}{nova_pos_y}"
        print(f"[SA] Tentando pegar a bateria na posição com a chave {key} no mutex ({nova_pos_x}, {nova_pos_y})")
        logger.info(f"Tentando pegar a bateria na posição com a chave {key} do mutex ({nova_pos_x}, {nova_pos_y})")

        with self.baterias_dict_mutex.get(key):
            print(f"[SA] Robô {self.robot_id} pegou a bateria na posição ({nova_pos_x}, {nova_pos_y})")
            logger.info(f"Robô {self.robot_id} pegou a bateria na posição ({nova_pos_x}, {nova_pos_y})")
            
            self.grid[current_pos_x, current_pos_y] = 0
            self.grid[nova_pos_x, nova_pos_y] = 10
            self.robots[self.idx]['pos'] = (nova_pos_x, nova_pos_y)
            self.pos = (nova_pos_x, nova_pos_y)
            
            with self.robots_mutex:
                energia_incrementada = self.energy + 20
                self.robots[self.idx]['energy'] = min(100, energia_incrementada)
                self.energy = self.robots[self.idx]['energy']

                print(f"[SA] Robô {self.robot_id} agora tem {self.energy} de energia")
                logger.info(f"Robô {self.robot_id} agora tem {self.energy} de energia")

    def duelo(self, nova_pos_x, nova_pos_y, current_pos_x, current_pos_y, logger):
        with self.robots_mutex:
            robo_inimigo = self.encontrar_robo_por_posicao((nova_pos_x, nova_pos_y))

            if robo_inimigo is None:
                print(f"[SA] Robô {self.robot_id} encontrou um robo inativo na posicao ({nova_pos_x}, {nova_pos_y})")
                logger.info(f"Robô {self.robot_id} encontrou um robo inativo na posicao ({nova_pos_x}, {nova_pos_y})")
                return

            print(f"[SA] Robô {self.robot_id} encontrou o robô {robo_inimigo['id']} na posição ({nova_pos_x}, {nova_pos_y})")
            logger.info(f"Robô {self.robot_id} encontrou o robô {robo_inimigo['id']} na posição ({nova_pos_x}, {nova_pos_y})")

            poder_de_duelo = self.calcular_forca_duelo(self.strength, self.energy)
            poder_de_duelo_inimigo = self.calcular_forca_duelo(robo_inimigo['strength'], robo_inimigo['energy'])

            #Empate
            if poder_de_duelo == poder_de_duelo_inimigo:
                print(f"[SA] Robô {self.robot_id} e robô {robo_inimigo['id']} empataram no duelo")
                logger.info(f"Robô {self.robot_id} e robô {robo_inimigo['id']} empataram no duelo")

                self.robots[self.idx]['energy'] = 0
                self.energy = 0
                self.robots[self.idx]['status'] = 0
                self.status = 0
                self.robots[self.idx]['pos'] = (-1, -1)
                self.pos = (-1, -1)

                robo_inimigo['energy'] = 0
                robo_inimigo['status'] = 0
                robo_inimigo['pos'] = (-1, -1)

                self.grid[current_pos_x, current_pos_y] = 0
                self.grid[nova_pos_x, nova_pos_y] = 0

                print(f"[SA] Robô {self.robot_id} e robô {robo_inimigo['id']} morreram no duelo")
                logger.info(f"Robô {self.robot_id} e robô {robo_inimigo['id']} morreram no duelo")
            #Vitoria do desafiante
            elif poder_de_duelo > poder_de_duelo_inimigo:
                print(f"[SA] Robô {self.robot_id} venceu o duelo contra o robô {robo_inimigo['id']}")
                logger.info(f"Robô {self.robot_id} venceu o duelo contra o robô {robo_inimigo['id']}")

                robo_inimigo['status'] = 0
                robo_inimigo['energy'] = 0
                robo_inimigo['pos'] = (-1, -1)

                self.grid[current_pos_x, current_pos_y] = 0
                self.grid[nova_pos_x, nova_pos_y] = 10
                self.robots[self.idx]['pos'] = (nova_pos_x, nova_pos_y)
                self.pos = self.robots[self.idx]['pos']

                print(f"[SA] Robô {self.robot_id} agora está na posição ({nova_pos_x}, {nova_pos_y})")
                logger.info(f"Robô {self.robot_id} agora está na posição ({nova_pos_x}, {nova_pos_y})")
            # Derrota do desafiante
            else:
                print(f"[SA] Robô {self.robot_id} perdeu o duelo contra o robô {robo_inimigo['id']}")
                logger.info(f"Robô {self.robot_id} perdeu o duelo contra o robô {robo_inimigo['id']}")

                self.robots[self.idx]['energy'] = 0
                self.energy = 0
                self.robots[self.idx]['status'] = 0
                self.status = 0
                self.robots[self.idx]['pos'] = (-1, -1)
                self.pos = (-1, -1)

                self.grid[current_pos_x, current_pos_y] = 0

                print(f"[SA] Robô {self.robot_id} morreu na posição ({current_pos_x}, {current_pos_y})")
                logger.info(f"Robô {self.robot_id} morreu na posição ({current_pos_x}, {current_pos_y})")
