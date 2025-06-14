import os
import threading

class Robot:
    def __init__(self, strength, energy, speed, status):
        self.strength = strength
        self.energy = energy
        self.speed = speed
        self.status = status
    def __call__(self):
        self.run()
    
    def run(self):
        self.robot_id = os.getpid()
        print(f"Robot {self.robot_id} started with strength {self.strength}, energy {self.energy}, speed {self.speed}, status {self.status}")
        thread1 = threading.Thread(target=self.sense_act, name="sense_act")
        thread2 = threading.Thread(target=self.housekeeping, name="housekeeping")

        thread1.start()
        thread2.start()

    def sense_act(self):
        # Implementação do thread sense_act
        pass
    def housekeeping(self):
        # Implementação do thread housekeeping
        pass