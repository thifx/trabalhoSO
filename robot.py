import os
import threading
import math



class Robot:
    def __init__(self, strength, energy, speed, status):
        self.strength = strength
        self.energy = energy
        self.speed = speed
        self.status = status
    def __call__(self):
        self.run()

    def distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def run(self):
        self.robot_id = os.getpid()
        print(f"Robot {self.robot_id} started with strength {self.strength}, energy {self.energy}, speed {self.speed}, status {self.status}")
        thread1 = threading.Thread(target=self.sense_act, name="sense_act")
        thread2 = threading.Thread(target=self.housekeeping, name="housekeeping")

        thread1.start()
        thread2.start()

    def collect_battery(self):

        self.robots_mutex.acquire()
        try:
            if self.energy < 100:
                self.energy = min(100, self.energy + 20)
                self.robots[self.idx]['energy'] = self.energy
            if self.pos in self.baterias_dict_mutex:
                self.baterias_dict_mutex.pop(self.pos, None)
        finally:
            self.robots_mutex.release()
        
        grid = np.ndarray((self.linhas, self.colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)
        self.grid_mutex.acquire()
        try:
            x, y = self.pos
            if grid[x, y] == 2:
                grid[x, y] = 10
        finally:
            self.grid_mutex.release()


    def fight(self):
        robot_list = self.robots
        for robot in robot_list:
            if tuple(robot['pos']) == self.pos and robot['id'] != self.id:
                power_1 = 2 * self.strength + self.energy
                power_2 = 2 * robot['strength'] + robot['energy']
                if power_1 == power_2:
                    self.status = 0
                    robot['status'] = 0

                    grid = np.ndarray((tabuleiro_linhas, tabuleiro_colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)
                    self.grid_mutex.acquire()
                    try:
                        x, y = self.pos
                        grid[x, y] = 0
                    finally:
                        self.grid_mutex.release()

                elif power_1 > power_2:
                    robot['status'] = 0

                    grid = np.ndarray((tabuleiro_linhas, tabuleiro_colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)
                    self.grid_mutex.acquire()
                    try:
                        x, y = robot['pos']
                        grid[x, y] = 0
                    finally:
                        self.grid_mutex.release()
                
                else:
                    self.status = 0

                    grid = np.ndarray((tabuleiro_linhas, tabuleiro_colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)
                    self.grid_mutex.acquire()
                    try:
                        x, y = self.pos
                        grid[x, y] = 0
                    finally:
                        self.grid_mutex.release()
                break



    def move(self, pos_x, pos_y):
        
        grid = np.ndarray((tabuleiro_linhas, tabuleiro_colunas), dtype=tabuleiro_dtype, buffer=self.shm_grid.buf)

        my_x, my_y = self.pos 
        dx = pos_x - my_x
        dy = pos_y - my_y
        step_x = int(np.sign(dx))
        step_y = int(np.sign(dy))
        new_x = my_x + step_x
        new_y = my_y + step_y

        target = self.valid_move(new_x, new_y, grid)
        if target is not None:
            try:
                self.grid_mutex.acquire()
                grid[my_x, my_y] = 0
                grid[new_x, new_y] = 99
                self.pos = (new_x, new_y)
            finally:
                self.grid_mutex.release()
            
            if target == 2:
                key = f"{new_x}{new_y}"
                mutex = self.baterias_dict_mutex.get((key), None)
                if mutex:
                    mutex.acquire()
                    try:
                        self.collect_battery()
                    finally:
                        mutex.release()
            elif target == 10 or target == 99:
                try:
                    self.robot_mutex.acquire()
                    self.fight()
                finally:
                    self.robot_mutex.release()


    def valid_move(pos_x, pos_y, grid):

        linhas = tabuleiro_linhas
        colunas = tabuleiro_colunas

        if pos_x < 0 or pos_x >= linhas or pos_y < 0 or pos_y >= colunas:
            return False
    
        valor_do_tabuleiro = grid[pos_x, pos_y]

        if valor_do_tabuleiro == 1:
            return None
        return valor_do_tabuleiro


    def sense_act(self):

        local_grid = self.grid.copy()

        battery_pos = np.argwhere(local_grid == 2)
        enemy_pos = np.argwhere(local_grid == 10)

        my_pos = self.pos  

        minor_e_dist = 1000000.0
        enemy_selected = (0, 0)

        minor_b_dist = 1000000.0
        battery_selected = (0, 0)

        for enemy in enemy_pos:
            d = self.distance(my_pos[0], my_pos[1], enemy[0], enemy[1])
            if d < minor_e_dist:
                minor_e_dist = d
                enemy_selected = (enemy[0], enemy[1])
    
        for battery in battery_pos:
            d_ = self.distance(my_pos[0], my_pos[1], battery[0], battery[1])
            if d_ < minor_b_dist:
                minor_b_dist = d_
                battery_selected = (battery[0], battery[1])

        if self.energy < 35:
            self.grid_mutex.acquire()
            self.move(battery_selected)
            self.grid_mutex.release()
    
        else:
            self.grid_mutex.acquire()
            if minor_e_dist < minor_b_dist:
                self.move(enemy_selected)
            else:
                self.move(battery_selected)
            self.grid_mutex.release()

        
    def housekeeping(self):
        # Implementação do thread housekeeping
        pass