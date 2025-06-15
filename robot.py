import os
import threading
import numpy as np
from multiprocessing import shared_memory
import time

robot_dtype = np.dtype([
    ('id', np.int32),
    ('strength', np.int32),
    ('energy', np.int32),
    ('speed', np.int32),
    ('pos', np.int32, (2,)),
    ('status', np.int8)
])

class Robot:
    def __init__(self, strength, energy, speed, status, robot_index, shm_name, robots_mutex, game_over_flag):
        self.strength = strength
        self.energy = energy
        self.speed = speed
        self.status = status
        self.robot_index = robot_index
        self.robots_mutex = robots_mutex
        self.game_over_flag = game_over_flag

        self.shm = shared_memory.SharedMemory(name=shm_name)
        self.robots_array = np.ndarray((4,), dtype=robot_dtype, buffer=self.shm.buf)
    def __call__(self):
        self.run()
    
    def run(self):
        self.robot_id = os.getpid()
        print(f"Robot {self.robot_id} (idx {self.robot_index}) iniciado.")

        thread1 = threading.Thread(target=self.sense_act, name="sense_act")
        thread2 = threading.Thread(target=self.housekeeping, name="housekeeping")

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

    def sense_act(self):
        # Implementação do thread sense_act
        pass

    def housekeeping(self):
        while self.status != "morto" and self.game_over_flag.value == 0:
            time.sleep(2)

            self.robots_mutex.acquire()
            try:
                self.energy = max(0, self.energy - 1)
                print(f"[HK] Robô {self.robot_id}: energia {self.energy}")

                if self.energy == 0:
                    self.status = "morto"
                    print(f"[HK] Robô {self.robot_id} morreu por falta de energia")

                self.robots_array[self.robot_index]['energy'] = self.energy
                self.robots_array[self.robot_index]['status'] = 0 if self.status == "morto" else 1
            finally:
                self.robots_mutex.release()

            self.robots_mutex.acquire()
            try:
                vivos = np.sum(self.robots_array['status'] == 1)
                if vivos == 1:
                    print(f"[HK] Robô {self.robot_id} detectou o fim do jogo.")
                    self.game_over_flag.value = 1
                    return
            finally:
                self.robots_mutex.release()