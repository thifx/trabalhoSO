from multiprocessing import shared_memory, Process
import numpy as np
from multiprocessing import Lock, shared_memory
from auxiliar import spawn_valores_aleatorios
from visualizador_pygame import viewer
from robot import Robot
from random import randint

#Configurações do jogo
linhas, colunas = 40, 20

def create_grid():

    tabuleiro = np.zeros((linhas, colunas), dtype=np.int8)

    spawn_valores_aleatorios(tabuleiro, 40, 2) 
    tabuleiro[15, 15] = 10   
    tabuleiro[20, 10] = 99   

    shm = shared_memory.SharedMemory(name="tabuleiro", create=True, size=tabuleiro.nbytes)
    tabuleiro_shm = np.ndarray(tabuleiro.shape, dtype=tabuleiro.dtype, buffer=shm.buf)
    tabuleiro_shm[:] = tabuleiro[:]
    return shm

def spawn_robots(num_robots):
    robot_dtype = np.dtype([
        ('id', np.int32),
        ('strength', np.int32),
        ('energy', np.int32),
        ('speed', np.int32),
        ('pos', np.int32, (2,)),
        ('status', np.int8)
    ])

    robots_shm = shared_memory.SharedMemory(name="robots", create=True, size=robot_dtype.itemsize * num_robots)
    robots = np.ndarray((num_robots,), dtype=robot_dtype, buffer=robots_shm.buf)
    for _ in range(num_robots):
        p = Process(target=Robot(randint(1, 10), randint(10, 100), randint(1, 5), status="vivo"))
        p.start()
        np.append(robots, p)
    return robots_shm

if __name__ == "__main__":
    grid_shm = create_grid()
    robots_shm = spawn_robots(4) 
    try:
        viewer(linhas, colunas, grid_shm)
    except KeyboardInterrupt:
        grid_shm.close()
        grid_shm.unlink()
        robots_shm.close()
        robots_shm.unlink()
