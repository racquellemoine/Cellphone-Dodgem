import math
import random
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

        # array of stall ids already visited
        self.stalls_visited = []

        #storing lookup info
        self.other_players = {}
        self.obstacles = {}
        self.counter = -1

        # array of stall ids already visited
        self.stalls_visited = []
        self.edited_tsp = []
        self.last_x = 0
        self.last_y = 0
        # self.target_stall = None -> set this here so don't have to find each time

        def in_stalls_visited(self, num):
            for stall in self.stalls_to_visit:
                if stall.id == num:
                    return True
            return False

        self.edited_tsp = [x for x in self.tsp_path if in_stalls_visited(self, x)]

    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        pass

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        for player in other_players:
            #print("player:", player)
            self.other_players[player[0]] = player[1], player[2]

        for obstacle in obstacles:
            #print("obstacle:", obstacle)
            self.store_obstacles[obstacle[0]] = obstacle[1], obstacle[2]

    # simulator calls this function when the player encounters an obstacle
    # Maybe if edited and we're given the obstacle id we can add it to our database
    def encounter_obstacle(self):
        self.obstacles[self.counter] = (self.counter, self.pos_x, self.pos_y)
        self.counter -= 1
        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)
        self.sign_x *= -1
        self.sign_y *= -1

        # self.pos_x += self.sign_x * self.vx
        # self.pos_y += self.sign_y * self.vy

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        
        self.pos_x = pos_x
        self.pos_y = pos_y
        
        return 'move'
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):

        target_stall = None
        for num in self.edited_tsp:
            if num not in self.stalls_visited:
                for stall in self.stalls_to_visit:
                    if stall.id == num:
                        target_stall = stall
                        break

        same_spot = False
        if self.last_x == self.pos_x and self.last_y == self.pos_y:
            same_spot = True
        #if target_stall:
        if target_stall and not same_spot:
            delta_y = target_stall.y - self.pos_y
            delta_x = target_stall.x - self.pos_x

            # check if already hit stall -> this method needs work, not sure how to check if visited stall...
            distance_to_target = math.sqrt(delta_x**2 + delta_y**2)
            if distance_to_target < 1:
                self.stalls_visited.append(target_stall.id)

            if delta_y == 0:
                self.vy = 0
                self.vx = 1
            elif delta_x == 0:
                self.vy = 1
                self.vx = 0
            else:
                # i think this is how math works? need to double check...
                angle = math.atan(numpy.abs(delta_y)/numpy.abs(delta_x))
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
        # do random if no target stall
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

        self.last_x = self.pos_x
        self.last_y = self.pos_y
        new_pos_x = self.pos_x + self.sign_x * self.vx
        new_pos_y = self.pos_y + self.sign_y * self.vy

        return new_pos_x, new_pos_y
