import math
import random
import fast_tsp
import pyvisgraph as vg
import os
from collections import deque, defaultdict
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

        # pathing
        self.dists = [[0 for _ in range(self.num_stalls + 1)] for _ in range(self.num_stalls + 1)]
        self.q = deque()
        self.__init_tsp()
        self.__init_queue()
    
        # obstacle avoidance
        self.lookup_timer = 1
        self.polys = defaultdict(list)
        self.graph = vg.VisGraph()
        self.workers = len(os.sched_getaffinity(0))
        self.need_update = True
        self.path = deque()
        self.curr_g = set()

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
            self.need_update = True
        else:
            r = []
            for s in self.q:
                if stall_id == s.id:
                    r.append(s)
            for s in r:
                self.q.remove(s)

    def __check_fov(self, obstacle):
        bx, by = obstacle[1], obstacle[2]
        fov = math.cos(math.pi / 8)
        a = self.vx, self.vy 
        b = self.__normalize(bx - self.pos_x, by - self.pos_y)

        return self.__dot(a, b) > fov

    def __build_poly(self, obstacle):
        o_x, o_y = obstacle[1], obstacle[2]

        poly = []
        poly.append(vg.Point(o_x - 1.51, o_y - 1.51))
        poly.append(vg.Point(o_x + 1.51, o_y - 1.51))
        poly.append(vg.Point(o_x + 1.51, o_y + 1.51))
        poly.append(vg.Point(o_x - 1.51, o_y + 1.51))

        return poly

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        polys = self.polys
        cg = self.curr_g

        for o in obstacles:
            if o not in polys:
                polys[o] = self.__build_poly(o)

            if self.__check_fov(o) and o not in cg:
                cg.add(o)
                self.need_update = True

    def __update_vg(self):
        p = list(map(lambda o: self.polys[o], self.curr_g))
        self.graph.build(p, self.workers)

    def __update_path(self):
        path = self.path
        s = vg.Point(self.pos_x, self.pos_y)
        t = vg.Point(self.q[0].x, self.q[0].y)
        new_path = self.graph.shortest_path(s, t)
        path.clear()
        for p in new_path[1:]:
            path.append(p)

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

        if self.need_update:
            self.__update_vg()
            self.__update_path()
            self.need_update = False

        t = self.path[0]

        if self.__calc_distance(pos_x, pos_y, t.x, t.y) < 1:
            self.path.popleft()

        if self.lookup_timer == 0:
            return 'lookup'
        
        self.lookup_timer -= 1
        
        return 'move'
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        if len(self.q) > 0:
            t = self.path[0]
            vx = t.x - self.pos_x
            vy = t.y - self.pos_y
            self.sign_x = 1
            self.sign_y = 1
            
            self.vx, self.vy = self.__normalize(vx, vy) if self.__calc_distance(vx, vy, 0, 0) > 1 else (vx, vy)

        elif len(self.q) == 0:
            self.vx, self.vy = 0, 0

        new_pos_x = self.pos_x + self.sign_x * self.vx
        new_pos_y = self.pos_y + self.sign_y * self.vy

        return new_pos_x, new_pos_y
