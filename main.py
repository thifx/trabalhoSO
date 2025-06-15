import numpy as np
from multiprocessing import shared_memory, Process, Manager
from multiprocessing import Lock, shared_memory
from auxiliar import spawn_valores_aleatorios,inicializar_locks
from visualizador_pygame import viewer
from robot import Robot
from random import randint

#Configurações do jogo
linhas, colunas = 40, 20

def create_grid(num_robots=4):

    tabuleiro = np.zeros((linhas, colunas), dtype=np.int8)

    spawn_valores_aleatorios(tabuleiro, 80, 1) # Gera 80 barreiras
    global posicoes_baterias 
    posicoes_baterias = spawn_valores_aleatorios(tabuleiro, 40, 2) # Gera 40 energias
    spawn_valores_aleatorios(tabuleiro, num_robots - 1, 10) # Gera n - 1 robôs
    spawn_valores_aleatorios(tabuleiro, 1, 99) # Gera o robô principal 

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
    posicoes_baterias = []
    manager = Manager() 
    grid_shm = create_grid()
    robots_shm = spawn_robots(4)
    baterias_dict_mutex,robos_dict_mutex = inicializar_locks(manager, posicoes_baterias, robots_shm,num_robots=4)
    try:
        viewer(linhas, colunas, grid_shm)
    except KeyboardInterrupt:
        grid_shm.close()
        grid_shm.unlink()
        robots_shm.close()
        robots_shm.unlink()
