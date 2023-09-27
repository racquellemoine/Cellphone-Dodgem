import math
import time
import random
random.seed(2)

class Player:
    def __init__(self, name, stalls_to_visit, T_theta):
        self.name = name
        self.stalls_to_visit = stalls_to_visit
        self.T_theta = T_theta
        self.pos_x = 0
        self.pos_y = 0

        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)

        self.sign_x = 1
        self.sign_y = 1

    def pass_lookup_info(self, other_players, obstacles):
        # store lookup info
        # print(other_players, obstacles)
        pass

    def encounter_obstacle(self):
        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)
        self.sign_x *= -1
        self.sign_y *= -1

    def get_action(self, pos_x, pos_y):
        # return 'look_up' or 'move'
        
        self.pos_x = pos_x
        self.pos_y = pos_y

        # if self.name == '1':
        #     return 'lookup'
        
        return 'move'
    
    def get_next_move(self):
        if self.pos_x <= 0:
            self.sign_x = 1
            self.vx = random.random()
            self.vy = math.sqrt(1 - self.vx**2)

        if self.pos_y <= 0:
            self.sign_y = 1
            self.vx = random.random()
            self.vy = math.sqrt(1 - self.vx**2)

        if self.pos_x >= 100:
            self.sign_x = -1
            self.vx = random.random()
            self.vy = math.sqrt(1 - self.vx**2)

        if self.pos_y >= 100:
            self.sign_y = -1
            self.vx = random.random()
            self.vy = math.sqrt(1 - self.vx**2)

        new_pos_x = self.pos_x + self.sign_x * self.vx
        new_pos_y = self.pos_y + self.sign_y * self.vy

        return new_pos_x, new_pos_y