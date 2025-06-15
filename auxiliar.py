import numpy as np
from global_configs import tabuleiro_linhas, tabuleiro_colunas, robot_dtype,tabuleiro_dtype,num_robots

def spawn_valores_aleatorios(tabuleiro: np.ndarray, quantidade: int, valor: int):
    posicoes_geradas = []
    livres = np.argwhere(tabuleiro == 0)
    if quantidade > len(livres):
        raise ValueError("Quantidade maior que espaços livres disponíveis no tabuleiro.")
    
    escolhas = livres[np.random.choice(len(livres), quantidade, replace=False)]
    for pos in escolhas:
        tabuleiro[pos[0], pos[1]] = valor
        posicoes_geradas.append((pos[0], pos[1]))
    
    return posicoes_geradas

def inicializar_locks(manager,grid_shm):
    """
    Os mutexes são usados para controlar o acesso concorrente às baterias.
    o mutex de cada bateria eh acessado com a chave "x,y" onde x e y são as coordenadas da bateria
    """
    tabuleiro = np.ndarray((tabuleiro_linhas, tabuleiro_colunas), dtype=tabuleiro_dtype, buffer=grid_shm.buf)
    posicoes_baterias = np.argwhere(tabuleiro == 2)
    baterias_dict_mutex = manager.dict()

    for posicao_bateria in posicoes_baterias:
        key = f"{posicao_bateria[0]}{posicao_bateria[1]}"
        baterias_dict_mutex[key] = manager.Lock()

    return baterias_dict_mutex

def verificar_posicao_valida(posicao,tabuleiro)->bool:
    linhas = 40
    colunas = 20
    pos_x = posicao[0]
    pos_y = posicao[1]
    #Verifica se a posicao esta dentro dos limites do tabuleiro
    if pos_x < 0 or pos_x >= linhas or pos_y < 0 or pos_y >= colunas:
        return False
    
    valor_do_tabuleiro = tabuleiro[pos_x, pos_y]
    #Verifica se o valor do tabuleiro na posicao eh valido
    if(valor_do_tabuleiro == 0): # Espaco livre
        return True
    elif(valor_do_tabuleiro == 1): #Barreira
        return False
    else: #Bateria ou robô
        return True
    
def realizar_acao_player(robo,tabuleiro,nova_posicao,baterias_dict_mutex):
    valor_tabuleiro = tabuleiro[nova_posicao[0], nova_posicao[1]]
    if valor_tabuleiro == 0:  # Espaço livre
        tabuleiro[robo.posicao[0], robo.posicao[1]] = 0  # Limpa a posição antiga
        robo.posicao = nova_posicao
        tabuleiro[nova_posicao[0], nova_posicao[1]] = robo.id  # Atualiza a nova posição do robô
    elif valor_tabuleiro == 2:  # Bateria
        pass  # Implementar lógica de coleta de bateria e organizacao dos mutex
    elif valor_tabuleiro == 99:  # Robô jogador
        pass  # Implementar lógica de interação entre robos
