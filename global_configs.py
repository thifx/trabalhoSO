import numpy as np

tabuleiro_linhas, tabuleiro_colunas = 40, 20
tabuleiro_dtype = np.int8
robot_dtype = np.dtype([
        ('id', np.int32),
        ('strength', np.int32),
        ('energy', np.int32),
        ('speed', np.int32),
        ('pos', np.int32, (2,)),
        ('status', np.int8),
        ('type', np.int8)
])
