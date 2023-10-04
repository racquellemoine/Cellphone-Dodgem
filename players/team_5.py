import math
import random
import fast_tsp
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
        self.num_stalls = len(stalls_to_visit)
        self.T_theta = T_theta
        self.tsp_path = tsp_path
        self.num_players = num_players

        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)

        self.sign_x = 1
        self.sign_y = 1

        # custom 
        self.dists = [[0 for _ in range(self.num_stalls + 1)] for _ in range(self.num_stalls + 1)]
        self.q = deque()
        self.encounter = 0

        self.__init_tsp()
        self.__init_queue()
    
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
            d = self.__calc_distance(px, py, stv[i].x, stv[i].y)
            self.dists[0][i+1] = math.ceil(d)

        for i in range(0, n):
            for j in range(0, n):
                d = self.__calc_distance(stv[i].x, stv[i].y, stv[j].x, stv[j].y)
                self.dists[i+1][j+1] = math.ceil(d)
                
        self.tsp_path = fast_tsp.find_tour(self.dists)

    def __calc_distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    def __normalize(self, vx, vy):
        norm = self.__calc_distance(vx, vy, 0, 0)

        return vx / norm, vy / norm

    def __dot(self, a, b):
        ax, ay = a
        bx, by = b

        return ax * bx + ay * by

    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        if stall_id == self.q[0].id:
            self.q.popleft()
            print(self.q[0].id)
        else:
            for s in self.q:
                if stall_id == s.id:
                    self.q.remove(s)

    def __check_fov(self, obstacle):
        bx, by = obstacle
        fov = math.cos(math.pi / 8)
        a = self.vx, self.vy 
        b = self.__normalize(bx - self.pos_x, by - self.pos_y)

        return self.__dot(a, b) > fov

    def __check_collision(self, obstacle):
        o_x, o_y = obstacle
        p_x, p_y = self.pos_x, self.pos_y
        t_x, t_y = self.q[0].x, self.q[0].y

        c1x, c1y = o_x - 1, o_y - 1
        c2x, c2y = o_x + 1, o_y - 1
        c3x, c3y = o_x + 1, o_y + 1
        c4x, c4y = o_x - 1, o_y + 1

        if self.intersection(c1x, c1y - 0.5, c2x, c2y - 0.5, p_x, p_y, t_x, t_y):
            return True
        if self.intersection(c2x + 0.5, c2y, c3x + 0.5, c3y, p_x, p_y, t_x, t_y):
            return True
        if self.intersection(c3x, c3y + 0.5, c4x, c4y + 0.5, p_x, p_y, t_x, t_y):
            return True
        if self.intersection(c4x - 0.5, c4y, c1x - 0.5, c1y, p_x, p_y, t_x, t_y):
            return True

        return False


    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        for o in obstacles:
            if self.__check_fov(o) and self.__check_collision(o):
                pass

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        self.encounter = 15

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
        if self.encounter > 0:
            self.encounter -= 1
        elif len(self.q) > 0:
            vx = self.q[0].x - self.pos_x
            vy = self.q[0].y - self.pos_y
            self.sign_x = 1
            self.sign_y = 1
            self.vx, self.vy = self.__normalize(vx, vy)
        elif len(self.q) == 0:
            self.vx, self.vy = 0, 0

        new_pos_x = self.pos_x + self.sign_x * self.vx
        new_pos_y = self.pos_y + self.sign_y * self.vy

        return new_pos_x, new_pos_y
