import pygame
import numpy as np
from multiprocessing import shared_memory, Lock
import time

linhas, colunas = 40, 20
largura_bloco = 20
altura_bloco = 20

CORES = {
    0: (255, 255, 255),  # livre - branco
    1: (0, 0, 0),        # barreira - preto
    2: (255, 255, 0),    # bateria - amarelo
}

def cor_por_valor(valor):
    if valor in CORES:
        return CORES[valor]
    elif valor == 99:
        return (0, 255, 0)      # robô jogador - verde
    elif valor >= 10:
        return (255, 0, 0)      # outros robôs - vermelho
    return (100, 100, 100)      # valor desconhecido - cinza

def main():
    #acessando o tabuleiro que existe na memória compartilhada
    shm = shared_memory.SharedMemory(name='tabuleiro', create=False)
    tabuleiro_shm = np.ndarray((linhas, colunas), dtype=np.int8, buffer=shm.buf)

    pygame.init()
    screen = pygame.display.set_mode((colunas * largura_bloco, linhas * altura_bloco))
    pygame.display.set_caption("Visualização do Tabuleiro")

    clock = pygame.time.Clock()
    rodando = True

    while rodando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        # Atualiza o desenho do tabuleiro
        screen.fill((200, 200, 200))
        for i in range(linhas):
            for j in range(colunas):
                valor = tabuleiro_shm[i, j]
                cor = cor_por_valor(valor)
                pygame.draw.rect(screen, cor,
                    (j * largura_bloco, i * altura_bloco, largura_bloco, altura_bloco))
        
        # Atualiza o desenho do tabuleiro
        screen.fill((200, 200, 200))
        for i in range(linhas):
            for j in range(colunas):
                valor = tabuleiro_shm[i, j]
                cor = cor_por_valor(valor)
                pygame.draw.rect(screen, cor,
                    (j * largura_bloco, i * altura_bloco, largura_bloco, altura_bloco))
        
        # Desenha as linhas da grade por cima dos blocos
        for i in range(linhas + 1):
            pygame.draw.line(screen, (0, 0, 0), (0, i * altura_bloco), (colunas * largura_bloco, i * altura_bloco))
        for j in range(colunas + 1):
            pygame.draw.line(screen, (0, 0, 0), (j * largura_bloco, 0), (j * largura_bloco, linhas * altura_bloco))

        pygame.display.flip()
        clock.tick(10)
    pygame.quit()
    shm.close()

if __name__ == "__main__":
    main()