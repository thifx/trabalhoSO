import numpy as np
import os
from multiprocessing import Lock, shared_memory,Value,Manager,Process
from auxiliar import spawn_valores_aleatorios,inicializar_locks
from visualizador_pygame import viewer
from RoboPlayer import RoboPlayer

def iniciar_robo_jogador(shm, linhas, colunas, robos_array, grid_mutex, baterias_dict_mutex, robos_dict_mutex):
    id_robo = os.getpid()
    robo_jogador = RoboPlayer(id=99,posicao=[20, 10], forca=10, velocidade=5)
     
    grid_mutex.acquire()
    tabuleiro_shm = np.ndarray((linhas, colunas), dtype=np.int8, buffer=shm.buf)
    tabuleiro_shm[robo_jogador.posicao[0], robo_jogador.posicao[1]] = robo_jogador.id
    grid_mutex.release()
    
    robos_array.append(robo_jogador) # Adiciona o robô ao array compartilhado
    robo_jogador.controlador_robo(shm, linhas, colunas) # Inicia o controlador do robô jogador
    
#Configurações do jogo
linhas, colunas = 40, 20

def create_grid():

    #cria array de zeros com a quantidade de linhas e colunas
    tabuleiro = np.zeros((linhas, colunas), dtype=np.int8)

    #definindo localização dos objetos
    spawn_valores_aleatorios(tabuleiro, 80, 1) #barreiras
    global posicoes_baterias
    posicoes_baterias = spawn_valores_aleatorios(tabuleiro, 40, 2) #energia
    tabuleiro[15, 15] = 10   # robô comum
    tabuleiro[20, 10] = 99   # robô jogador

    #cria um bloco de memória compartilhada definindo o tamanho como o tamanho de bytes do tabuleiro
    shm = shared_memory.SharedMemory(name="tabuleiro", create=True, size=tabuleiro.nbytes)
    #interpreta o bloco de memória compartilhada como um array numpy com o shape (linhas, colunas) e tipo do array tabuleiro
    tabuleiro_shm = np.ndarray(tabuleiro.shape, dtype=tabuleiro.dtype, buffer=shm.buf)

    #o tabuleiro com memoria compartilhada foi criado, mas com os 
    tabuleiro_shm[:] = tabuleiro[:]
    return shm

if __name__ == "__main__":
    #Variaveis compartilhadas
    manager = Manager() #Controla o ciclo de vida das variaveis compartilhadas
    posicoes_baterias = [] # Lista preenchida na funcao create_grid
    shm = create_grid()
    robos_array = manager.list()
    jogo_finalizado = manager.Value('b', False)
    
    #Inicialização dos mutexes 
    grid_mutex = manager.Lock()
    baterias_dict_mutex,robos_dict_mutex = inicializar_locks(manager, posicoes_baterias, robos_array)
    try:
        viewer(linhas, colunas, shm)
        # Inicia o robô jogador
        robo_jogador = Process(target=iniciar_robo_jogador, args=(shm, linhas, colunas, robos_array, grid_mutex, baterias_dict_mutex, robos_dict_mutex))
        robo_jogador.start()
        robo_jogador.join()
    except KeyboardInterrupt:
        shm.close()
        shm.unlink()
        manager.shutdown()
