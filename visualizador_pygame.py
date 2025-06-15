from multiprocessing import shared_memory
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

robot_dtype = np.dtype([
        ('id', np.int32),
        ('strength', np.int32),
        ('energy', np.int32),
        ('speed', np.int32),
        ('pos', np.int32, (2,)),
        ('status', np.int8),
        ('type', np.int8)
    ])

def viewer(linhas, colunas, grid_shm, robots_shm):
    pygame.init()
    screen = pygame.display.set_mode((colunas * largura_bloco, linhas * altura_bloco))
    pygame.display.set_caption("Visualização do Tabuleiro")

    clock = pygame.time.Clock()
    rodando = True
    while rodando:
        tabuleiro_shm = np.ndarray((linhas, colunas), dtype=np.int8, buffer=grid_shm.buf)
        robots = np.ndarray((4,), dtype=robot_dtype, buffer=robots_shm.buf)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            if event.type == pygame.KEYDOWN:
                print(robots)
                player = [x for x in robots if x['type'] == 99][0]
                x, y = player['pos'][0], player['pos'][1]
                novo_x, novo_y = x, y
                if event.key == pygame.K_UP:
                    novo_y = max(0, y - 1)
                elif event.key == pygame.K_DOWN:
                    novo_y = min(linhas - 1, y + 1)
                elif event.key == pygame.K_LEFT:
                    novo_x = max(0, x - 1)
                elif event.key == pygame.K_RIGHT:
                    novo_x = min(colunas - 1, x + 1)
                print(player)
                if tabuleiro_shm[novo_y, novo_x] != 1:
                    tabuleiro_shm[y, x] = 0       
                    tabuleiro_shm[novo_y, novo_x] = 99
                    player['pos'][0] = novo_x
                    player['pos'][1] = novo_y
                    print(f"Moved to ({novo_x}, {novo_y})")
            # Checa shm se flag game_over === True

        screen.fill((200, 200, 200))
        for i in range(linhas):
            for j in range(colunas):
                valor = tabuleiro_shm[i, j]
                cor = CORES.get(valor, (100, 100, 100)) 
                pygame.draw.rect(screen, cor,
                    (j * largura_bloco, i * altura_bloco, largura_bloco, altura_bloco))
        
        for i in range(linhas + 1):
            pygame.draw.line(screen, (0, 0, 0), (0, i * altura_bloco), (colunas * largura_bloco, i * altura_bloco))
        for j in range(colunas + 1):
            pygame.draw.line(screen, (0, 0, 0), (j * largura_bloco, 0), (j * largura_bloco, linhas * altura_bloco))

        pygame.display.flip()
        clock.tick(10)
    pygame.quit()
    