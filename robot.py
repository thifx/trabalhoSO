import math
from multiprocessing import shared_memory
import os
import threading
import numpy as np
import time
from global_configs import tabuleiro_dtype, robot_dtype, linhas, colunas
from time import sleep

class Robot:
    def __init__(self, idx, shm_name_robots, shm_name_grid, robots_mutex, grid_mutex, baterias_dict_mutex, game_over_flag):
        self.idx = idx

        self.game_over_flag = game_over_flag
        
        self.robots_mutex = robots_mutex
        self.grid_mutex = grid_mutex
        self.baterias_dict_mutex = baterias_dict_mutex

        self.shm_robots = shared_memory.SharedMemory(name=shm_name_robots)
        self.shm_grid = shared_memory.SharedMemory(name=shm_name_grid)

        self.robots = np.ndarray((2,), dtype=robot_dtype, buffer=self.shm_robots.buf)
        self.grid = np.ndarray((linhas, colunas), dtype=np.int8, buffer=self.shm_grid.buf)

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

    def collect_battery(self):
        self.robots_mutex.acquire()
        try:
            if self.energy < 100:
                self.energy = min(100, self.energy + 20)
                self.robots[self.idx]['energy'] = self.energy
            if self.pos in self.baterias_dict_mutex:
                self.baterias_dict_mutex.pop(self.pos, None)
        finally:
            self.robots_mutex.release()
        
        grid = np.ndarray((linhas, colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)
        self.grid_mutex.acquire()
        try:
            x, y = self.pos
            if grid[x, y] == 2:
                grid[x, y] = 10
        finally:
            self.grid_mutex.release()


    def fight(self):
        robot_list = self.robots
        for robot in robot_list:
            if tuple(robot['pos']) == self.pos and robot['id'] != self.id:
                power_1 = 2 * self.strength + self.energy
                power_2 = 2 * robot['strength'] + robot['energy']
                if power_1 == power_2:
                    self.status = 0
                    robot['status'] = 0

                    grid = np.ndarray((linhas, colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)
                    self.grid_mutex.acquire()
                    try:
                        x, y = self.pos
                        grid[x, y] = 0
                    finally:
                        self.grid_mutex.release()

                elif power_1 > power_2:
                    robot['status'] = 0

                    grid = np.ndarray((linhas, colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)
                    self.grid_mutex.acquire()
                    try:
                        x, y = robot['pos']
                        grid[x, y] = 0
                    finally:
                        self.grid_mutex.release()
                
                else:
                    self.status = 0

                    grid = np.ndarray((linhas, colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)
                    self.grid_mutex.acquire()
                    try:
                        x, y = self.pos
                        grid[x, y] = 0
                    finally:
                        self.grid_mutex.release()
                break

    def move(self, pos_y, pos_x):
        grid = np.ndarray((linhas, colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)

        my_x, my_y = self.pos 
        distancex = pos_x - my_x
        distancey = pos_y - my_y
        step_x = int(np.sign(distancex))
        step_y = int(np.sign(distancey))
        new_x = my_x + step_x
        new_y = my_y + step_y
        target = self.valid_move(new_x, new_y, grid)
        if target is not None:
            try:
                print(f"[MOVE] Robô {self.robot_id} tentando mover de ({my_y}, {my_x}) para ({new_x}, {new_y})")
                grid[my_x, my_y] = 0
                grid[new_x, new_y] = 10
                print(f"[MOVE] Robô {self.robot_id} movido para ({new_x}, {new_y})")
                print(step_x, step_y)
                self.pos = (new_x, new_y)
                sleep(3)
            except Exception as e:
                print(f"[MOVE] Erro ao mover robô {self.robot_id}: {e}")
            finally:
                # self.robots_mutex.release()
                pass
            # if target == 2:
            #     key = f"{new_x}{new_y}"
            #     mutex = self.baterias_dict_mutex.get((key), None)
            #     if mutex:
            #         mutex.acquire()
            #         try:
            #             self.collect_battery()
            #         finally:
            #             mutex.release()
            # elif target == 10 or target == 99:
            #     try:
            #         self.robots_mutex.acquire()
            #         self.fight()
            #     finally:
            #         self.robots_mutex.release()


    def valid_move(self, pos_x, pos_y, grid):

        if pos_x < 0 or pos_x >= linhas or pos_y < 0 or pos_y >= colunas:
            return None
    
        valor_do_tabuleiro = grid[pos_x, pos_y]
        if valor_do_tabuleiro == 1:
            return None
        return valor_do_tabuleiro

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def sense_act(self):
        while self.status != 0 and self.game_over_flag.value == 0:
            local_grid = self.grid.copy()

            battery_pos = np.argwhere(local_grid == 2)
            enemy_pos = [tuple(pos) for pos in np.argwhere(local_grid == 10) if tuple(pos) != self.pos]
            my_pos = self.pos

            minor_e_dist = 1000000.0
            enemy_selected = (0, 0)

            minor_b_dist = 1000000.0
            battery_selected = (0, 0)

            for enemy in enemy_pos:
                distance = self.distance(my_pos[0], my_pos[1], enemy[0], enemy[1])
                if distance < minor_e_dist:
                    minor_e_dist = distance
                    enemy_selected = (enemy[0], enemy[1])
        
            for battery in battery_pos:
                distance = self.distance(my_pos[0], my_pos[1], battery[0], battery[1])
                if distance < minor_b_dist:
                    minor_b_dist = distance
                    battery_selected = (battery[0], battery[1])
            if self.energy < 80:
                self.move(battery_selected[0], battery_selected[1])
        
            # else:
            #     self.grid_mutex.acquire()
            #     if minor_e_dist < minor_b_dist:
            #         self.move(enemy_selected[0], enemy_selected[1])
            #     else:
            #         self.move(battery_selected[0], battery_selected[1])
            #     self.grid_mutex.release()

    def housekeeping(self):
        while self.status != 0 and self.game_over_flag.value == 0:
            time.sleep(2)

            self.robots_mutex.acquire()
            try:
                self.energy = max(0, self.energy - 1)
                print(f"[HK] Robô {self.robot_id}: energia {self.energy}")

                if self.energy == 0:
                    self.status = "morto"
                    print(f"[HK] Robô {self.robot_id} morreu por falta de energia")

                self.robots[self.idx]['energy'] = self.energy
                self.robots[self.idx]['status'] = 0 if self.status == "morto" else 1
            finally:
                self.robots_mutex.release()

            self.robots_mutex.acquire()
            try:
                vivos = np.sum(self.robots['status'] == 1)
                if vivos == 1:
                    print(f"[HK] Robô {self.robot_id} detectou o fim do jogo.")
                    self.game_over_flag.value = 1
                    return
            finally:
                self.robots_mutex.release()