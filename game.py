from multiprocessing import Lock, shared_memory, Process
import numpy as np
from random import randint
from robot import Robot
from auxiliar import spawn_valores_aleatorios
from visualizador_pygame import viewer

class Game:
    def __init__(self, linhas=40, colunas=20, num_robots=4):
        self.linhas = linhas
        self.colunas = colunas
        self.num_robots = num_robots

        self.grid_lock = Lock()
        self.robots_lock = Lock()

        self.grid_shm = None
        self.robots_shm = None
        self.robot_processes = []

    def create_grid(self):
        tabuleiro = np.zeros((self.linhas, self.colunas), dtype=np.int8)
        spawn_valores_aleatorios(tabuleiro, 40, 2)
        tabuleiro[15, 15] = 10
        tabuleiro[20, 10] = 99

        shm = shared_memory.SharedMemory(name="tabuleiro", create=True, size=tabuleiro.nbytes)
        tabuleiro_shm = np.ndarray(tabuleiro.shape, dtype=tabuleiro.dtype, buffer=shm.buf)
        tabuleiro_shm[:] = tabuleiro[:]
        self.grid_shm = shm

    def spawn_robots(self):
        robot_dtype = np.dtype([
        ('id', np.int32),
        ('strength', np.int32),
        ('energy', np.int32),
        ('speed', np.int32),
        ('pos', np.int32, (2,)),
        ('status', np.int8)
        ])

        robots_shm = shared_memory.SharedMemory(name="robots", create=True, size=robot_dtype.itemsize * self.num_robots)
        robots = np.ndarray((self.num_robots,), dtype=robot_dtype, buffer=robots_shm.buf)
        for _ in range(self.num_robots):
            p = Process(target=Robot(randint(1, 10), randint(10, 100), randint(1, 5), status="vivo"))
            p.start()
            np.append(robots, p)
            self.robot_processes.append(p)

        self.robots_shm = robots_shm

    def start(self):
        self.create_grid()
        self.spawn_robots()
        viewer(self.linhas, self.colunas, self.grid_shm)

    def cleanup(self):
        if self.grid_shm:
            self.grid_shm.close()
            self.grid_shm.unlink()
        if self.robots_shm:
            self.robots_shm.close()
            self.robots_shm.unlink()
        for p in self.robot_processes:
            p.terminate()
            p.join()