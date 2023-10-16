import math
import random
import fast_tsp
import os
from collections import deque, defaultdict
from itertools import chain
from pathfinder import navmesh_baker as nmb

random.seed(2)

LOOKUP_INTERVAL = 8
OBSTACLE_HITBOX_SIZE = 2.1
STALL_HITBOX_SIZE = 2
DIST_EPS = 1e-5

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Player:
    def __init__(self, id, name, color, initial_pos_x, initial_pos_y, stalls_to_visit, T_theta, tsp_path, num_players):
        self.id = id
        self.name = name
        self.color = color
        self.pos_x = initial_pos_x
        self.pos_y = initial_pos_y
        self.stalls_to_visit = stalls_to_visit
        self.num_stalls = len(stalls_to_visit)
        self.T_theta = T_theta
        self.tsp_path = tsp_path
        self.num_players = num_players

        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)

        self.sign_x = 1
        self.sign_y = 1

        # global pathing
        self.dists = [[0 for _ in range(self.num_stalls + 1)] for _ in range(self.num_stalls + 1)]
        self.q = deque()
        self.need_update = True
        self.__init_tsp()
        self.__init_queue()

        # local avoidance
        self.lookup_timer = LOOKUP_INTERVAL
        self.path = deque()
        self.collision = 0
        self.is_alert = False

    def __init_queue(self):
        stv = self.stalls_to_visit
        tsp = self.tsp_path

        for i in tsp[1:]:
            self.q.append(stv[i-1])

    def __init_tsp(self):
        stv = self.stalls_to_visit
        n = self.num_stalls
        px, py = self.pos_x, self.pos_y

        for i in range(0, n):
            d = Player.__calc_distance(px, py, stv[i].x, stv[i].y)
            self.dists[0][i+1] = math.ceil(d)

        for i in range(0, n):
            for j in range(0, n):
                d = Player.__calc_distance(stv[i].x, stv[i].y, stv[j].x, stv[j].y)
                self.dists[i+1][j+1] = math.ceil(d)
                
        self.tsp_path = fast_tsp.find_tour(self.dists) if n > 1 else [0, 1]

    @staticmethod
    def __calc_distance(x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    @staticmethod
    def __normalize(vx, vy):
        norm = Player.__calc_distance(vx, vy, 0, 0)

        return vx / norm, vy / norm


    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        if stall_id == self.q[0].id:
            self.q.popleft()
            if len(self.q) > 0:
                self.__update_path()
                self.lookup_timer = 0
        else:
            r = None 
            for s in self.q:
                if stall_id == s.id:
                    r = s
                    break
            self.q.remove(r)

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        pass
    
    def __update_path(self):
        self.path.clear()
        s = Point(self.pos_x, self.pos_y)
        t = Point(self.q[0].x, self.q[0].y)
        new_path = [s, t]
        for p in new_path[1:]:
            self.path.append(p)

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        self.collision = 12
        self.lookup_timer = 0
        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)
        self.sign_x *= -1
        self.sign_y *= -1

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move' or 'lookup move'
        
        self.pos_x = pos_x
        self.pos_y = pos_y
        
        if len(self.q) == 0:
            return 'move'

        if self.need_update:
            self.__update_path()
            self.need_update = False

        t = self.path[0]

        if Player.__calc_distance(pos_x, pos_y, t.x, t.y) < DIST_EPS:
            self.path.popleft()

        if self.lookup_timer == 0:
            self.lookup_timer = 1 if self.is_alert else LOOKUP_INTERVAL
            self.is_alert = False

            return 'lookup move'
        
        self.lookup_timer -= 1

        return 'move'
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        if self.collision > 0:
            self.collision -= 1
            if self.collision == 0 and len(self.q) > 0:
                self.__update_path()
        elif len(self.q) > 0:
            t = self.path[0]
            vx = t.x - self.pos_x
            vy = t.y - self.pos_y
            self.sign_x = 1
            self.sign_y = 1
            self.vx, self.vy = list(Player.__normalize(vx, vy)) \
                                if Player.__calc_distance(vx, vy, 0, 0) > 1 \
                                else [vx, vy] 
        elif len(self.q) == 0:
            self.vx, self.vy = 0, 0

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
