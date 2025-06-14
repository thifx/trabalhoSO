from multiprocessing import Lock, shared_memory
import numpy as np
from auxiliar import spawn_valores_aleatorios
from visualizador_pygame import viewer

linhas, colunas = 40, 20
Lock = Lock()

def create_grid():

    #cria array de zeros com a quantidade de linhas e colunas
    tabuleiro = np.zeros((linhas, colunas), dtype=np.int8)

    #definindo localização dos objetos
    spawn_valores_aleatorios(tabuleiro, 80, 1) #barreiras
    spawn_valores_aleatorios(tabuleiro, 40, 2) #energia
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
    shm = create_grid()
    try:
        viewer(linhas, colunas, shm)
    except KeyboardInterrupt:
        shm.close()
        shm.unlink()
