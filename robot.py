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

    def move(self, pos_x, pos_y):
        
        grid = np.ndarray((self.linhas, self.colunas), dtype=np.int8, buffer=shm.buf)

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
                grid[new_x, new_y] = 99 #ou ROBO.ID
                self.pos = (new_x, new_y)
            finally:
                self.grid_mutex.release()
            
            if target == 2:
                try:
                    self.battery_mutex.acquire()
                    self.collect_battery()
                finally:
                    self.battery_mutex.release()
            elif target == 10:
                try:
                    self.robot_mutex.acquire()
                    self.fight()
                finally:
                    self.robot_mutex.release()


    def valid_move(pos_x, pos_y, grid):

        linhas = 40
        colunas = 20

        if pos_x < 0 or pos_x >= linhas or pos_y < 0 or pos_y >= colunas:
            return False
    
        valor_do_tabuleiro = grid[pos_x, pos_y]

        if valor_do_tabuleiro == 1:
            return None
        return valor_do_tabuleiro


    def sense_act(self):

        local_grid = self.shared_grid.copy()

        battery_pos = np.argwhere(local_grid == 2)
        enemy_pos = np.argwhere(local_grid == 10)

        my_pos = np.array([x_robot, y_robot])  # Posição atual do robô

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