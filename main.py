from multiprocessing import shared_memory, Process, Value, Manager,Lock
from auxiliar import spawn_valores_aleatorios,inicializar_locks
from global_configs import *
from visualizador_pygame import viewer
from robot import Robot
from random import randint
import numpy as np
import time

#Configurações globais
processos = []

#Mutexes e variaveis compartilhadas
manager = Manager()
baterias_dict_mutex = manager.dict()
grid_mutex = Lock()
robots_mutex = Lock()
game_over_flag = Value('i', 0)

def create_grid(num_robots=num_robots):
    global baterias_dict_mutex
    
    grid_shm = shared_memory.SharedMemory(name="tabuleiro", create=True, size=tabuleiro.nbytes)
    tabuleiro_shm = np.ndarray(tabuleiro.shape, dtype=tabuleiro.dtype, buffer=grid_shm.buf)
    spawn_valores_aleatorios(tabuleiro, 80, 1) # Gera 80 barreiras 
    spawn_valores_aleatorios(tabuleiro, 40, 2) # Gera 40 energias
    spawn_valores_aleatorios(tabuleiro, num_robots - 1, 10) # Gera n - 1 robôs
    spawn_valores_aleatorios(tabuleiro, 1, 99) # Gera o robô principal
    tabuleiro_shm[:] = tabuleiro[:]
    baterias_dict_mutex  = inicializar_locks(manager,grid_shm)
    return grid_shm

def spawn_robots(num_robots=num_robots):
    grid_shm = shared_memory.SharedMemory(name="tabuleiro")
    tabuleiro_shm = np.ndarray((linhas, colunas), dtype=tabuleiro.dtype, buffer=grid_shm.buf)
    robots_shm = shared_memory.SharedMemory(name="robots", create=True, size=robot_dtype.itemsize * num_robots)
    robots = np.ndarray((num_robots,), dtype=robot_dtype, buffer=robots_shm.buf)
    
    posicoes_99 = np.argwhere(tabuleiro_shm == 99)
    posicoes_10 = np.argwhere(tabuleiro_shm == 10)

    for i in range(num_robots):
        strength = randint(1, 10)
        energy = randint(10, 100)
        speed = randint(1, 5)
        status = 1
        tipo = 99 if i == 0 else 10
        if tipo == 99:
            pos = posicoes_99[0]
        else:
            pos = posicoes_10[i - 1]
            
        robots[i]['id'] = i
        robots[i]['strength'] = strength
        robots[i]['energy'] = energy
        robots[i]['speed'] = speed
        robots[i]['status'] = status
        robots[i]['type'] = tipo
        robots[i]['pos'] = pos
        if tipo != 99:
            p = Process(target=Robot(i, "robots", "tabuleiro", robots_mutex,grid_mutex,baterias_dict_mutex, game_over_flag))
            p.start()
            processos.append(p)

    return robots_shm

if __name__ == "__main__": 
    grid_shm = create_grid()
    robots_shm = spawn_robots()
    try:
        logger.info("O jogo está inicialziando")
        viewer(linhas, colunas, grid_shm, robots_shm, grid_mutex, game_over_flag,robots_mutex)
    except KeyboardInterrupt:
        pass
    finally:
        grid_shm.close()
        grid_shm.unlink()
        robots_shm.close()
        robots_shm.unlink()

        for p in processos:
            p.terminate()
        logger.info("O jogo finalizou")
