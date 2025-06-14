import pygame
import numpy as np

largura_bloco = 20
altura_bloco = 20

CORES = {
    0: (255, 255, 255),  # livre - branco
    1: (0, 0, 0),        # barreira - preto
    2: (255, 255, 0),    # bateria - amarelo
    99: (0, 255, 0),      # robô jogador - verde
    10: (255, 0, 0),     # robô comum - vermelho
}

def cor_por_valor(valor):
    CORES.get(valor, (100, 100, 100)) 

def viewer(linhas, colunas, shm):
    tabuleiro_shm = np.ndarray((linhas, colunas), dtype=np.int8, buffer=shm.buf)

    pygame.init()
    screen = pygame.display.set_mode((colunas * largura_bloco, linhas * altura_bloco))
    pygame.display.set_caption("Visualização do Tabuleiro")

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                shm.close()
                break

        screen.fill((200, 200, 200))
        for i in range(linhas):
            for j in range(colunas):
                valor = tabuleiro_shm[i, j]
                cor = cor_por_valor(valor)
                pygame.draw.rect(screen, cor,
                    (j * largura_bloco, i * altura_bloco, largura_bloco, altura_bloco))
        
        for i in range(linhas + 1):
            pygame.draw.line(screen, (0, 0, 0), (0, i * altura_bloco), (colunas * largura_bloco, i * altura_bloco))
        for j in range(colunas + 1):
            pygame.draw.line(screen, (0, 0, 0), (j * largura_bloco, 0), (j * largura_bloco, linhas * altura_bloco))

        pygame.display.flip()
        clock.tick(10)
    