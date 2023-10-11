import math
import queue
import random
import numpy
import fast_tsp
from collections import deque

random.seed(2)


class Location:
    def __init__(self, x, y, target_x, target_y, parent, distance_travelled):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.parent = parent
        self.distance_travelled = distance_travelled
        self.children = []

    # heuristic is absolute distance to target, return lt if distance already travelled + h is <
    def __lt__(self, other):
        self_h = self.__calc_distance(self.x, self.y, self.target_x, self.target_y)
        other_h = self.__calc_distance(other.x, other.y, other.target_x, other.target_y)
        return (self_h + self.distance_travelled) < (other_h + other.distance_travelled)

    # two location states are equal if they have the same x and y coordinates
    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __calc_distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    # TODO: incorporate obstacles! if the new position would encounter an obstacle, return None!!
    def move(self, angle, delta_y, delta_x):
        new_y = math.sin(angle)
        new_x = math.cos(angle)
        sign_y = 1
        sign_x = 1
        if delta_y < 0:
            sign_y = -1

        if delta_x < 0:
            sign_x = -1

        return Location(self.x + new_x*sign_x, self.y + new_y*sign_y, self.target_x, self.target_y, self, self.distance_travelled + 1)

    def expand(self):
        delta_y = self.target_y - self.y
        delta_x = self.target_x - self.x
        theta = math.atan(numpy.abs(delta_y) / numpy.abs(delta_x))
        # TODO: find optimal value of theta (aka how much to branch move) and decide if to do more branching
        delta = 3
        children = [
            self.move(theta + delta, delta_y, delta_x),
            self.move(theta + 2*delta, delta_y, delta_x),
            self.move(theta, delta_y, delta_x),
            self.move(theta - delta, delta_y, delta_x),
            self.move(theta - 2 * delta, delta_y, delta_x)
        ]
        self.children = [state for state in children if state is not None]
        return self.children

class Player:
    def __init__(self, id, name, color, initial_pos_x, initial_pos_y, stalls_to_visit, T_theta, tsp_path, num_players):
        self.id = id
        self.name = name
        self.color = color
        self.pos_x = initial_pos_x
        self.pos_y = initial_pos_y
        self.stalls_to_visit = stalls_to_visit
        self.num_stalls = len(stalls_to_visit)  # number of stalls to visit
        self.T_theta = T_theta
        self.tsp_path = tsp_path
        self.num_players = num_players

        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx ** 2)

        self.sign_x = 1
        self.sign_y = 1

        #next move
        self.action = 'move'

        # team 5 vars
        self.dists = [[0 for _ in range(self.num_stalls + 1)] for _ in range(self.num_stalls + 1)]
        self.q = deque()
        # var to count how long to be in obstacle avoidance mode
        self.collision_counter = 0
        self.target_locations = []

        # storing lookup info
        self.other_players = {}
        self.obstacles = {}
        self.counter = -1

        self.tsp()
        self.queue_path()

    # initialize queue with stalls to visit from tsp in order
    def queue_path(self):
        stv = self.stalls_to_visit
        tsp = self.tsp_path

        for i in tsp[1:]:
            self.q.append(stv[i - 1])

    # get tsp in relation to us
    def tsp(self):
        stv = self.stalls_to_visit
        n = self.num_stalls
        px, py = self.pos_x, self.pos_y

        for i in range(0, n):
            d = self.__calc_distance(px, py, stv[i].x, stv[i].y)
            self.dists[0][i + 1] = math.ceil(d)

        for i in range(0, n):
            for j in range(0, n):
                d = self.__calc_distance(stv[i].x, stv[i].y, stv[j].x, stv[j].y)
                self.dists[i + 1][j + 1] = math.ceil(d)

        self.tsp_path = fast_tsp.find_tour(self.dists)

    def __calc_distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        if stall_id == self.q[0].id:
            self.q.popleft()
        else:
            for s in self.q:
                if stall_id == s.id:
                    self.q.remove(s)

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        for player in other_players:
            self.other_players[player[0]] = player[1], player[2]

        for obstacle in obstacles:
            self.obstacles[obstacle[0]] = obstacle[1], obstacle[2]

        # see if any obstacles are in our path
        # if so, calculate new target point, add to target locations lists
        # modify move function to head towards target point if list isn't empty
        # else head towards stall

        self.action = 'move'

    # simulator calls this function when the player encounters an obstacle
    # Maybe if edited and we're given the obstacle id we can add it to our database
    def encounter_obstacle(self):
        self.collision_counter = 20
        self.obstacles[self.counter] = (self.counter, self.pos_x, self.pos_y)
        self.counter -= 1
        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx ** 2)
        self.sign_x *= -1
        self.sign_y *= -1

        # self.pos_x += self.sign_x * self.vx
        # self.pos_y += self.sign_y * self.vy

    def A_star_obstacle_search(self):
        frontier = queue.PriorityQueue()
        initial_location = Location(self.pos_x, self.pos_y, self.q[0].x, self.q[0].y, self.pos_x, self.pos_y)
        frontier.put(initial_location)

        explored = set()

        while frontier.qsize() > 0:
            state = frontier.get()

            if (state.x, state.y) not in explored:
                explored.add((state.x, state.y))
                # return path once hit target
                if self.hit_goal(state) or state.distance_travelled >= 10:
                    return
                for child_location in state.expand():
                    if (child_location.x, child_location.y) not in explored:
                        frontier.put(child_location)
            explored.add(state)


    # returns true if position of location is the position of the target stall
    # TODO: fix this to be within radius of target stall, not directly on it
    def hit_goal(self, location):
        return (location.x == self.q[0].x) and (location.y == self.q[0].y)

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'

        self.pos_x = pos_x
        self.pos_y = pos_y

        return 'move'

    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):

        if self.collision_counter > 0:
            self.collision_counter -= 1
        elif self.q and len(self.q) > 0:
            target_stall = self.q[0]
            delta_y = target_stall.y - self.pos_y
            delta_x = target_stall.x - self.pos_x

            if delta_y == 0:
                self.vy = 0
                self.vx = 1
            elif delta_x == 0:
                self.vy = 1
                self.vx = 0
            else:
                angle = math.atan(numpy.abs(delta_y) / numpy.abs(delta_x))
                # sin/cos multiplied by 1 to get the straight line distance to the point
                self.vy = math.sin(angle)
                self.vx = math.cos(angle)

            if delta_y < 0:
                self.sign_y = -1
            else:
                self.sign_y = 1

            if delta_x < 0:
                self.sign_x = -1
            else:
                self.sign_x = 1
        else:
            # post game strategy -> find a place to hide and accumulate phone points
            self.vx = 0
            self.vy = 0

        new_pos_x = self.pos_x + self.sign_x * self.vx
        new_pos_y = self.pos_y + self.sign_y * self.vy

        return new_pos_x, new_pos_y
