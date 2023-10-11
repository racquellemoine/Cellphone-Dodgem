import math
import random
import fast_tsp
import numpy
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
        self.obstacles_loc = []
        self.original_pos_x = initial_pos_x
        self.original_pos_y = initial_pos_y

        self.turn_counter = 0
        self.collision_turn = -100

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

    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        print("eye dee", stall_id)
        print(self.path_to_follow)

        for i in range(len(self.path_to_follow)):
            posx, posy, eyedee, _ = self.path_to_follow[i]
            if stall_id == eyedee:
                self.path_to_follow.pop(i)
                break

    def populate_path(self):
        # populate the self.path_to_follow public variable

        stall_coordinates = [(stall.x, stall.y, stall.id)
                             for stall in self.stalls_to_visit]

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

        print("In pass_lookup_info function.")
        # update the information to the self.discovered_region variable

        # Imp note - since this is a small version put together in less time, I'll just assume our vision is 10x10 square as opposed to the 10 unit radius for us to see.
        visible_area_x, visible_area_y = range(-10, 11), range(-10, 11)
        for _x in visible_area_x:
            for _y in visible_area_y:
                curr_x = min(max(0, self.pos_x + _x), 100)
                curr_y = min(max(0, self.pos_y + _y), 100)
                self.discovered_region[int(curr_x)][int(curr_y)] = 1

        for obstacle in obstacles:
            print('obstacle:', obstacle)
            self.obstacles_loc.append((obstacle[1], obstacle[2]))
            self.discovered_region[int(obstacle[1])][int(obstacle[2])] = 0

    # simulator calls this function when the player encounters an obstacle

    def encounter_obstacle(self):
        # assumption is that we have already looked around and added our obstacles to the path
        # if self.pos_x

        self.obstacles_loc.append((self.pos_x, self.pos_y))
        self.just_collided += 1
        self.collision_turn = self.turn_counter

        def generate_deltas():
            delta_x = random.choice([-1, 1])
            delta_y = random.choice([-1, 1])

            delta_x += self.pos_x
            delta_y += self.pos_y

            return delta_x, delta_y

        delta_x, delta_y = generate_deltas()

        while (delta_x, delta_y) in self.obstacles_loc:
            delta_x, delta_y = generate_deltas()

        angle = math.atan(numpy.abs(delta_y)/numpy.abs(delta_x))
        delta_vy = math.sin(angle)
        delta_vx = math.cos(angle)

        if (self.pos_x, self.pos_y) in self.obstacles_loc:
            # if true, then we must move and reroute tsp after doing some exploration
            return delta_vx, delta_vy, True
        else:
            # if false, then there is a chance that we ran into a player and we may not need to reroute tsp
            return delta_vx, delta_vy, False

    # simulator calls this function to get the action 'lookup' or 'move' from the player

    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'

        self.turn_counter += 1

        self.pos_x = pos_x
        self.pos_y = pos_y
        print(f"In get_action function, <pos_x, pos_y>: <{pos_x}, {pos_y}>")
        print(self.turn_counter)

        # a function that checkes if the current position is near an undiscovered region.
        def should_lookup():
            print("should look up func.")
            # all possible 8 directions to move from the current position
            _x = [0, 1, 1,  1,  0, -1, -1, -1]
            _y = [1, 1, 0, -1, -1, -1,  0,  1]

            for x_move, y_move in zip(_x, _y):
                # Check for out of bound situations
                curr_x = max(min(pos_x + x_move, 99), 0)
                curr_y = max(min(pos_y + y_move, 99), 0)

                if self.discovered_region[int(curr_x)][int(curr_y)] == -1:
                    print(f"undiscovered location <{curr_x}, {curr_y}> found.")
                    return True  # i.e. we should look up

            # otherwise, don't look up
            return False

        # check if the current position
        # a) is not discovered yet
        if self.discovered_region[int(pos_x)][int(pos_y)] == -1:
            print(self.turn_counter, 'Lookup')
            return 'lookup'

        # b) within the already discovered region, but about to go to an undiscovered region (+- 1 units)
        elif should_lookup():
            print(self.turn_counter, 'Lookup')
            return 'lookup'
        # otherwise move
        if len(self.path_to_follow) == 0:
            print(self.turn_counter, 'move (finished)')
            return 'move'

        print(self.turn_counter, 'move')
        return 'move'

    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        if not self.path_to_follow or len(self.path_to_follow) == 0:
            return self.pos_x, self.pos_y  # No stalls to visit

        if self.turn_counter - self.collision_turn <= 11:
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

        else:
            next_stall = self.path_to_follow[0]
            target_x, target_y = next_stall[0], next_stall[1]

            dx = target_x - self.pos_x
            dy = target_y - self.pos_y
            distance_to_target = math.sqrt(dx**2 + dy**2)

            # Check for nearby obstacles and other players
            for obstacle_x, obstacle_y in self.obstacles_loc:
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

            return new_pos_x, new_pos_y
