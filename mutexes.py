from multiprocessing import Lock

global shared_variable
class Mutexes():
    def __init__(self):
        self.grid_mutex = Lock()
        self.robots_mutex = Lock()
        self.battery_mutex_array = {}
        for battery_position in shared_variable.batteryPositions:
            key = str(battery_position[0]+battery_position[1]) 
            self.battery_mutex_array[key] = Lock() 
        
        