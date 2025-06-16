import numpy as np
from global_configs import *

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
    tabuleiro = np.ndarray((linhas, colunas), dtype=tabuleiro_dtype, buffer=grid_shm.buf)
    posicoes_baterias = np.argwhere(tabuleiro == 2)
    baterias_dict_mutex = manager.dict()

    for posicao_bateria in posicoes_baterias:
        key = f"{posicao_bateria[0]}{posicao_bateria[1]}"
        baterias_dict_mutex[key] = manager.Lock()

    return baterias_dict_mutex