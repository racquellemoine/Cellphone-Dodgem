import math
import random
import fast_tsp
from collections import deque
from datetime import timedelta, datetime

random.seed(2)

# Constants
MAX_SECS = 0.5


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
        self.end_game = False

        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx ** 2)
        self.sign_x = 1
        self.sign_y = 1

        # Added functionality
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
        self.other_players_dict = {}
        self.field_vision = []

        self.XDIM = 100  # constants.vis_height
        self.YDIM = 100  # constants.vis_width
        self.DELTA = 10  # temp, bc we can only move 1m per turn?
        self.max_time = timedelta(seconds=MAX_SECS)
        self.WIN_RADIUS = 2  # temp, but bc stall is 2x2 and we have 1m border around
        self.LOOKUP_RADIUS = 10
        # self.start_node = self.pos_x, self.pos_y

        self.goal_stall = None
        self.is_rrt_planning = False
        self.rrt_tree = []
        self.collided = False

        self.collision_counter = 0
        self.stuck_counter = 0
        self.backward_steps = 2
        self.last_moves = []

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
        if stall_id == self.queue[0].id:
            self.queue.popleft()
            self.goal_stall = None
        else:
            # do this because what if we by accident collect something along the way?
            # IF goal_stall.id == stall_id, then set None, else, we still need the curr traj
            for stall in self.queue:
                if stall.id == stall_id:
                    print("Collected: ", stall.id)
                    self.queue.remove(stall)
                    break

    def pass_lookup_info(self, other_players, obstacles):
        """
        Simulator calls this function when it passes the lookup information.
        This function is called if the player returns 'lookup' as the action in the get_action function

        Args:
            other_players - list of other players' current position tuples (ID, x,y)
            obstacles - list of obstacle tuples (ID, x,y) in the game we know

        """
        for obstacle in obstacles:
            # print(f'adding obstacle to list {obstacle}')
            if obstacle not in self.obstacles_list:
                self.obstacles_list.append(obstacle)

        # set the dict value based on the player IDs of ONLY players we currently see
        ## UPDATE THE DICT ONLY BASED ON WHO WE SEE IN OUR FIELD OF VISION, i.e. THE ONLY THREATS
        current_players = {}
        for player in other_players:
            player_id, x, y = player
            current_players[player_id] = (x, y)
        self.other_players_dict = current_players

        #BEFORE:::
        # for player in other_players:
        #     self.other_players_dict[player[0]] = (player[1], player[2])

        return

    def emergency_exit(self):

        if len(self.field_vision) >= 10:
            # print("FIELD", self.field_vision)

            print("EMERGENCY EXIT")
            self.queue.append(self.goal_stall)
            self.queue.popleft()
            # if len(self.queue) > 3:
            #     self.goal_stall = self.queue[2]
            # else:
            self.goal_stall = self.queue[0]

        self.field_vision = []

        return

    def stuck_exit(self):
        self.queue.append(self.goal_stall)
        self.queue.popleft()
        self.goal_stall = self.queue[0]
        self.stuck_counter = 0


    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        print('ENCOUNTER OBSTACLE')

        self.collided = True
        self.collision_counter += 1
        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx ** 2)
        self.sign_x *= -1
        self.sign_y *= -1

        #TODO: keep this here?
        self._bounce_off_boundaries(self.pos_x, self.pos_y)

    # simulator calls this function to get the action 'lookup', 'move', or 'lookup move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        # end game

        if len(self.queue) == 0 or self.T_theta <= 10:
            # if not self.end_game:
            #     print("END GAME")
            #     self.pos_x = pos_x - 2
            #     self.pos_y = pos_y - 2
            #     self.end_game = True
            if self.end_game:
                # Move backward for 'backward_steps' steps
                if self.backward_steps > 0:
                    #GO LEFT based on current velocity. Just switch x sign
                    self.sign_x *= -1
                    self.sign_y = 1
                else:
                    self.end_game = False
            return 'move'

        self.pos_x = pos_x
        self.pos_y = pos_y
        # lookup whole time during game
        return 'lookup move'

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
        # print(f'CHECK obstacle {obstacle} new point {new_point}')

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

    # def _win_condition(self, new_node, goal_point):
    #     """
    #     Check if the new_node is within WIN_RADIUS of the goal_stall
    #
    #     Args:
    #         new_node - the node we are checking
    #         goal_stall - the stall we are trying to reach
    #
    #     Returns:
    #         Bool - True if new_node is within WIN_RADIUS of goal_stall, False otherwise
    #     """
    #
    #     if math.dist(new_node, (goal_point[0], goal_point[1])) <= self.WIN_RADIUS:
    #         return True
    #     return False

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
            goal - tuple (x,y) representing the location of the goal

        Returns:
            x, y (tuple) - the new point in space to move towards

        """

        goal_x, goal_y = goal[0], goal[1]
        # generate x and y separately
        x = random.random()
        y = random.random()

        # bias: 5% of the time. So any generated val <= 0.05 should return goal
        # else: multiply the random val by the constraint of the grid to get valid coord

        if (x <= 0.05):
            x = goal_x
        else:
            x *= XDIM

        if (y <= 0.05):
            y = goal_y
        else:
            y *= YDIM

        # print(x, y)
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

        vx = new_point[0] - current_node[0]
        vy = new_point[1] - current_node[1]
        self.sign_x = 1
        self.sign_y = 1
        self.vx, self.vy = self._normalize(vx, vy)

        self._bounce_off_boundaries(self.pos_x, self.pos_y)

        new_pos_x = self.pos_x + self.sign_x * self.vx
        new_pos_y = self.pos_y + self.sign_y * self.vy

        return new_pos_x, new_pos_y

    def _is_collision_free(self, obstacles, other_players, new_point):
        """
        Iterate through the obstacles and check that our point is not colliding.
        If there are no obstacles/players we detected, then we are collision free.

        Args:
            obstacles - list of obstacle tuples (ID, x,y) in the game we know
            other_players - dict of other players' current position, i.e. ID: (x,y)
            new_point - the point we are checking for collision

        Returns:
            Bool - True if collision free, False otherwise
        """

        # print(f'obs {obstacles} players {other_players} new point {new_point}')

        # Point is outside the grid boundaries
        # new_x, new_y = new_point
        # if new_x < 0 or new_x > self.XDIM or new_y < 0 or new_y > self.YDIM:
        #     return False

        for o in obstacles:
            if len(o) > 0:
                obstacle_coords = o[1], o[2]
                if self._check_collision_obstacle(obstacle_coords, new_point):
                    self.field_vision.append(o)
                    return False

        for player_id in other_players.keys():
            # if len(p) > 0:
            player_coords = other_players[player_id]
            if self._check_collision_obstacle(player_coords, new_point):
                # APPENDING TUPLE IN EXPECTED FORMAT
                #TODO PLEASE CHANGE IF NEEDED FOR CLARITY
                self.field_vision.append((player_id, player_coords[0], player_coords[1]))
                return False

        return True

    #########################################################

    def _get_next_tsp_node(self):
        """
        Get the next node in the tsp path and set it as the goal stall.
        We do not pop it from the queue until we collect it.

        Call emergency exit to detect if we should get a different goal stall
        based on high traffic.
        """
        if len(self.queue) > 0:
            # don't pop until we collect it!
            self.goal_stall = self.queue[0]
            # self.emergency_exit()

    #########################################################

    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):

        # we want to calculate the expected trajectory between current position and goal stall
        # if we detect an obstacle or player in our path, we want to use RRT to plan a path around it
        # if we don't detect anything, we want to move directly to the goal stall

        # if self.goal_stall.id == 34 or self.goal_stall == 94:
        #     print(f'Goal stall {self.goal_stall.id}')
        #     print(f'Player {self.id} at {self.pos_x}, {self.pos_y}')
        #     # print everything from the queue so we see the ID and not the object
        #     for stall in self.queue:
        #         print(f'Queue: {stall.id}')
        #
        #     print("queue done")


        # curr_pos_x, curr_pos_y = self.pos_x, self.pos_y

        # if we just start or when we finish collecting an item
        if self.goal_stall is None and len(self.queue) > 0:
            self._get_next_tsp_node()
            # print(f'AFTER getting next node Q={self.queue}')
            # # print(f'Goal stall is at {self.goal_stall.x}, {self.goal_stall.y}')

        if self.goal_stall:

            # we compare the distance btw 5th last visited position and current position
            if len(self.last_moves) == 5:
                check_all = True
                for move in self.last_moves:
                    print(f'DIST {math.dist((self.pos_x, self.pos_y), move)}')
                    if math.dist((self.pos_x, self.pos_y), move) > 2:
                        check_all = False

                if check_all:
                    print("STUCK")
                    self.stuck_counter += 1

                # reset
                self.last_moves = []

            if self.stuck_counter >= 2:
                print("CALLING STUCK EXIT")

                if len(self.queue) == 1:

                    print("STUCK BEFORE LAST STALL")
                    #RANDOM TRAJECTORY
                    self.vx = random.random()
                    self.vy = math.sqrt(1 - self.vx ** 2)
                    self.sign_x *= 1 #-1
                    self.sign_y *= 1

                    self._bounce_off_boundaries(self.pos_x, self.pos_y)

                    new_pos_x = self.pos_x + self.sign_x * self.vx
                    new_pos_y = self.pos_y + self.sign_y * self.vy

                    self.stuck_counter = 0


                    self.last_moves.append((new_pos_x, new_pos_y))
                    return new_pos_x, new_pos_y

                else:
                    self.stuck_exit()

            if self.collision_counter >= 3:
                # print(f'COLLISION COUNT {self.collision_counter}')

                # RANDOM COLLISION TRAJECTORY ALREADY CALCULATED IN ENCOUNTER OBSTACLE FXN

                # self.vx = random.random()
                # self.vy = math.sqrt(1 - self.vx ** 2)
                # self.sign_x *= -1
                # self.sign_y *= -1

                self._bounce_off_boundaries(self.pos_x, self.pos_y)

                new_pos_x = self.pos_x + self.sign_x * self.vx
                new_pos_y = self.pos_y + self.sign_y * self.vy
                self.collision_counter = 0

                self.last_moves.append((new_pos_x, new_pos_y))
                return new_pos_x, new_pos_y



            goal_point = self.goal_stall.x, self.goal_stall.y

            if self._is_collision_free(self.obstacles_list, self.other_players_dict, goal_point):
                vx = self.goal_stall.x - self.pos_x
                vy = self.goal_stall.y - self.pos_y
                self.sign_x = 1
                self.sign_y = 1
                self.vx, self.vy = self._normalize(vx, vy)

                self._bounce_off_boundaries(self.pos_x, self.pos_y)

                new_pos_x = self.pos_x + self.sign_x * self.vx
                new_pos_y = self.pos_y + self.sign_y * self.vy

                # print(f'Moving to {new_pos_x}, {new_pos_y}')
                print("No obstacles in the way, moving directly to goal stall")

                self.last_moves.append((new_pos_x, new_pos_y))
                return new_pos_x, new_pos_y
            else:
                # print("Obstacle detected, planning with RRT")

                self.emergency_exit()


                #TODO. (did), but just using self.pos_x, self.pos_y instead of curr bc it's same thing
                self.rrt_tree = [(self.pos_x, self.pos_y)]  # Initialize the RRT tree with the start node
                #  print("This is the start node ", self.start_node)
                # explore until new point is collision free or until 1 second has passed
                begin = datetime.utcnow()
                while datetime.utcnow() - begin < self.max_time:
                    # print("This is ", datetime.utcnow(), begin, self.max_time)
                    new_point = self._get_new_point(self.XDIM, self.YDIM, goal_point)
                    if self._is_collision_free(self.obstacles_list, self.other_players_dict, new_point):
                        break

                #TODO --- the rrt tree
                # closest_node = self._nearest_node(self.rrt_tree, new_point)
                # print("Closest ", closest_node, " Tree ", self.rrt_tree, " New point ", new_point, "Current pos ", self.pos_x, self.pos_y)

                new_node = self._extend((self.pos_x, self.pos_y), new_point, self.DELTA)
                # print("This is the new node ", new_node)

                # TODO CHANGE FROM obstacles list to field vision. aka anything we're going to collide with??
                if self._is_collision_free(self.obstacles_list, self.other_players_dict, new_node):
                    # print(f'extending to new node {new_node}')
                    # print(f'DISTANCE CURR-NEW NODE {math.dist(self.start_node, new_node)}')
                    self.rrt_tree.append(new_node)
                    # self._bounce_off_boundaries(self.pos_x, self.pos_y)

                    new_pos_x, new_pos_y = new_node
                    # print("This is x, y ", new_pos_x, new_pos_y)
                    print("Returning new node from RRT")

                    self.last_moves.append((new_pos_x, new_pos_y))
                    return new_pos_x, new_pos_y
                else:
                    # TODO: WHAT ELSE DO WE DO WHEN WE ACTUALLY JUST HAD A COLLISION? HOW DO WE MOVE?
                    print("Collision detected while extending RRT tree")

                    self.vx = random.random()
                    # print("This is the unit vector", self.vx)
                    self.vy = math.sqrt(1 - self.vx ** 2)
                    self.sign_x *= -1
                    self.sign_y *= -1

                    self._bounce_off_boundaries(self.pos_x, self.pos_y)

                    new_pos_x = self.pos_x + self.sign_x * self.vx
                    new_pos_y = self.pos_y + self.sign_y * self.vy

                    self.last_moves.append((new_pos_x, new_pos_y))
                    return new_pos_x, new_pos_y

        elif self.goal_stall is None and len(self.queue) == 0:
            # endgame, step to the left of the stall
            if not self.end_game and self.backward_steps > 0:
                self.end_game = True
                # print("not yet end game amd backward steps > 0")
                return self.pos_x, self.pos_y

            elif self.backward_steps == 0:
                # print("end game and backward steps == 0")
                return self.pos_x, self.pos_y

            elif self.end_game and self.backward_steps > 0:
                self.backward_steps -= 1
                # print(f'No more stalls to visit, move out of way {self.backward_steps} steps left')
                self._bounce_off_boundaries(self.pos_x, self.pos_y)
                new_pos_x = self.pos_x + self.sign_x * self.vx
                new_pos_y = self.pos_y + self.sign_y * self.vy
                return new_pos_x, new_pos_y
