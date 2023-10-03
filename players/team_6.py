from dataclasses import dataclass
import math
import random
import sys

random.seed(2)

@dataclass
class Vector:
    x: float
    y: float

class Player:
    def __init__(self, id, name, color, initial_pos_x, initial_pos_y, stalls_to_visit, T_theta, tsp_path, num_players):
        self.id = id
        self.name = name
        self.color = color
        self.pos = Vector(initial_pos_x, initial_pos_y)
        self.stalls_to_visit = stalls_to_visit
        self.T_theta = T_theta
        self.tsp_path = tsp_path
        self.num_players = num_players

        # moving direction. make sure norm of (vx, vy) is 1
        self.dir = Vector(1, 0)

        # next lookup checkpoint
        self.next_ckpt = Vector(initial_pos_x, initial_pos_y)

        # tolerance for reaching a checkpoint
        self.epsilon = 0.0005

        self.sign_x = 1
        self.sign_y = 1

    def __calc_dist(self, a: Vector, b: Vector) -> float:
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

    # returns (x,y) of next stall we wanna visit
    def __next_stall(self) -> Vector:
        min_distance =  sys.maxsize
        curr_stall = None
        for stall in self.stalls_to_visit:
            curr_dist = math.sqrt((stall.x - self.pos_x)**2 + \
                                                   (stall.y - self.pos_y)**2)
            if curr_dist < min_distance:
                min_distance =  curr_dist
                curr_stall = stall
        return curr_stall

    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        pass

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        pass

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        self.dir = Vector(1,0) # arbitrary direction; needs to be changed
        self.sign_x *= -1
        self.sign_y *= -1

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        
        self.pos = Vector(pos_x, pos_y) # update current position

        return 'lookup' if self.__calc_dist(self.pos, self.next_ckpt) < self.epsilon else 'move'
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        ns = self.get_closest_stall()
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
