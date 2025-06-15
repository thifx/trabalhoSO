from multiprocessing import shared_memory, Process, Value
from multiprocessing import shared_memory, Process, Manager
from multiprocessing import Lock, shared_memory
from auxiliar import spawn_valores_aleatorios,inicializar_locks
from visualizador_pygame import viewer
from robot import Robot
from random import randint
import numpy as np
import time

#Configurações globais
processos = []
linhas, colunas = 40, 20
tabuleiro = np.zeros((linhas, colunas), dtype=np.int8)
robot_dtype = np.dtype([
        ('id', np.int32),
        ('strength', np.int32),
        ('energy', np.int32),
        ('speed', np.int32),
        ('pos', np.int32, (2,)),
        ('status', np.int8),
        ('type', np.int8)
])

#Mutexes e variaveis compartilhadas
manager = Manager()
baterias_dict_mutex,robos_dict_mutex = manager.dict(), manager.dict()
grid_mutex = Lock()
robots_mutex = Lock()
game_over_flag = Value('i', 0)

def create_grid(num_robots=4):
    grid_shm = shared_memory.SharedMemory(name="tabuleiro", create=True, size=tabuleiro.nbytes)
    tabuleiro_shm = np.ndarray(tabuleiro.shape, dtype=tabuleiro.dtype, buffer=grid_shm.buf)
    spawn_valores_aleatorios(tabuleiro, 80, 1) # Gera 80 barreiras 
    spawn_valores_aleatorios(tabuleiro, 40, 2) # Gera 40 energias
    spawn_valores_aleatorios(tabuleiro, num_robots - 1, 10) # Gera n - 1 robôs
    spawn_valores_aleatorios(tabuleiro, 1, 99) # Gera o robô principal
    tabuleiro_shm[:] = tabuleiro[:]
    return grid_shm

def spawn_robots(num_robots=4):
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
            p = Process(target=Robot(i, "robots", "tabuleiro", linhas, colunas, robots_mutex, game_over_flag))
            p.start()
            processos.append(p)

    return robots_shm

if __name__ == "__main__": 
    grid_shm = create_grid()
    robots_shm = spawn_robots()
    baterias_dict_mutex  = inicializar_locks(manager,grid_shm)
    try:
        viewer(linhas, colunas, grid_shm, robots_shm)
    except KeyboardInterrupt:
        pass
    finally:
        grid_shm.close()
        grid_shm.unlink()
        robots_shm.close()
        robots_shm.unlink()

        for p in processos:
            p.terminate()
