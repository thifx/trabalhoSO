from multiprocessing import shared_memory, Process, Value
import numpy as np
from multiprocessing import shared_memory, Process, Manager
from multiprocessing import Lock, shared_memory
from auxiliar import spawn_valores_aleatorios,inicializar_locks
from visualizador_pygame import viewer
from robot import Robot
from random import randint
import time

linhas, colunas = 40, 20

grid_mutex = Lock()
robots_mutex = Lock()

game_over_flag = Value('i', 0)

robot_dtype = np.dtype([
        ('id', np.int32),
        ('strength', np.int32),
        ('energy', np.int32),
        ('speed', np.int32),
        ('pos', np.int32, (2,)),
        ('status', np.int8)
    ])

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
    robots_shm = shared_memory.SharedMemory(name="robots", create=True, size=robot_dtype.itemsize * num_robots)
    robots = np.ndarray((num_robots,), dtype=robot_dtype, buffer=robots_shm.buf)


    processes = []

    for i in range(num_robots):
        strength = randint(1, 10)
        energy = randint(10, 100)
        speed = randint(1, 5)
        pos = (randint(0, linhas - 1), randint(0, colunas - 1))

        robots[i] = (i, strength, energy, speed, pos, 1)

        p = Process(target=Robot(strength, energy, speed, "vivo", i, "robots", robots_mutex, game_over_flag))
        p.start()
        processes.append(p)

    return robots_shm, processes

if __name__ == "__main__":
    posicoes_baterias = []
    manager = Manager() 
    grid_shm = create_grid()
    robots_shm, processos = spawn_robots(4)
    baterias_dict_mutex,robos_dict_mutex = inicializar_locks(manager, posicoes_baterias, robots_shm,num_robots=4)
    try:
        viewer(linhas, colunas, grid_shm)

        while game_over_flag.value == 0:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Encerrando o jogo manualmente")
    finally:
        grid_shm.close()
        grid_shm.unlink()
        robots_shm.close()
        robots_shm.unlink()

        for p in processos:
            p.terminate()
