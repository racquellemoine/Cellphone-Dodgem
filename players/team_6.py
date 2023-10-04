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
        self.stalls_visited = []
        self.curr_stall = self.__next_stall()
        self.T_theta = T_theta
        self.tsp_path = tsp_path
        self.num_players = num_players
        self.known_obstacles = []

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
        if dist == 0:
            return Vector(0,0)
        return Vector((dest.x - source.x)/dist, (dest.y - source.y)/dist)

    def __innerprod(self, a: Vector, b: Vector) -> float:
        return a.x*b.x + a.y*b.y

    # returns (x,y) of next stall we wanna visit
    def __next_stall(self) -> Vector:
        min_distance = sys.maxsize
        curr_stall = None
        for stall in self.stalls_to_visit:
            curr_dist = self.__calc_dist(self.pos, stall)
            if curr_dist < min_distance and stall not in self.stalls_visited:
                min_distance =  curr_dist
                curr_stall = stall
        if curr_stall is None:
            return Vector(0,0)
        self.stalls_visited.append(curr_stall)
        return curr_stall

    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        self.stalls_visited.append(self.curr_stall)
        self.curr_stall = self.__next_stall()

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        # update self.dir and self.next_ckpt according to new info
        
        self.dir = self.__normalize(self.pos, Vector(self.curr_stall.x, self.curr_stall.y))
        safe_go = (10-DANGER_ZONE)/2 # how far we can go safely without lookup

        # adjust direction based on obstacles & walls
        for obstacle in obstacles:
            if obstacle not in self.known_obstacles:
                self.known_obstacles.append(Vector(obstacle[1], obstacle[2]))
                # obstacle is a tuple of (x,y,radius)

        for obstacle in obstacles:
            o = Vector(obstacle[0], obstacle[1])
            u = self.__normalize(self.pos, o)
            cos_theta = self.__innerprod(self.dir, u)
            if cos_theta > 0:
                # obstacle is in front of us
                d = self.__calc_dist(self.pos, o)
                # update safe_go
                safe_go = min(safe_go, (d-DANGER_ZONE)/(2*cos_theta))

        # look at other players
        for player in other_players:
            p = Vector(player[1], player[2])
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
        # Try moving in the opposite direction of the current dir vector
        new_pos = Vector(self.pos.x - self.dir.x, self.pos.y - self.dir.y)
        if new_pos not in self.known_obstacles:
            self.pos = new_pos
            self.next_ckpt = Vector(self.pos.x + self.dir.x, self.pos.y + self.dir.y)
            return

        # If the opposite direction is blocked, try moving in a perpendicular direction
        if self.dir.x == 0:
            # If the current dir vector is vertical, try moving horizontally
            new_pos = Vector(self.pos.x + 1, self.pos.y)
            if new_pos not in self.known_obstacles:
                self.dir = Vector(1, 0)
                self.pos = new_pos
                self.next_ckpt = Vector(self.pos.x + self.dir.x, self.pos.y + self.dir.y)
                return
            new_pos = Vector(self.pos.x - 1, self.pos.y)
            if new_pos not in self.known_obstacles:
                self.dir = Vector(-1, 0)
                self.pos = new_pos
                self.next_ckpt = Vector(self.pos.x + self.dir.x, self.pos.y + self.dir.y)
                return
        else:
            # If the current dir vector is horizontal, try moving vertically
            new_pos = Vector(self.pos.x, self.pos.y + 1)
            if new_pos not in self.known_obstacles:
                self.dir = Vector(0, 1)
                self.pos = new_pos
                self.next_ckpt = Vector(self.pos.x + self.dir.x, self.pos.y + self.dir.y)
                return
            new_pos = Vector(self.pos.x, self.pos.y - 1)
            if new_pos not in self.known_obstacles:
                self.dir = Vector(0, -1)
                self.pos = new_pos
                self.next_ckpt = Vector(self.pos.x + self.dir.x, self.pos.y + self.dir.y)
                return

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
