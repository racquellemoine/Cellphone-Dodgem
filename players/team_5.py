import math
import random
import fast_tsp
import os
from collections import deque, defaultdict
from itertools import chain
import rvo2

random.seed(2)

LOOKUP_INTERVAL = 8
COLLISION_TIMEOUT = 12
DIST_EPS = 1e-5

#RVO Simulator Properties
TIME_STEP = 1
NEIGHBOR_DIST = 8
MAX_NEIGHBORS = 6
TIME_HORIZON = 1
TIME_HORIZON_OBS = 2
RADIUS = 0.6
MAX_SPEED = 1
DEF_VELO = (0, 0)

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def from_3d(pt):
        return Point(pt[0] * 5, pt[2] * 5)

    def to_3d(self):
        return (self.x / 5, 0.0, self.y / 5)

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

        # init rvo and environment boundary
        self.sim = None
        self.agent = None
        self.agent_q = deque()
        self.agent_id = dict()
        self.prev_pos = dict()
        self.__init_rvo()         

        # local avoidance
        self.lookup_timer = LOOKUP_INTERVAL
        self.path = deque()
        self.collision = 0
        self.is_alert = False
        self.seen_obs = set()

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

    def __init_rvo(self):
        self.sim = rvo2.PyRVOSimulator(TIME_STEP,
                                       NEIGHBOR_DIST,
                                       MAX_NEIGHBORS,
                                       TIME_HORIZON,
                                       TIME_HORIZON_OBS,
                                       RADIUS,
                                       MAX_SPEED,
                                       DEF_VELO)
        # environment bound
        self.sim.addObstacle([(0.0, 0.0),
                              (0.0, 100.0),
                              (100.0, 100.0),
                              (100.0, 0.0)])
        # self
        self.agent = self.sim.addAgent((self.pos_x, self.pos_y))

    @staticmethod
    def __calc_distance(x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    @staticmethod
    def __normalize(vx, vy):
        norm = Player.__calc_distance(vx, vy, 0, 0)

        return vx / norm, vy / norm

    @staticmethod
    def __build_poly(o_x, o_y):
        poly = []
        poly.append((o_x - 1.1, o_y - 1.1))
        poly.append((o_x + 1.1, o_y - 1.1))
        poly.append((o_x + 1.1, o_y + 1.1))
        poly.append((o_x - 1.1, o_y + 1.1))

        return poly

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

    def __kill_agent(self, aid):
        sim = self.sim

        sim.setAgentPosition(aid, (-1, -1))
        sim.setAgentPrefVelocity(aid, DEF_VELO)
        sim.setAgentVelocity(aid, DEF_VELO)
        sim.setAgentNeighborDist(aid, 0)
        sim.setAgentMaxNeighbors(aid, 0)


    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        seen = self.seen_obs
        sim = self.sim

        for oid, ox, oy in obstacles:
            if oid not in seen:
                seen.add(oid)
                sim.addObstacle(Player.__build_poly(ox, oy))

        sim.processObstacles()

        killed = []
        for pid in self.agent_id:
            if pid not in (p for p, _, _ in other_players):
                aid = self.agent_id[pid]
                self.__kill_agent(aid)
                self.agent_q.append(aid)
                killed.append(pid)
        for k in killed:
            self.agent_id.pop(pid, -1)

        for pid, px, py in other_players:
            if pid in self.agent_id:
                aid = self.agent_id[pid]
                prevx, prevy = self.prev_pos[pid]
                pv = (px - prevx, py - prevy)
                if sim.getAgentPrefVelocity(aid) == DEF_VELO:
                    sim.setAgentPrefVelocity(aid, pv)
                sim.setAgentPosition(aid, (px, py))
                sim.setAgentVelocity(aid, pv)
                self.prev_pos[pid] = (px, py)
            else:
                if self.agent_q:
                    aid = self.agent_q.popleft()
                    sim.setAgentPosition(aid, (px, py))
                    sim.setAgentNeighborDist(aid, NEIGHBOR_DIST)
                    sim.setAgentMaxNeighbors(aid, MAX_NEIGHBORS)
                else:
                    aid = sim.addAgent((px, py))
                self.agent_id[pid] = aid
                sim.setAgentPrefVelocity(aid, DEF_VELO)
                sim.setAgentVelocity(aid, DEF_VELO)
                self.prev_pos[pid] = (px, py)

        self.is_alert =  sim.getAgentNumAgentNeighbors(self.agent)

    def __update_path(self):
        if self.path:
            self.path.popleft()
        t = Point(self.q[0].x, self.q[0].y)
        self.path.append(t)

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        self.collision = COLLISION_TIMEOUT
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
        self.sim.setAgentPosition(self.agent, (pos_x, pos_y))
        
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
    
    def __is_deadlock(self, px, py, vx, vy):
        pd = self.__calc_distance(px, py, 0, 0)
        vd = self.__calc_distance(vx, vy, 0, 0)

        return pd < 0.1 and vd < 0.1

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
            self.sim.setAgentPrefVelocity(self.agent, (vx, vy))
            self.sign_x = 1
            self.sign_y = 1
            self.sim.doStep()
            prev = (self.vx, self.vy)
            self.vx, self.vy = self.sim.getAgentVelocity(self.agent)
            if self.__is_deadlock(*prev, self.vx, self.vy):
                self.collision = COLLISION_TIMEOUT
                self.vx = random.random()
                self.vy = math.sqrt(1 - self.vx**2)
                self.sign_x *= -1
                self.sign_y *= -1
            #print(f"{self.q[0].id} : {self.vx}, {self.vy}")
            #print("pos: ", self.pos_x, self.pos_y)
            #print("sim pos: ", self.sim.getAgentPosition(self.agent))
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
