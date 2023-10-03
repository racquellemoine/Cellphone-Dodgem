from dataclasses import dataclass
import math
import random
import sys

random.seed(2)

HORIZON = 10 # how far we can look
DANGER_ZONE = 0.5 # how close we can get to an obstacle/person

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

        # unit vector representing direction of movement
        self.dir = Vector(1, 0)

        # next lookup checkpoint
        self.next_ckpt = Vector(initial_pos_x, initial_pos_y)

        # tolerance for reaching a checkpoint
        self.epsilon = 0.0005

        self.sign_x = 1
        self.sign_y = 1

    def __calc_dist(self, a: Vector, b: Vector) -> float:
        return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

    # returns normalized vector from a to b
    def __normalize(self, source: Vector, dest: Vector) -> Vector:
        dist = self.__calc_dist(source, dest)
        return Vector((dest.x - source.x)/dist, (dest.y - source.y)/dist)

    def __innerprod(self, a: Vector, b: Vector) -> float:
        return a.x*b.x + a.y*b.y

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
        # update self.dir and self.next_ckpt according to new info
        
        self.dir = self.__normalize(self.pos, self.__next_stall())
        safe_go = (10-DANGER_ZONE)/2 # how far we can go safely without lookup

        # adjust direction based on obstacles & walls

        
        # look at other players
        for player in other_players:
            p = Vector(player.pos_x, player.pos_y)
            u = self.__normalize(self.pos, p)
            cos_theta = self.__innerprod(self.dir, u)
            if cos_theta > 0:
                # player is in front of us
                d = self.__calc_dist(self.pos, p)
                # update safe_go
                safe_go = min(safe_go, (d-DANGER_ZONE)/(2*cos_theta))
        
        self.next_ckpt = Vector(self.pos.x + safe_go*self.dir.x, self.pos.y + safe_go*self.dir.y)

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        self.dir = Vector(1,0) # arbitrary direction; needs to be changed
        self.sign_x *= -1
        self.sign_y *= -1

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        
        self.pos = Vector(pos_x, pos_y) # update current position
        
        vab = Vector(self.next_ckpt.x - pos_x, self.next_ckpt.y - pos_y)
        return 'lookup' if self.__innerprod(vab, self.dir) < self.epsilon else 'move'
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        return self.pos.x + self.dir.x, self.pos.y + self.dir.y
