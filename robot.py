from multiprocessing import shared_memory
import os
import threading
import numpy as np

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
    def __init__(self, idx, shm_name_robots, shm_name_grid, linhas, colunas):
        self.idx = idx
        self.linhas = linhas
        self.colunas = colunas

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
        # Implementação do thread housekeeping
        pass