from multiprocessing import shared_memory
from global_configs import *
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

def viewer(linhas, colunas, grid_shm, robots_shm,grid_mutex, game_over_flag,robots_mutex):
    pygame.init()
    screen = pygame.display.set_mode((colunas * largura_bloco, linhas * altura_bloco))
    pygame.display.set_caption("Visualização do Tabuleiro")

    clock = pygame.time.Clock()
    rodando = True
    while rodando:
        tabuleiro_shm = np.ndarray((linhas, colunas), dtype=np.int8, buffer=grid_shm.buf)
        robots = np.ndarray((num_robots,), dtype=robot_dtype, buffer=robots_shm.buf)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False
            idx = np.where(robots['type'] == 99)[0][0]
            player = robots[idx]
            if event.type == pygame.KEYDOWN and robots[idx]['status'] != 0 and game_over_flag.value == 0:
                x, y = player['pos'][1], player['pos'][0]
                novo_y, novo_x = y, x
                if event.key == pygame.K_UP:
                    novo_y = max(0, y - 1)
                elif event.key == pygame.K_DOWN:
                    novo_y = min(linhas - 1, y + 1)
                elif event.key == pygame.K_LEFT:
                    novo_x = max(0, x - 1)
                elif event.key == pygame.K_RIGHT:
                    novo_x = min(colunas - 1, x + 1)
                if tabuleiro_shm[novo_y, novo_x] != 1:
                    valor_destino = tabuleiro_shm[novo_y, novo_x]
                    status_array = robots['status']
                    vivos = np.where(status_array == 1)[0]

                    #Logica  
                    with grid_mutex:    
                        tabuleiro_shm[y, x] = 0
                        tabuleiro_shm[novo_y, novo_x] = 99
                        player['pos'][0] = novo_y
                        player['pos'][1] = novo_x

                        print(f'[PLAYER] Movimentou para o bloco ({novo_y}, {novo_x})')
                        logger.info(f'[PLAYER] Movimentou para o bloco ({novo_y}, {novo_x})')
                        robots[idx]['energy'] = max(0, robots[idx]['energy'] - 1)
                        if(valor_destino == 2):
                            robots[idx]['energy'] = 100
                            print(f'[PLAYER] Acessou um bloco de energia')
                            logger.info(f'[PLAYER] Acessou um bloco de energia')
                        
                        if(valor_destino == 10):
                            print(f'[PLAYER] Encontrou um robô comum no bloco ({novo_y}, {novo_x})')
                            logger.info(f'[PLAYER] Encontrou um robô comum no bloco ({novo_y}, {novo_x})')
                            with robots_mutex:
                                robo_comum_idx = np.where(robots['pos'] == (novo_y, novo_x))[0]
                                if robo_comum_idx.size > 0:
                                    robo_comum_idx = robo_comum_idx[0]
                                    robo_comum = robots[robo_comum_idx]
                                    if robo_comum['status'] == 1:
                                        minha_forca = 2 * robots[idx]['strength'] + robots[idx]['energy']
                                        robo_inimigo_forca = 2 * robo_comum['strength'] + robo_comum['energy']
                                        if robo_inimigo_forca < minha_forca:
                                            print(f'[PLAYER] Derrotou o robô {robo_comum["id"]}')
                                            robots[robo_comum_idx]['status'] = 0
                                            robots[robo_comum_idx]['pos'] = (-1, -1)
                                        elif robo_inimigo_forca > minha_forca:
                                            print(f'[PLAYER] Foi derrotado pelo robô {robo_comum["id"]}')
                                            robots[idx]['status'] = 0
                                            robots[idx]['pos'] = (-1, -1)
                                            tabuleiro_shm[novo_y, novo_x] = 10
                                        else:
                                            print(f'[PLAYER] Empate com o robô {robo_comum["id"]}')
                                            robots[robo_comum_idx]['status'] = 0
                                            robots[robo_comum_idx]['pos'] = (-1, -1)
                                            tabuleiro_shm[novo_y, novo_x] = 0
                                            robots[idx]['status'] = 0
                                            robots[idx]['pos'] = (-1, -1)
                            
                        if(robots[idx]['energy'] == 0):
                            print('[PLAYER] morreu por falta de energia')
                            logger.info('[PLAYER] morreu por falta de energia')
                            robots[idx]['status'] = 0
                            tabuleiro_shm[novo_y, novo_x] = 0

                        if len(vivos) == 1 and vivos[0] == idx:
                            print("[PLAYER] É o único vivo! VITÓRIA!")
                            logger.info("[PLAYER] É o único vivo! VITÓRIA!")
                            game_over_flag.value = 1

        screen.fill((200, 200, 200))
        for i in range(linhas):
            for j in range(colunas):
                valor = tabuleiro_shm[i, j]
                if valor==10 or valor==99:
                    robots = np.ndarray((num_robots,), dtype=robot_dtype, buffer=robots_shm.buf)
                    for robo in robots:
                        if robo['pos'][0] == i and robo['pos'][1] == j and robo['status'] == 0:
                            continue
                            
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
    