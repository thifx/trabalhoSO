from multiprocessing import shared_memory
import os
import threading
import numpy as np
import time

robot_dtype = np.dtype([
    ('id', np.int32),
    ('strength', np.int32),
    ('energy', np.int32),
    ('speed', np.int32),
    ('pos', np.int32, (2,)),
    ('status', np.int8),
    ('type', np.int8)
])

class Robot:
    def __init__(self, idx, shm_name_robots, shm_name_grid, linhas, colunas, robots_mutex, game_over_flag):
        self.idx = idx
        self.linhas = linhas
        self.colunas = colunas

        self.game_over_flag = game_over_flag
        self.robots_mutex = robots_mutex

        self.shm_robots = shared_memory.SharedMemory(name=shm_name_robots)
        self.shm_grid = shared_memory.SharedMemory(name=shm_name_grid)

        self.robots = np.ndarray((4,), dtype=robot_dtype, buffer=self.shm_robots.buf)
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

    def sense_act(self):
        # Implementação do thread sense_act
        pass

    def housekeeping(self):
        while self.status != "morto" and self.game_over_flag.value == 0:
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