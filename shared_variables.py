from multiprocessing import Queue

class SharedVariables():
    def __init__(self,grid,robots_array,battery_positions,barrier_positions,finished=False):
        self.grid = grid
        self.robotsArray = robots_array
        self.batteryPositions = battery_positions
        self.barrierPositions = barrier_positions
        self.isFinished = finished
        