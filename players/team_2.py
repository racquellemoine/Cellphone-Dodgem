import math
import random
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
        self.return_to_og = 0
        self.original_pos_x = initial_pos_x
        self.original_pos_y = initial_pos_y

        self.turn_counter = 0

        # -1 if not discovered
        #  0 if obstacle
        #  1 if discovered
        #  2 if unvisited stalls
        #  3 if visited stalls
        self.discovered_region = [[-1]*101] * 101

        # A point in path is a 3 variable tuple that looks like (pos_x, pos_y, "stall/point")
        self.path_to_follow = [(None, None, None)] * len(self.stalls_to_visit) # cross-check this once
        populate_path()

    def populate_path():
        # populate the self.path_to_follow public variable
        pass

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
                self.discovered_region[curr_x][curr_y] = 1

        for obstacle in obstacles:
            print('obstacle:', obstacle)
            self.obstacles_loc.add((obstacle[1], obstacle[2]))
            self.discovered_region[obstacle[1]][obstacle[2]] = 0


    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        # assumption is that we have already looked around and added our obstacles to the path
        # if self.pos_x

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

                if self.discovered_region[curr_x][curr_y] == -1:
                    print(f"undiscovered location <{curr_x}, {curr_y}> found.")
                    return True # i.e. we should look up

            # otherwise, don't look up
            return False

        # check if the current position
        # a) is not discovered yet
        if self.discovered_region[pos_x][pos_y] == -1:
            print(self.turn_counter, 'Lookup')
            return 'lookup'

        # b) within the already discovered region, but about to go to an undiscovered region (+- 1 units)
        elif should_lookup():
            print(self.turn_counter, 'Lookup')
            return 'lookup'
        # otherwise move
        print(self.turn_counter, 'move')
        return 'move'

    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        new_pos_x, new_pos_y = 0, 0

        print('In the get_next_move func - ')
        print(self.tsp_path)

        def gen_new():
            pos_x, pos_y = 0, 0
            val = random.random()
            if val <= 0.25:
                pos_x, pos_y = self.pos_x + 1, self.pos_y
            elif val < 0.5:
                pos_x, pos_y = self.pos_x, self.pos_y + 1
            elif val < 0.7:
                pos_x, pos_y = self.pos_x - 1, self.pos_y
            elif val <= 0.1:
                pos_x, pos_y = self.pos_x, self.pos_y - 1
            return pos_x, pos_y

        new_pos_x, new_pos_y = gen_new()

        if ((new_pos_x, new_pos_y) in self.obstacles_loc):  # when using while, it got stuck
            new_pos_x, new_pos_y = gen_new()
        while new_pos_x < 0 or new_pos_x > 100 or new_pos_y < 0 or new_pos_y > 100:
            new_pos_x, new_pos_y = gen_new()

        return new_pos_x, new_pos_y
