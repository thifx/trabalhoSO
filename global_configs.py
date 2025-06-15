import numpy as np
import logging

logger = logging.getLogger("game_logger")
logger.setLevel(logging.DEBUG)
if not logger.hasHandlers():
    handler = logging.FileHandler("game_result.log", mode='w')
    formatter = logging.Formatter(
        ' %(module)s:%(lineno)d - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

tabuleiro_linhas, tabuleiro_colunas = 40, 20
tabuleiro = np.zeros((tabuleiro_linhas,tabuleiro_colunas), dtype=np.int8)
tabuleiro_dtype = np.int8
num_robots = 4
robot_dtype = np.dtype([
        ('id', np.int32),
        ('strength', np.int32),
        ('energy', np.int32),
        ('speed', np.int32),
        ('pos', np.int32, (2,)),
        ('status', np.int8),
        ('type', np.int8)
])