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
        self.discovered_region = [[-1]*101] * 101

    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        pass

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        pass

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        self.obstacles_loc.add((self.pos_x, self.pos_y))

        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)
        self.sign_x *= -1
        self.sign_y *= -1

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'

        self.turn_counter += 1

        self.pos_x = pos_x
        self.pos_y = pos_y
        # print(f"<pos_x, pos_y>: <{pos_x}, {pos_y}>")

        # a function that checkes if the current position is near an undiscovered region.
        def should_lookup():
            # all possible 8 directions to move from the current position
            _x = [0, 1, 1,  1,  0, -1, -1, -1]
            _y = [1, 1, 0, -1, -1, -1,  0,  1]

            for x_move, y_move in zip(_x, _y):
                # Check for out of bound situations
                curr_x = min(max(pos_x + x_move, 99), 0)
                curr_y = min(max(pos_y + y_move, 99), 0)

                if self.discovered_region[curr_x][curr_y] == -1:
                    return True # i.e. we should look up

            # otherwise, don't look up
            return False

        # check if the current position
        # a) is not discovered yet
        if self.discovered_region[pos_x][pos_y] == -1:
            # print(self.turn_counter, 'Lookup')
            return 'lookup'

        # b) within the already discovered region, but about to go to an undiscovered region (+- 1 units)
        elif should_lookup():
            # print(self.turn_counter, 'Lookup')
            return 'lookup'
        # otherwise move
        # print(self.turn_counter, 'move')
        return 'move'

    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        new_pos_x, new_pos_y = 0, 0

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
