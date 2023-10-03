import math
import random
from collections import deque
from itertools import chain
random.seed(2)

class Player:
    def __init__(self, id, name, color, initial_pos_x, initial_pos_y, stalls_to_visit, T_theta, tsp_path, num_players):
        self.id = id
        self.name = name
        self.color = color
        self.pos_x = initial_pos_x
        self.pos_y = initial_pos_y
        self.stalls_to_visit = stalls_to_visit
        self.T_theta = T_theta
        self.tsp_path = tsp_path
        self.num_players = num_players

        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)

        self.sign_x = 1
        self.sign_y = 1

        print(len(self.stalls_to_visit))
        print(len(self.tsp_path))
        # custom 
        self.q = deque()
        self.__init_queue()
    
    def __init_queue(self):
        stv = self.stalls_to_visit
        tsp = self.tsp_path

        min_d = float('inf')
        closest = 0
        for i, s in enumerate(stv):
            d = self.__calc_distance(self.pos_x, self.pos_y, s.x, s.y)
            if (d < min_d):
                min_d = d
                closest = i

        c = tsp.index(closest)
        for i in chain(tsp[c:], tsp[:c]):
            self.q.append(stv[i])

    def __calc_distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def __normalize(self, vx, vy):
        norm = self.__calc_distance(vx, vy, 0, 0)

        return vx / norm, vy / norm

    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        if stall_id == id(self.q[0]):
            self.q.popleft()
        else:
            for s in self.q:
                if stall_id == id(s):
                    self.q.remove(s)

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        pass

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)
        self.sign_x *= -1
        self.sign_y *= -1

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        
        self.pos_x = pos_x
        self.pos_y = pos_y
        
        return 'move'
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
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

        if (len(q) > 0):
            vx = self.q[0].x - self.pos_x
            vy = self.q[0].y - self.pos_y
            self.vx, self.vy = self.__normalize(vx, vy)

        new_pos_x = self.pos_x + self.sign_x * self.vx
        new_pos_y = self.pos_y + self.sign_y * self.vy

        return new_pos_x, new_pos_y
