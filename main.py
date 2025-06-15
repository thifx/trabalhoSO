from multiprocessing import shared_memory, Process
import numpy as np
from multiprocessing import Lock, shared_memory
from auxiliar import spawn_valores_aleatorios
from visualizador_pygame import viewer
from robot import Robot
from random import randint
from game import Game


if __name__ == "__main__":
    Game()