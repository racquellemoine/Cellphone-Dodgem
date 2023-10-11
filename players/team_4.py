import math
import queue
import random
import numpy
import fast_tsp
random.seed(2)


class Location:
    def __init__(self, x, y, target_x, target_y, parent, distance_travelled, player):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.parent = parent
        self.distance_travelled = distance_travelled
        self.children = []
        self.player = player

    # heuristic is absolute distance to target, return lt if distance already travelled + h is <
    def __lt__(self, other):
        self_h = self.__calc_distance(self.x, self.y, self.target_x, self.target_y)
        other_h = self.__calc_distance(other.x, other.y, other.target_x, other.target_y)
        return (self_h + self.distance_travelled) < (other_h + other.distance_travelled)

    # two location states are equal if they have the same x and y coordinates
    # TODO: this should be within a margin of x and y, not exactly equal
    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __calc_distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def move(self, dx, dy):
        new_x_pos = self.x + dx
        new_y_pos = self.y + dy

        if new_y_pos > 99 or new_y_pos < 1:
            return None

        if new_x_pos > 99 or new_x_pos < 1:
            return None

        # TODO: expand to account for players as well and their expected trajectories if known to us
        if self.player.obstacles and len(self.player.obstacles) > 0:
            for key in self.player.obstacles.keys():
                obs_x = self.player.obstacles[key][0]
                obs_y = self.player.obstacles[key][1]
                if self.check_collision_obstacle(obs_x, obs_y, self.x, self.y, new_x_pos, new_y_pos):
                    return None

        return Location(new_x_pos, new_y_pos, self.target_x, self.target_y, self, self.distance_travelled + 1, self.player)

    def expand(self):
        children = [
            self.move(0, .9),
            self.move(0, -.9),
            self.move(-.9, 0),
            self.move(.9, 0),
            self.move(-1/math.sqrt(2), 1/math.sqrt(2)),
            self.move(1/math.sqrt(2), 1/math.sqrt(2)),
            self.move(1 / math.sqrt(2), -1 / math.sqrt(2)),
            self.move(-1 / math.sqrt(2), -1 / math.sqrt(2))
        ]
        self.children = [state for state in children if state is not None]
        return self.children

    def check_collision_obstacle(self, stall_x, stall_y, p_x, p_y, new_p_x, new_p_y):
        c1x, c1y = stall_x - 1, stall_y - 1
        c2x, c2y = stall_x + 1, stall_y - 1
        c3x, c3y = stall_x + 1, stall_y + 1
        c4x, c4y = stall_x - 1, stall_y + 1

        if self.intersection(c1x, c1y - 0.5, c2x, c2y - 0.5, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.intersection(c2x + 0.5, c2y, c3x + 0.5, c3y, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.intersection(c3x, c3y + 0.5, c4x, c4y + 0.5, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.intersection(c4x - 0.5, c4y, c1x - 0.5, c1y, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.check_collision(c1x, c1y, c1x, c1y, p_x, p_y, new_p_x, new_p_y):
            return True

        if self.check_collision(c2x, c2y, c2x, c2y, p_x, p_y, new_p_x, new_p_y):
            return True

        if self.check_collision(c3x, c3y, c3x, c3y, p_x, p_y, new_p_x, new_p_y):
            return True

        if self.check_collision(c4x, c4y, c4x, c4y, p_x, p_y, new_p_x, new_p_y):
            return True

        return False

    def intersection(self, a, b, c, d, e, f, g, h):
        s0 = [(a, b), (c, d)]
        s1 = [(e, f), (g, h)]
        dx0 = s0[1][0]-s0[0][0]
        dx1 = s1[1][0]-s1[0][0]
        dy0 = s0[1][1]-s0[0][1]
        dy1 = s1[1][1]-s1[0][1]
        p0 = dy1*(s1[1][0]-s0[0][0]) - dx1*(s1[1][1]-s0[0][1])
        p1 = dy1*(s1[1][0]-s0[1][0]) - dx1*(s1[1][1]-s0[1][1])
        p2 = dy0*(s0[1][0]-s1[0][0]) - dx0*(s0[1][1]-s1[0][1])
        p3 = dy0*(s0[1][0]-s1[1][0]) - dx0*(s0[1][1]-s1[1][1])
        return (p0*p1<=0) & (p2*p3<=0)

    def check_collision(self, x1, y1, new_x1, new_y1, x2, y2, new_x2, new_y2):
        vx = new_x1 - x1
        vy = new_y1 - y1
        wx = new_x2 - x2
        wy = new_y2 - y2

        A = vx ** 2 + wx ** 2 + vy ** 2 + wy ** 2 - 2 * vx * wx - 2 * vy * wy
        B = 2 * x1 * vx - 2 * x2 * vx - 2 * x1 * wx + 2 * x2 * wx + 2 * y1 * vy - 2 * y2 * vy - 2 * y1 * wy + 2 * y2 * wy
        C = x1 ** 2 + x2 ** 2 + y1 ** 2 + y2 ** 2 - 2 * x1 * x2 - 2 * y1 * y2 - 0.25

        D = B ** 2 - 4 * A * C

        if A == 0:
            if B == 0:
                if C == 0:
                    return True
                else:
                    return False
            root = (-1 * C) / B
            if root >= 0 and root <= 1:
                return True
            return False

        if D < 0:
            return False

        if D == 0:
            root = (-1 * B) / (2 * A)
            if root >= 0 and root <= 1:
                return True

        if D > 0:
            root1 = (-1 * B + math.sqrt(D)) / (2 * A)
            root2 = (-1 * B - math.sqrt(D)) / (2 * A)

            if root1 > 0 and root1 <= 1:
                return True
            if root2 > 0 and root2 <= 1:
                return True

        return False

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
        self.paths = []
        self.reroute = []
        # var to count how long to be in obstacle avoidance mode
        self.collision_counter = 0
        self.target_locations = []

        # storing lookup info
        self.other_players = {}
        self.obstacles = {}
        self.counter = -1

        self.tsp()
        self.queue_path()
        self.in_endgame = False

    # initialize queue with stalls to visit from tsp in order
    def queue_path(self):
        stv = self.stalls_to_visit
        tsp = self.tsp_path

        for i in tsp[1:]:
            self.paths.append(stv[i - 1])

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
        for s in self.paths:
            if stall_id == s.id:
                self.paths.remove(s)

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        for player in other_players:
            self.other_players[player[0]] = player[1], player[2]

        for obstacle in obstacles:
            self.obstacles[obstacle[0]] = obstacle[1], obstacle[2]

        self.reroute = self.A_star_obstacle_search()
        # see if any obstacles are in our path
        # if so, calculate new target point, add to target locations lists
        # modify move function to head towards target point if list isn't empty
        # else head towards stall

        self.action = 'move'

    # simulator calls this function when the player encounters an obstacle
    # Maybe if edited and we're given the obstacle id we can add it to our database
    def encounter_obstacle(self):
        if self.in_endgame:
            self.collision_counter = 20
        else:
            self.collision_counter = 9
        
        self.action = 'lookup'
        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx ** 2)
        self.sign_x *= -1
        self.sign_y *= -1

    def A_star_obstacle_search(self):
        frontier = queue.PriorityQueue()
        if self.paths and len(self.paths) > 0:
            initial_location = Location(self.pos_x, self.pos_y, self.paths[0].x, self.paths[0].y, None, 0, self)
            frontier.put(initial_location)

            explored = set()

            while frontier.qsize() > 0:
                state = frontier.get()

                if (state.x, state.y) not in explored:
                    explored.add((state.x, state.y))
                    # return path once hit target
                    if state.distance_travelled >= 10 or self.hit_goal(state):
                        return self.get_path_to_goal(state)
                    for child_location in state.expand():
                        if (child_location.x, child_location.y) not in explored:
                            frontier.put(child_location)

        return None

    def get_path_to_goal(self, location):
        path_to_goal = []
        while location.parent:
            path_to_goal.insert(0, (location.x, location.y))
            location = location.parent
        return path_to_goal

    # returns true if position of location is the position of the target stall
    # TODO: fix this to be within radius of target stall, not directly on it
    def hit_goal(self, location):
        return (location.x == self.paths[0].x) and (location.y == self.paths[0].y)

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'

        self.pos_x = pos_x
        self.pos_y = pos_y

        return self.action

    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):

        #Once A-star complete:
        #Unsure the structure which it returns, but integrating it into get_next_move should look something like this
        '''
        if len(self.paths) == 0:
            #exit strategy code
        else: 
            if len(self.obstacle_path) > 0:
                target_location = self.obstacle_path[0]
                delta_y = target_stall.y - self.pos_y
                delta_x = target_stall.x - self.pos_x
                self.obstacle_path.remove(target_location)

            elif self.paths and len(self.paths) > 0:
                target_stall = self.paths[0]
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
        
        new_pos_x = self.pos_x + self.sign_x * self.vx
        new_pos_y = self.pos_y + self.sign_y * self.vy

        return new_pos_x, new_pos_y


        '''
        reroute = False
        if self.collision_counter > 0:
            self.collision_counter -= 1
        elif self.reroute and len(self.reroute) > 0:
            reroute = True
        elif self.paths and len(self.paths) > 0:
            target_stall = self.paths[0]
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
            self.in_endgame = True
            return self.endgame()

        if reroute:
            new_pos_x = self.reroute[0][0]
            new_pos_y = self.reroute[0][1]
            self.reroute = self.reroute[1:]
        else:
            new_pos_x = self.pos_x + self.sign_x * self.vx
            new_pos_y = self.pos_y + self.sign_y * self.vy

        return new_pos_x, new_pos_y

    def endgame(self):
        final_pos_y = 5 if self.pos_y < 50 else 95
        final_pos_x = 5 if self.pos_x < 50 else 95
        delta_y = final_pos_y - self.pos_y
        delta_x = final_pos_x - self.pos_x

        if -1 < delta_y < 1 and -1 < delta_x < 1:
            return self.pos_x, self.pos_y
        else:
            angle = math.atan(numpy.abs(delta_y) / numpy.abs(delta_x))
            self.vy = math.sin(angle)
            self.vx = math.cos(angle)

        self.sign_y = -1 if delta_y < 0 else 1
        self.sign_x = -1 if delta_x < 0 else 1
        return self.pos_x + self.sign_x * self.vx, self.pos_y + self.sign_y * self.vy
