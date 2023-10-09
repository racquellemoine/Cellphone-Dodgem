import math
import random
import fast_tsp
from collections import deque
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
        self.obstacles_list= []
        self.other_players_list= []

        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)

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
        self.goal_stall = None

        self.set_tsp_path()
        self.set_queue()

    # simulator calls this function when the player collects an item from a stall
    
    def set_queue(self):
        for i in self.tsp_path[1:]:
            self.queue.append(self.stalls_to_visit[i-1])

    def set_tsp_path(self):
        s_to_v = self.stalls_to_visit

        for i in range(len(s_to_v)):
            distance1 = math.sqrt((self.pos_x- s_to_v[i].x)**2 + (self.pos_y - s_to_v[i].y)**2)
            self.distance_grid[0][i+1] = math.ceil(distance1)
            for j in range(len(s_to_v)):
                distance2 = math.sqrt((s_to_v[i].x-s_to_v[j].x)**2 + (s_to_v[i].y - s_to_v[j].y)**2)
                self.distance_grid[i+1][j+1] = math.ceil(distance2)

        self.tsp_path = fast_tsp.find_tour(self.distance_grid)
        print("THIS IS THE PATH", self.tsp_path)

    
    def collect_item(self, stall_id):
        for stall in self.stalls_to_visit:
            if stall.id == stall_id:
                self.stalls_to_visit.remove(stall)
        
        return stall_id

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        self.obstacles_list.append(other_players)
        self.other_players_list.append(other_players)
        return

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)
        self.sign_x *= -1
        self.sign_y *= -1

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        
        self.pos_x = pos_x
        self.pos_y = pos_y
        
        return 'move'
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):

        closest_stall = None
        min_distance = float('inf')

        # if empty, stand still
        if not self.stalls_to_visit:
            # get_action should be looking down at phone ('move'?)
            return self.pos_x, self.pos_y

        # if we have no current trajectory we're following
        if self.goal_stall is None:
            for stall in self.stalls_to_visit:
                # distance given we only need to be 1m away from edge of stall to collect
                dist = math.dist((self.pos_x, self.pos_y),(stall.x + 1, stall.y + 1))
                if dist < min_distance:
                    closest_stall = stall
                    min_distance = dist

            print(f'Goal stall is at {closest_stall.x}, {closest_stall.y} while I am at {self.pos_x}, {self.pos_y}')

            self.goal_stall = closest_stall
            dist_to_edge = min_distance
            print(f'Min distance is {min_distance}')
        else:
            dist_to_edge = math.dist((self.pos_x, self.pos_y), (self.goal_stall.x + 1, self.goal_stall.y + 1))

        # if we are 1m away from goal stall
        if dist_to_edge < 1:
            # self.collect_item(self.goal_stall.id)
            print(f'Collected item from stall {self.goal_stall.id}')

            # should be done in collect_item
            self.stalls_to_visit.remove(self.goal_stall)
            self.goal_stall = None
            return self.pos_x, self.pos_y

        if self.pos_x < self.goal_stall.x:
            self.sign_x = 1
        elif self.pos_x > self.goal_stall.x:
            self.sign_x = -1
        else:
            self.sign_x = 0

        if self.pos_y < self.goal_stall.y:
            self.sign_y = 1
        elif self.pos_y > self.goal_stall.y:
            self.sign_y = -1
        else:
            self.sign_y = 0

        # boundary bounce?
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

        new_pos_x = self.pos_x + self.sign_x * self.vx
        new_pos_y = self.pos_y + self.sign_y * self.vy

        print(f'Moving to {new_pos_x}, {new_pos_y}')
        return new_pos_x, new_pos_y
