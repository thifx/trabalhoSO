import numpy as np

def spawn_valores_aleatorios(tabuleiro: np.ndarray, quantidade: int, valor: int):
    livres = np.argwhere(tabuleiro == 0)
    if quantidade > len(livres):
        raise ValueError("Quantidade maior que espaços livres disponíveis no tabuleiro.")
    
    escolhas = livres[np.random.choice(len(livres), quantidade, replace=False)]
    for pos in escolhas:
        tabuleiro[pos[0], pos[1]] = valor
