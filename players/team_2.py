import math
import random
import fast_tsp
import numpy
import fast_tsp
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
        self.vy = math.sqrt(1 - self.vx**2)

        self.sign_x = 1
        self.sign_y = 1
        self.obstacles_loc = set()
        self.original_pos_x = initial_pos_x
        self.original_pos_y = initial_pos_y

        self.turn_counter = 0
        self.collision_turn = -100

        self.is_crowded = None
        self.to_check_crowd = None

        self.last_lookup_pos = (None, None)

        # set the lookup frequency that is dependent on the number of players in the game
        self.lookup_freq = None
        if num_players < 10:
            self.lookup_freq = 10
        elif num_players >= 10 and num_players < 15:
            self.lookup_freq = 8
        elif num_players >= 15 and num_players < 25:
            self.lookup_freq = 7
        else:
            self.lookup_freq = 5

        print("Current lookup freq is ", self.lookup_freq)

        # -1 if not discovered
        #  0 if obstacle
        #  1 if discovered
        #  2 if unvisited stalls
        #  3 if visited stalls
        self.discovered_region = [[-1]*101] * 101
        self.just_collided = 0

        # A point in path is a 3 variable tuple that looks like (pos_x, pos_y, "stall/point")
        self.path_to_follow = []
        self.populate_path()

        self.best_rest_spot = None

    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        # print("eye dee", stall_id)
        # print(self.path_to_follow)

        for i in range(len(self.path_to_follow)):
            posx, posy, eyedee, _ = self.path_to_follow[i]
            if stall_id == eyedee:
                self.path_to_follow.pop(i)
                break

    def populate_path(self):
        # populate the self.path_to_follow public variable

        stall_coordinates = [(stall.x, stall.y, stall.id)
                             for stall in self.stalls_to_visit]

        if len(self.stalls_to_visit) == 1:
            stall = self.stalls_to_visit[0]
            pos_x = stall.x
            pos_y = stall.y
            id = stall.id
            waypoint = (pos_x, pos_y, id, "stall")
            self.path_to_follow.append(waypoint)
        else:
            def compute_distance_matrix(coordinates):
                n = len(coordinates)
                matrix = [[0] * n for _ in range(n)]
                for i in range(n):
                    for j in range(n):
                        x1, y1, _ = coordinates[i]
                        x2, y2, _ = coordinates[j]
                        distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
                        matrix[i][j] = int(round(distance))
                return matrix

            distance_matrix = compute_distance_matrix(stall_coordinates)

            optimal_order = fast_tsp.find_tour(distance_matrix)

            for index in optimal_order:
                stall = self.stalls_to_visit[index]
                pos_x = stall.x
                pos_y = stall.y
                id = stall.id
                waypoint = (pos_x, pos_y, id, "stall")
                self.path_to_follow.append(waypoint)

            # Calculate the distances from the current position to each stall
            closest_stall, mindist = None, 100000
            for stall in self.path_to_follow:
                x = stall[0]
                y = stall[1]
                dist = ((self.pos_x - x) ** 2 + (self.pos_y - y) ** 2) ** 0.5

                if dist < mindist:
                    closest_stall, mindist = stall, dist

            if closest_stall:
                # Find the index of the closest stall
                closest_stall_index = self.path_to_follow.index(closest_stall)
                # Reorder the stall_coordinates to start with the closest stall
                self.path_to_follow = self.path_to_follow[closest_stall_index:] + \
                    self.path_to_follow[:closest_stall_index]

        # print()
        # print("final path", self.path_to_follow)

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function

    def pass_lookup_info(self, other_players, obstacles):

        # update the information to the self.discovered_region variable

        # Imp note - since this is a small version put together in less time, I'll just assume our vision is 10x10 square as opposed to the 10 unit radius for us to see.
        visible_area_x, visible_area_y = range(-10, 11), range(-10, 11)
        for _x in visible_area_x:
            for _y in visible_area_y:
                curr_x = min(max(0, self.pos_x + _x), 100)
                curr_y = min(max(0, self.pos_y + _y), 100)
                self.discovered_region[int(curr_x)][int(curr_y)] = 1

        for obstacle in obstacles:
            self.obstacles_loc.add((obstacle[1], obstacle[2], obstacle[0]))
            self.discovered_region[int(obstacle[1])][int(obstacle[2])] = 0

        if self.to_check_crowd:
            if len(obstacles) > 3:
                self.is_crowded = True
            else:
                self.is_crowded = False
            self.to_check_crowd = False

    # simulator calls this function when the player encounters an obstacle

    def encounter_obstacle(self):
        # assumption is that we have already looked around and added our obstacles to the path
        # if self.pos_x

        # self.obstacles_loc.append((self.pos_x, self.pos_y))
        self.just_collided += 1
        self.collision_turn = self.turn_counter

    # simulator calls this function to get the action 'lookup' or 'move' from the player

    # version 2 of the function
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'

        self.turn_counter += 1

        self.pos_x = pos_x
        self.pos_y = pos_y
        # print(f"In get_action function, <pos_x, pos_y>: <{pos_x}, {pos_y}>")
        # print(self.turn_counter)

        # a function that checkes if the current position is near an undiscovered region.
        def get_manhattan_dist(a, b):
            # a and b both are two dimensional vectors describing the positions of two points for which the distance is required
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        # check if the current position
        # a) is not discovered yet
        if self.discovered_region[int(pos_x)][int(pos_y)] == -1:
            print(self.turn_counter, 'Lookup - new area')
            self.last_lookup_pos = (self.pos_x, self.pos_y)
            return 'lookup'

        # otherwise, check the distance between current and previous lookup position. if it is over a threshold, then lookup, otherwise move
        elif get_manhattan_dist((pos_x, pos_y), self.last_lookup_pos) > self.lookup_freq:
            self.last_lookup_pos = (self.pos_x, self.pos_y)
            print(self.turn_counter, 'Lookup - further than last lookup')
            return 'lookup'

        elif self.to_check_crowd == None:
            self.to_check_crowd = True
            return 'lookup'
        # otherwise move
        else:
            print(self.turn_counter, 'move')
            return 'move'

    def get_best_resting_spot(self):

        def get_score(x, y):
            _x = [0, 1, 1,  1,  0, -1, -1, -1]
            _y = [1, 1, 0, -1, -1, -1,  0,  1]

            score = 0
            for mv_y in _y:
                if y + mv_y > 100 or y + mv_y < 1:
                    continue
                for mv_x in _x:
                    if x + mv_x > 100 or x + mv_x < 1:
                        continue
                    if self.discovered_region[x + mv_x][y + mv_y] == 1:
                        score += 1
                    elif self.discovered_region[x + mv_x][y + mv_y] == 0:
                        score += -1
                    elif self.discovered_region[x + mv_x][y + mv_y] == 2 or self.discovered_region[x + mv_x][y + mv_y] == 3:
                        score += -3
                    else:
                        score += 0

            return score

        best_score = -1000
        best_pos = (-1, -1)
        for i in range(1, 101):
            for j in range(1, 101):
                curr_score = get_score(i, j)
                if curr_score > best_score:
                    best_score = curr_score
                    best_pos = (i, j)

        best_pos_bag = []
        for i in range(1, 101):
            for j in range(1, 101):
                curr_score = get_score(i, j)
                if curr_score == best_score:
                    best_pos_bag.append((i, j))
        return random.choice(best_pos_bag)

    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        if not self.path_to_follow or len(self.path_to_follow) == 0:
            if not self.is_crowded and not self.best_rest_spot is None:
                self.best_rest_spot = self.get_best_resting_spot()
                # add this to the path to follow, so that the subsequent function can make use of this function
                print("best resting spot added! Spot is",
                      self.best_rest_spot)
                self.path_to_follow.append(
                    [self.best_rest_spot[0], self.best_rest_spot[1], -1, "rest point"])
            else:
                return self.pos_x, self.pos_y  # No stalls to visit

        def check_collision_obstacle(stall_x, stall_y, p_x, p_y, new_p_x, new_p_y):
            def intersection(a, b, c, d, e, f, g, h):
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
                return (p0*p1 <= 0) & (p2*p3 <= 0)

            def check_collision(x1, y1, new_x1, new_y1, x2, y2, new_x2, new_y2):
                def distance(x, y, new_x, new_y):
                    dx = new_x - x
                    dy = new_y - y
                    return dx, dy

                def dot_product(dx1, dy1, dx2, dy2):
                    return dx1 * dx2 + dy1 * dy2

                dx1, dy1 = distance(x1, y1, new_x1, new_y1)
                dx2, dy2 = distance(x2, y2, new_x2, new_y2)

                A = dot_product(dx1, dx1, dx2, dx2) + dot_product(dy1,
                                                                  dy1, dy2, dy2) - 2 * dot_product(dx1, dx2, dy1, dy2)
                B = 2 * (x1 * dx1 - x2 * dx1 - x1 * dx2 + x2 * dx2 +
                         y1 * dy1 - y2 * dy1 - y1 * dy2 + y2 * dy2)
                C = x1 * x1 + x2 * x2 + y1 * y1 + y2 * y2 - 2 * x1 * x2 - 2 * y1 * y2 - 0.25

                D = B * B - 4 * A * C

                if A == 0:
                    if B == 0:
                        return C == 0
                    root = (-C) / B
                    return 0 <= root <= 1

                if D < 0:
                    return False

                if D == 0:
                    root = (-B) / (2 * A)
                    return 0 <= root <= 1

                if D > 0:
                    root1 = (-B + math.sqrt(D)) / (2 * A)
                    root2 = (-B - math.sqrt(D)) / (2 * A)

                    return (0 <= root1 <= 1) or (0 <= root2 <= 1)

                return False

            corners = [
                (stall_x - 1, stall_y - 1),
                (stall_x + 1, stall_y - 1),
                (stall_x + 1, stall_y + 1),
                (stall_x - 1, stall_y + 1)
            ]

            for (x1, y1), (x2, y2) in zip(corners, corners[1:] + [corners[0]]):
                if intersection(x1, y1 - 0.5, x2, y2 - 0.5, p_x, p_y, new_p_x, new_p_y):
                    return True
                if check_collision(x1, y1, x1, y1, p_x, p_y, new_p_x, new_p_y):
                    return True

            return False

        def will_collide(new_x, new_y):
            # Make a copy of the obstacles set
            obstacles_copy = set(self.obstacles_loc)
            for x, y, n in list(obstacles_copy):
                if check_collision_obstacle(x, y, self.pos_x, self.pos_y, new_x, new_y):
                    return True

            return False

        def gen_rand_point():
            # Generate random velocity components
            random_angle = random.uniform(0, 2 * math.pi)
            self.vx = math.cos(random_angle)
            self.vy = math.sin(random_angle)

            # Calculate the new position
            new_pos_x = self.pos_x + self.vx
            new_pos_y = self.pos_y + self.vy

            # Ensure that the velocity is within bounds
            max_speed = 1.0  # Maximum speed is 1 m/s
            norm = math.sqrt(self.vx**2 + self.vy**2)
            if norm > max_speed:
                self.vx = max_speed * self.vx / norm
                self.vy = max_speed * self.vy / norm

            # Check if the new position is within bounds (0-100)
            new_pos_x = max(min(new_pos_x, 100), 0)
            new_pos_y = max(min(new_pos_y, 100), 0)

            return new_pos_x, new_pos_y

        if self.turn_counter - self.collision_turn <= 11:

            new_pos_x, new_pos_y = gen_rand_point()

        else:
            next_stall = self.path_to_follow[0]
            target_x, target_y = next_stall[0], next_stall[1]

            dx = target_x - self.pos_x
            dy = target_y - self.pos_y
            distance_to_target = math.sqrt(dx**2 + dy**2)

            # Check for nearby obstacles and other players
            for obstacle_x, obstacle_y, _ in list(self.obstacles_loc):
                obstacle_distance = math.sqrt(
                    (obstacle_x - self.pos_x)**2 + (obstacle_y - self.pos_y)**2)
                if obstacle_distance < 0.5:
                    # If too close to an obstacle, adjust direction to avoid it
                    dx += (self.pos_x - obstacle_x)
                    dy += (self.pos_y - obstacle_y)

            if distance_to_target < 0.5:
                # Calculate new velocity components
                # If already close to the target stall, stop and remove it from the list
                self.path_to_follow.pop(0)
                self.vx, self.vy = 0, 0
            else:
                # Calculate the new direction
                norm = math.sqrt(dx**2 + dy**2)
                self.vx = dx / norm
                self.vy = dy / norm

            # Ensure that the velocity is within bounds
            max_speed = 1.0  # Maximum speed is 1 m/s
            if math.sqrt(self.vx**2 + self.vy**2) > max_speed:
                self.vx = max_speed * self.vx / norm
                self.vy = max_speed * self.vy / norm

            # Calculate the new position
            new_pos_x = self.pos_x + self.vx
            new_pos_y = self.pos_y + self.vy

            # Check if the new position is within bounds (0-100)
            new_pos_x = max(min(new_pos_x, 100), 0)
            new_pos_y = max(min(new_pos_y, 100), 0)

        if len(list(self.obstacles_loc)) != 0:
            while will_collide(new_pos_x, new_pos_y):
                new_pos_x, new_pos_y = gen_rand_point()

        return new_pos_x, new_pos_y
