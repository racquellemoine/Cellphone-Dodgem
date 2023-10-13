import math
import random
import fast_tsp
from collections import deque

import constants

random.seed(2)


class Player:
    def __init__(self, id, name, color, initial_pos_x, initial_pos_y, stalls_to_visit, T_theta, tsp_path, num_players):
        self.id = id
        self.name = name
        self.color = color
        self.pos_x = initial_pos_x
        self.pos_y = initial_pos_y
        self.stalls_to_visit = stalls_to_visit
        self.T_theta = T_theta
        self.tsp_path = tsp_path
        self.num_players = num_players

        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx ** 2)
        self.sign_x = 1
        self.sign_y = 1

        #Added functionality 
        self.distance_grid = []
        for i in range(len(stalls_to_visit) + 1):
            row = []
            for j in range(len(stalls_to_visit) + 1):
                row.append(0)

            # Add the row to the list
            self.distance_grid.append(row)
        
        self.queue = deque()
        self.set_tsp_path()
        self.set_queue()
        
        self.obstacles_list = []
        self.other_players_list = []
        self.goal_stall = None

        XDIM = constants.vis_height
        YDIM = constants.vis_width

    # simulator calls this function when the player collects an item from a stall

    def set_queue(self):
        for i in self.tsp_path[1:]:
            self.queue.append(self.stalls_to_visit[i - 1])

    def set_tsp_path(self):
        s_to_v = self.stalls_to_visit

        for i in range(len(s_to_v)):
            distance1 = math.sqrt((self.pos_x - s_to_v[i].x) ** 2 + (self.pos_y - s_to_v[i].y) ** 2)
            self.distance_grid[0][i + 1] = math.ceil(distance1)
            for j in range(len(s_to_v)):
                distance2 = math.sqrt((s_to_v[i].x - s_to_v[j].x) ** 2 + (s_to_v[i].y - s_to_v[j].y) ** 2)
                self.distance_grid[i + 1][j + 1] = math.ceil(distance2)

        self.tsp_path = fast_tsp.find_tour(self.distance_grid)
        # print("THIS IS THE PATH", self.tsp_path)

    def collect_item(self, stall_id):
        for stall in self.stalls_to_visit:
            if stall.id == stall_id:
                self.stalls_to_visit.remove(stall)
        self.goal_stall = None
        return stall_id

    def end_game_tactic(self):
        self.get_action(0,0)
    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        self.obstacles_list.append(other_players)
        self.other_players_list.append(other_players)
        return

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        # print('Encountered obstacle')
        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx ** 2)
        self.sign_x *= -1
        self.sign_y *= -1

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        
        self.pos_x = pos_x
        self.pos_y = pos_y

        return 'move'

    #########################################################

    def _normalize(self, vx, vy):
        norm = math.dist((vx, vy), (0, 0))
        return vx / norm, vy / norm

    def _bounce_off_boundaries(self, x, y):
        if x <= 0:
            self.sign_x = 1
            self.vx = random.random()
            self.vy = math.sqrt(1 - self.vx ** 2)

        if y <= 0:
            self.sign_y = 1
            self.vx = random.random()
            self.vy = math.sqrt(1 - self.vx ** 2)

        if x >= 100:
            self.sign_x = -1
            self.vx = random.random()
            self.vy = math.sqrt(1 - self.vx ** 2)

        if y >= 100:
            self.sign_y = -1
            self.vx = random.random()
            self.vy = math.sqrt(1 - self.vx ** 2)

     #########################################################
    #                  From dodgem_game.py                  #
    #########################################################

    def _intersection(self, a, b, c, d, e, f, g, h):
        s0 = [(a, b), (c, d)]
        s1 = [(e, f), (g, h)]
        dx0 = s0[1][0] - s0[0][0]
        dx1 = s1[1][0] - s1[0][0]
        dy0 = s0[1][1] - s0[0][1]
        dy1 = s1[1][1] - s1[0][1]
        p0 = dy1 * (s1[1][0] - s0[0][0]) - dx1 * (s1[1][1] - s0[0][1])
        p1 = dy1 * (s1[1][0] - s0[1][0]) - dx1 * (s1[1][1] - s0[1][1])
        p2 = dy0 * (s0[1][0] - s1[0][0]) - dx0 * (s0[1][1] - s1[0][1])
        p3 = dy0 * (s0[1][0] - s1[1][0]) - dx0 * (s0[1][1] - s1[1][1])
        return (p0 * p1 <= 0) & (p2 * p3 <= 0)

    def _check_collision(self, x1, y1, new_x1, new_y1, x2, y2, new_x2, new_y2):
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

    def _check_collision_obstacle(self, obstacle, new_point):
        obstacle_x, obstacle_y = obstacle
        p_x, p_y = self.pos_x, self.pos_y
        new_p_x, new_p_y = new_point

        c1x, c1y = obstacle_x - 1, obstacle_y - 1
        c2x, c2y = obstacle_x + 1, obstacle_y - 1
        c3x, c3y = obstacle_x + 1, obstacle_y + 1
        c4x, c4y = obstacle_x - 1, obstacle_y + 1

        if self._intersection(c1x, c1y - 0.5, c2x, c2y - 0.5, p_x, p_y, new_p_x, new_p_y):
            return True
        if self._intersection(c2x + 0.5, c2y, c3x + 0.5, c3y, p_x, p_y, new_p_x, new_p_y):
            return True
        if self._intersection(c3x, c3y + 0.5, c4x, c4y + 0.5, p_x, p_y, new_p_x, new_p_y):
            return True
        if self._intersection(c4x - 0.5, c4y, c1x - 0.5, c1y, p_x, p_y, new_p_x, new_p_y):
            return True
        if self._check_collision(c1x, c1y, c1x, c1y, p_x, p_y, new_p_x, new_p_y):
            return True

        if self._check_collision(c2x, c2y, c2x, c2y, p_x, p_y, new_p_x, new_p_y):
            return True

        if self._check_collision(c3x, c3y, c3x, c3y, p_x, p_y, new_p_x, new_p_y):
            return True

        if self._check_collision(c4x, c4y, c4x, c4y, p_x, p_y, new_p_x, new_p_y):
            return True

        return False

    #########################################################
    #                   RRT Implementation                  #
    #########################################################

    def _nearest_node(self, nodes, new_node):
        """
        Find the nearest node in our list of nodes that is closest to the new_node.
        Tie breaking: return the first node we encounter.

        Args:
            nodes - a list of nodes in the RRT
            new_node - a node generated from getNewPoint

        Returns:
            closest_node (tuple) - the node in nodes that is closest to new_node
        """

        min_dist = float('inf')
        closest_node = None
        for n in nodes:
            distance = math.dist(new_node, n)

            if distance < min_dist:
                min_dist = distance
                closest_node = n

        return closest_node

    def _get_new_point(self, XDIM, YDIM, goal):
        """
        Find a new point in space to move towards uniformally randomly,
        but with probability 0.05, sample the goal. Else, sample the space
        based on the given dimensions of the space.
        This allows us to explore the space, but also move towards the goal.

        Args:
            XDIM - constant representing the width of the game aka grid of (0,XDIM)
            YDIM - constant representing the height of the game aka grid of (0,YDIM)
            goal - node (tuple of integers) representing the location of the goal

        Returns:
            x, y (tuple) - the new point in space to move towards

        """
        # generate x and y separately
        x = random.random()
        y = random.random()

        # bias: 5% of the time. So any generated val <= 0.05 should return goal
        # else: multiply the random val by the constraint of the grid to get valid coord
        if (x <= 0.05):
            x = goal.x
        else:
            x *= XDIM

        if (y <= 0.05):
            y = goal.y
        else:
            y *= YDIM

        return x, y

    def _extend(self, current_node, new_point, delta):
        """
        Extend (by at most distance delta) in the direction of the new_point and place
        a new node there

        current_node - node from which we extend
        new_point - point in space which we are extending toward
        delta - maximum distance we extend by

        Maybe delta should be 10m given our line of sight in 1 lookup is 10m?

        Returns:
            x, y (tuple) - the new point in space to move towards
        """

        vector = [new_point[0] - current_node[0], new_point[1] - current_node[1]]
        distance = math.dist(current_node, new_point)

        # the amount we will actually extend, depending on dist vs theta
        # --> extend at MOST delta, but at least the dist between curr and new points
        # extend_amt = 0

        # using unit vector to find point in same direction
        if distance > delta:
            # only extend delta
            unit_vec = [vector[0] / distance, vector[1] / distance]
            x = current_node[0] + (unit_vec[0] * delta)
            y = current_node[1] + (unit_vec[1] * delta)

        else:
            # extend the actual distance btw current_node and new_point
            # aka, return new point
            return new_point

        return x, y

    def _is_collision_free(self, obstacles, other_players, new_point):
        """
        Iterate through the obstacles and check that our point is not colliding

        Args:
            obstacles - list of obstacles (x,y) in the game we know
            other_players - list of other players' current position (x,y)
            new_point - the point we are checking for collision

        Returns:
            Bool - True if collision free, False otherwise
        """

        for o in obstacles:
            if self._check_collision_obstacle(o, new_point):
                return False

        for p in other_players:
            if self._check_collision_obstacle(p, new_point):
                return False

        return True

    #########################################################

    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):

        # print("QUEUE LEN: ", len(self.queue))

        if self.goal_stall is None and len(self.queue) > 0:
            self.goal_stall = self.queue.popleft()
            # print(f'Goal stall is at {self.goal_stall.x}, {self.goal_stall.y}')

        if self.goal_stall:

            vx = self.goal_stall.x - self.pos_x
            vy = self.goal_stall.y - self.pos_y
            self.sign_x = 1
            self.sign_y = 1
            self.vx, self.vy = self._normalize(vx, vy)

            self._bounce_off_boundaries(self.pos_x, self.pos_y)

            new_pos_x = self.pos_x + self.sign_x * self.vx
            new_pos_y = self.pos_y + self.sign_y * self.vy

            # if self.pos_x == new_pos_x:
            #     print("X is the same")
            # if self.pos_y == new_pos_y:
            #     print("Y is the same")

            # print(f'Moving to {new_pos_x}, {new_pos_y}')
            return new_pos_x, new_pos_y

        elif self.goal_stall is None and len(self.queue) == 0:
            return self.pos_x, self.pos_y

        elif self.T_theta <= 10:
            print("End game tactic")
            self.end_game_tactic()


        # # Currently if time is less than 10 second
        # elif self.T_theta <= 10 or len(self.queue) == 0:
        #     print("End game tactic")
        #     self.end_game_tactic()

            
        # closest_stall = None
        # min_distance = float('inf')
        #
        # # if empty, stand still
        # if not self.stalls_to_visit:
        #     # get_action should be looking down at phone ('move'?)
        #     return self.pos_x, self.pos_y
        #
        # # if we have no current trajectory we're following
        # if self.goal_stall is None:
        #     for stall in self.stalls_to_visit:
        #         # distance given we only need to be 1m away from edge of stall to collect
        #         dist = math.dist((self.pos_x, self.pos_y), (stall.x + 1, stall.y + 1))
        #         if dist < min_distance:
        #             closest_stall = stall
        #             min_distance = dist
        #
        #     # print(f'Goal stall is at {closest_stall.x}, {closest_stall.y} while I am at {self.pos_x}, {self.pos_y}')
        #
        #     self.goal_stall = closest_stall
        #     dist_to_edge = min_distance
        #     # print(f'Min distance is {min_distance}')
        # else:
        #     dist_to_edge = math.dist((self.pos_x, self.pos_y), (self.goal_stall.x + 1, self.goal_stall.y + 1))
        #
        # # if we are 1m away from goal stall
        # if dist_to_edge < 1:
        #     # self.collect_item(self.goal_stall.id)
        #     print(f'Collected item from stall {self.goal_stall.id}')
        #
        #     # should be done in collect_item
        #     # self.stalls_to_visit.remove(self.goal_stall)
        #     # self.goal_stall = None
        #     return self.pos_x, self.pos_y

