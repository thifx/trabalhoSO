import numpy as np
import logging

#Logger configs
logger = logging.getLogger("game_logger")
logger.setLevel(logging.DEBUG)
if not logger.hasHandlers():
    handler = logging.FileHandler("game_result.log", mode='w')
    formatter = logging.Formatter(
        ' %(module)s:%(lineno)d - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

#Global variables used in the game
linhas, colunas = 40, 20
num_robots = 30
tabuleiro_dtype = np.int8
tabuleiro = np.zeros((linhas,colunas), dtype=tabuleiro_dtype)
robot_dtype = np.dtype([
        ('id', np.int32),
        ('strength', np.int32),
        ('energy', np.int32),
        ('speed', np.int32),
        ('pos', np.int32, (2,)),
        ('status', np.int8),
        ('type', np.int8)
])