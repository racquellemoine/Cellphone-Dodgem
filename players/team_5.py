import math
import random
import fast_tsp
import pyvisgraph as vg
import os
import numpy as np
from collections import deque, defaultdict
from itertools import chain
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial import ConvexHull, Delaunay
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from .RVO_Py_MAS.RVO import RVO_update, reach, compute_V_des, reach

random.seed(2)

DEBUG = False
LOOKUP_INTERVAL = 1
OBSTACLE_HITBOX_SIZE = 2.2
STALL_HITBOX_SIZE = 2
DIST_EPS = 1e-5

class Position():
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
        self.collision = 0

        # RVO 
        self.ws = {'robot_radius' : 1.0,
                   'circular_obstacles' : [],
                   'boundary' : []}
        self.player_pos = [[0,0] for _ in range(num_players + 1)]
        self.player_v = [[0,0] for _ in range(num_players + 1)]
        self.neighbors = set()
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
            d = self.__calc_distance(px, py, stv[i].x, stv[i].y)
            self.dists[0][i+1] = math.ceil(d)

        for i in range(0, n):
            for j in range(0, n):
                d = self.__calc_distance(stv[i].x, stv[i].y, stv[j].x, stv[j].y)
                self.dists[i+1][j+1] = math.ceil(d)
                
        self.tsp_path = fast_tsp.find_tour(self.dists) if n > 1 else [0, 1]

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

    def __check_fov(self, obstacle):
        bx, by = obstacle[1], obstacle[2]
        fov = math.cos(math.pi / 8)
        a = self.vx, self.vy 
        b = self.__normalize(bx - self.pos_x, by - self.pos_y)

        return self.__dot(a, b) > fov

    # deprecated
    def __build_poly(self, obstacle):
        o_x, o_y = obstacle[1], obstacle[2]

        poly = []
        poly.append(vg.Point(o_x - 2, o_y - 2))
        poly.append(vg.Point(o_x + 2, o_y - 2))
        poly.append(vg.Point(o_x + 2, o_y + 2))
        poly.append(vg.Point(o_x - 2, o_y + 2))

        return poly

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        polys = self.polys
        ws = self.ws

        ws['circular_obstacles'].clear
        for o in obstacles:
            ws['circular_obstacles'].append([o[1], o[2], 1.0])
            if o not in polys:
                polys[o] = self.__build_poly(o)
                self.need_update = True

        ppos, pv = self.player_pos, self.player_v
        self.neighbors.clear()
        for pid, px, py in other_players:
            self.neighbors.add(pid)
            prevx, prevy = ppos[pid]
            ppos[pid] = [px, py]
            pv[pid] = [px - prevx, py - prevy] \
                if self.__calc_distance(px, py, prevx, prevy) <= 1.005 \
                else [0, 0]

        self.is_alert = (other_players or obstacles)

    """
    def __merge_nearby_obstacles(self):
        obstacle_centers = np.array(list(self.polys.keys()))[:,1:]
        ac = AgglomerativeClustering(n_clusters=None, linkage='single', metric='euclidean', distance_threshold=math.sqrt(2 * (OBSTACLE_HITBOX_SIZE * 2) ** 2))
        clusters = ac.fit(obstacle_centers).labels_
        
        blobs = []
        for i in range(0, clusters.max() + 1):
            cluster_centers = obstacle_centers[clusters == i]
            cluster_vertices = np.empty((len(cluster_centers) * 4, 2))
            for i, center in enumerate(cluster_centers):
                for j, d in enumerate(np.array([[1, 1], [1, -1], [-1, 1], [-1, -1]]) * OBSTACLE_HITBOX_SIZE):
                    cluster_vertices[i * 4 + j] = center + d
            hull = ConvexHull(cluster_vertices)
            blob = cluster_vertices[hull.vertices]
            for stall_center in self.stalls_to_visit + [Position(self.pos_x, self.pos_y)]:
                if Delaunay(blob).find_simplex((stall_center.x, stall_center.y)):
                    stall = Polygon([(stall_center.x + d1, stall_center.y + d2) for d1, d2 in np.array([[1, 1], [1, -1], [-1, -1], [-1, 1]]) * STALL_HITBOX_SIZE])
                    blob = list(Polygon(blob).difference(stall).exterior.coords)
            blobs.append(blob)
        
        if DEBUG:
            plt.figure()
            plt.axis('scaled')
            plt.xlim(0, 100)
            plt.ylim(0, 100)
            plt.gca().invert_yaxis()
            for blob in blobs:
                plt.plot(*zip(*blob))
            plt.show()
        
        return [[vg.Point(point[0], point[1]) for point in blob] for blob in blobs]
    """

    def __update_vg(self):
        if not self.polys:
            return
        #if len(self.polys) == 1:
        p = list(self.polys.values())
        #else :
        #    p = self.__merge_nearby_obstacles()
        self.graph.build(p, self.workers)

    def __update_path(self):
        self.path.clear()
        s = vg.Point(self.pos_x, self.pos_y)
        t = vg.Point(self.q[0].x, self.q[0].y)
        if not self.polys:
            new_path = [s, t]
        else:
            try:
                new_path = self.graph.shortest_path(s, t)
            except:
                new_path = [s, t]
        for p in new_path[1:]:
            self.path.append(p)

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        self.collision = 15
        self.lookup_timer = 0
        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)
        self.sign_x *= -1
        self.sign_y *= -1

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        self.pos_x = pos_x
        self.pos_y = pos_y

        if len(self.q) == 0:
            return 'move'

        if self.need_update:
            self.__update_vg()
            self.__update_path()
            self.need_update = False

        t = self.path[0]

        if self.__calc_distance(pos_x, pos_y, t.x, t.y) < DIST_EPS:
            self.path.popleft()

        if self.lookup_timer == 0:
            self.lookup_timer = LOOKUP_INTERVAL

            return 'lookup'
        
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
            
            self.vx, self.vy = self.__normalize(vx, vy) if self.__calc_distance(vx, vy, 0, 0) > 1 else (vx, vy)

        elif len(self.q) == 0:
            self.vx, self.vy = 0, 0

        if self.is_alert:
            X = [self.player_pos[pid] for pid in self.neighbors]
            X.append([self.pos_x, self.pos_y])
            V = [self.player_v[pid] for pid in self.neighbors]
            V.append([self.vx, self.vy])
            V_max = [1.0 for _ in range(len(X))]
            V_opt = RVO_update(X, V, V, self.ws)
            self.vx, self.vy = V_opt[-1][0], V_opt[-1][1]

        new_pos_x = self.pos_x + self.sign_x * self.vx
        new_pos_y = self.pos_y + self.sign_y * self.vy

        return new_pos_x, new_pos_y
