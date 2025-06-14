import pygame
import numpy as np
from multiprocessing import Lock, shared_memory,Value,Manager
from auxiliar import verificar_posicao_valida,realizar_acao_player

class RoboPlayer():    
    def __init__(self, id, posicao,forca,velocidade):
        self.status = 1 # 1 = vivo, 0 = inativo
        self.energia = 100
        self.posicao = posicao
        self.id = id
        self.velocidade = velocidade
        self.forca = forca
        poder = 2* self.forca * self.velocidade
    
    def controlador_robo(self, shm, linhas, colunas, grid_mutex, baterias_dict_mutex):        
        # Configuração do Pygame
        global robos_array, robos_dict_mutex
        running = True
        while running:
            pygame.init()
            pygame.display.set_mode((200, 200))
            clock = pygame.time.Clock()

            #Tratamento de eventos 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Captura estado contínuo do teclado
            keys = pygame.key.get_pressed()
            
            # Calcula nova posição
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                nova_posicao = (self.posicao[0]-1,self.posicao[1])
                #Modificar o tabuleiro compartilhado
                grid_mutex.acquire()
                tabuleiro_shm = np.ndarray((linhas, colunas), dtype=np.int8, buffer=shm.buf)
                if(verificar_posicao_valida(nova_posicao, tabuleiro_shm)):
                    realizar_acao_player(robo=self,tabuleiro=tabuleiro_shm,nova_posicao=nova_posicao, baterias_dict_mutex=baterias_dict_mutex)
                grid_mutex.release()
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                nova_posicao = (self.posicao[0]+1,self.posicao[1])
                #Modificar o tabuleiro compartilhado
                grid_mutex.acquire()
                tabuleiro_shm = np.ndarray((linhas, colunas), dtype=np.int8, buffer=shm.buf)
                if(verificar_posicao_valida(nova_posicao, tabuleiro_shm)):
                    realizar_acao_player(robo=self,tabuleiro=tabuleiro_shm,nova_posicao=nova_posicao, baterias_dict_mutex=baterias_dict_mutex)
                grid_mutex.release()
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                nova_posicao = (self.posicao[0],self.posicao[1]-1)
                #Modificar o tabuleiro compartilhado
                grid_mutex.acquire()
                tabuleiro_shm = np.ndarray((linhas, colunas), dtype=np.int8, buffer=shm.buf)
                if(verificar_posicao_valida(nova_posicao, tabuleiro_shm)):
                    realizar_acao_player(robo=self,tabuleiro=tabuleiro_shm,nova_posicao=nova_posicao, baterias_dict_mutex=baterias_dict_mutex)
                grid_mutex.release()
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                nova_posicao = (self.posicao[0],self.posicao[1]+1)
                #Modificar o tabuleiro compartilhado
                grid_mutex.acquire()
                tabuleiro_shm = np.ndarray((linhas, colunas), dtype=np.int8, buffer=shm.buf)
                if(verificar_posicao_valida(nova_posicao, tabuleiro_shm)):
                    realizar_acao_player(robo=self,tabuleiro=tabuleiro_shm,nova_posicao=nova_posicao, baterias_dict_mutex=baterias_dict_mutex)
                grid_mutex.release()
            clock.tick(20)
        pygame.quit()    
        