import math
import time
import random
import os

class PlayerState:
    def __init__(self, name, color, initial_pos_x, initial_pos_y, stalls_to_visit, T_theta):
        self.name = name
        self.color = color
        self.stalls_to_visit = stalls_to_visit
        self.T_theta = T_theta

        self.wait = 0

        self.pos_x = initial_pos_x
        self.pos_y = initial_pos_y

        self.players = []
        self.obstacles = []

        # to keep track if a player is already in a stall
        self.curr_stall = None

        # list of visited stalls
        self.visited_stalls = []

        # items obtained
        self.items_obtained = 0

        self.interaction = 0
        self.satisfaction = 0

        # log file
        self.log = os.path.join("logs", "player " + str(name) + ".txt")
        
        with open(self.log, 'w') as f:
            f.write("Player Moves\n")
        self.score = 0

    def start_wait(self):
        self.wait = 10
        
    def update_position(self, pos_x, pos_y):
        self.pos_x, self.pos_y = pos_x, pos_y

    def add_stall_visited(self, stall_id):
        self.visited_stalls.append(stall_id)

    def add_items(self, item):
        self.items_obtained += item

    def increment_interaction(self):
        self.interaction += 1

    def compute_satisfaction(self):
        self.satisafaction = self.interaction * math.log(self.interaction, 2)

    def look_up(self, players, obstacles):
        pass