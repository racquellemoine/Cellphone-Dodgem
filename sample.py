import tkinter as tk
# import tkFont as tkfont
import time
import math
import random
import numpy as np
import constants
from players.default_player import Player as DefaultPlayer
from player_state import PlayerState

from sympy import Point, Segment

# random.seed(2)
# 
class Stall():
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

class DodgemGame(tk.Tk):
    def __init__(self, args):
        super().__init__()

        # time
        self.start_time = time.time()
        self.time_interval = 0

        # arguments
        self.no_of_stalls = args.no_of_stalls
        self.no_to_visit = args.no_to_visit
        self.max_items = args.max_items

        # stalls and obstacles
        self.stalls = []
        self.stalls_to_visit = []
        self.obstacles = []

        # player
        self.players = []
        self.player_states = []
        self.player_comp = []

        # distance
        self.dist_matrix = np.zeros((self.no_of_stalls, self.no_of_stalls))

        # travelling salesman approximation algorithm
        self.T = 100
        self.theta = 2

        self.result = open("result.txt", "w")
        self.obstacle_log = open("obstacle_log.txt", "w")
        self.item_log = open("item_log.txt", "w")

        self.check_log = open("check_log.txt", "w")

        self.stall_log = open("stall.log.txt", "w")

        self._configure_game()
        self._create_players(args.players)
        self._render_frame()
        self.bind("<KeyPress-Left>", lambda _: self._play_game())
        self.mainloop()


    def _configure_game(self):
        root = tk.Tk()
        canvas = tk.Canvas(root, height=constants.vis_height, width=constants.vis_width, bg="#263D42")

        # create stalls
        count = 0
        while count < self.no_of_stalls:
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            # avoid overlapping stalls
            while canvas.find_overlapping(x * constants.canvas_scale, y * constants.canvas_scale, \
                                        (x + constants.stall_size) * constants.canvas_scale, (y + constants.stall_size) * constants.canvas_scale) or \
                                        x > 97 or y > 97 or x < 1 or y < 1:
                x = random.uniform(0, 100)
                y = random.uniform(0, 100)
            self.stalls.append(Stall(count + 1, x + constants.stall_size / 2, y + constants.stall_size / 2))
            canvas.create_rectangle(x * constants.canvas_scale, y * constants.canvas_scale, (x + constants.stall_size) * constants.canvas_scale, (y + constants.stall_size) * constants.canvas_scale, outline="black", fill="white", width=1)
            count += 1

        # stalls to visit by players
        self.stalls_to_visit = random.sample(self.stalls, self.no_to_visit)

        for stall in self.stalls_to_visit:
            self.stall_log.write("____________________________________________________\n")
            self.stall_log.write("Stall ID: " + str(stall.id) + "\n")
            self.stall_log.write("Stall Position: (" + str(stall.x) + ", " + str(stall.y) + ")\n")
            c1x, c1y = stall.x - 1, stall.y - 1
            c2x, c2y = stall.x + 1, stall.y - 1
            c3x, c3y = stall.x + 1, stall.y + 1
            c4x, c4y = stall.x - 1, stall.y + 1
            self.stall_log.write("STALL CORNER 1: (" + str(c1x) + ", " + str(c1y) + ")\n")
            self.stall_log.write("STALL CORNER 2: (" + str(c2x) + ", " + str(c2y) + ")\n")
            self.stall_log.write("STALL CORNER 3: (" + str(c3x) + ", " + str(c3y) + ")\n")
            self.stall_log.write("STALL CORNER 4: (" + str(c4x) + ", " + str(c4y) + ")\n")
            self.stall_log.write("____________________________________________________\n")

        self.items_to_collect = []
        for i in range(self.no_to_visit):
            self.items_to_collect.append(random.randint(1, self.max_items))

        # obstacles
        self.obstacles = []
        for stall in self.stalls:
            if stall not in self.stalls_to_visit:
                self.obstacles.append(stall)

        root.destroy()

    def _create_players(self, player_names):
        no_of_players = len(player_names)

        # create randomized positions
        perimeter = 400
        mod = math.ceil(perimeter / no_of_players)
        positions = []

        for i in range(no_of_players):
            pos = mod * i + random.randint(1, mod)
            if 0 < pos <= 100:
                pos_x = 0
                pos_y = pos
            elif 100 < pos <= 200:
                pos_x = pos - 100
                pos_y = 100
            elif 200 < pos <= 300:
                pos_x = 100
                pos_y = 300 - pos
            else:
                pos_x = 400 - pos
                pos_y = 0
            positions.append([pos_x, pos_y])
        
        random.shuffle(positions)

        colors = ['yellow', 'white', 'black', 'violet', 'orange', 'gray', 'green', 'brown']

        for index, name in enumerate(player_names):
            if name == 'd':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.items_to_collect)
                player = DefaultPlayer(self.stalls_to_visit, self.items_to_collect)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '1':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.items_to_collect)
                player = DefaultPlayer(self.stalls_to_visit, self.items_to_collect)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '2':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.items_to_collect)
                player = DefaultPlayer(self.stalls_to_visit, self.items_to_collect)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '3':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.items_to_collect)
                player = DefaultPlayer(self.stalls_to_visit, self.items_to_collect)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '4':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.items_to_collect)
                player = DefaultPlayer(self.stalls_to_visit, self.items_to_collect)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '5':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.items_to_collect)
                player = DefaultPlayer(self.stalls_to_visit, self.items_to_collect)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '6':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.items_to_collect)
                player = DefaultPlayer(self.stalls_to_visit, self.items_to_collect)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '7':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.items_to_collect)
                player = DefaultPlayer(self.stalls_to_visit, self.items_to_collect)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '8':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.items_to_collect)
                player = DefaultPlayer(self.stalls_to_visit, self.items_to_collect)
                self.players.append(player)
                self.player_states.append(state)

    def _render_frame(self):
        self.canvas = tk.Canvas(self, height=constants.vis_height + 2 * constants.canvas_scale, width=constants.vis_width + 40 * constants.canvas_scale, bg="#ADD8E6")
        self.canvas.create_rectangle(1 * constants.canvas_scale, 1 * constants.canvas_scale, constants.vis_height + 1 * constants.canvas_scale, constants.vis_width + 1 * constants.canvas_scale, outline="#000000", fill="white", width=1)

        # render stalls
        for stall in self.stalls_to_visit:
            x = stall.x + 1
            y = stall.y + 1
            self.canvas.create_rectangle((x - constants.stall_size / 2) * constants.canvas_scale, (y - constants.stall_size / 2) * constants.canvas_scale, (x + constants.stall_size / 2) * constants.canvas_scale, (y + constants.stall_size / 2) * constants.canvas_scale, outline="#0e9cef", fill="#0e9cef", width=1)
            self.canvas.create_text((x) * constants.canvas_scale, (y) * constants.canvas_scale, font=('freemono', 11, 'bold'), text=stall.id)

        for stall in self.obstacles:
            x = stall.x + 1
            y = stall.y + 1
            self.canvas.create_rectangle((x - constants.stall_size / 2) * constants.canvas_scale, (y - constants.stall_size / 2) * constants.canvas_scale, (x + constants.stall_size / 2) * constants.canvas_scale, (y + constants.stall_size / 2) * constants.canvas_scale, outline="#ff9695", fill="#ff9695", width=1)
            self.canvas.create_text((x) * constants.canvas_scale, (y) * constants.canvas_scale, font=('freemono', 11, 'bold'), text=stall.id)

        for index, player_state in enumerate(self.player_states):
            x = player_state.pos_x + 1
            y = player_state.pos_y + 1
            color = player_state.color
            p = self.canvas.create_oval((x - 0.5) * constants.canvas_scale, (y - 0.5) * constants.canvas_scale, (x + 0.5) * constants.canvas_scale, (y + 0.5) * constants.canvas_scale, fill=color)
            self.player_comp.append(p)

            self.canvas.create_text((10 * index + 1) * constants.canvas_scale, (102) * constants.canvas_scale, font=('freemono', 11, 'bold'), text="Player")
        self.canvas.pack()



    def calculate_distance(self):
        # find distances between stalls
        for i in range(self.no_of_stalls):
            for j in range(self.no_of_stalls):
                self.dist_matrix[i][j] = math.sqrt((self.stalls[i].x - self.stalls[j].x)**2 + (self.stalls[i].y - self.stalls[j].y)**2)

    def compute_distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    # def intersection(self, p_x1, p_y1, p_x2, p_y2, q_x1, q_y1, q_x2, q_y2):
    #     m1 = 0
    #     m2 = 0
    #     if p_x1 == p_x2:
    #         m1 = 0
    #     elif p_y1 == p_y2:
    #         m1 = math.inf
    #     else:
    #         m1 = (p_y2 - p_y1) / (p_x2 - p_x1)

    #     if q_x1 == q_x2:
    #         m2 = 0
    #     elif q_y1 == q_y2:
    #         m2 = math.inf
    #     else:
    #         m2 = (q_y2 - q_y1) / (q_x2 - q_x1)

    #     if m1 == m2:
    #         return False
    #     else:
    #         c1 = -1 * m1 * p_x1 + p_y1
    #         c2 = -1 * m2 * q_x1 + q_y1
    #         intersect_x = (c2 - c1) / (m1 - m2)
    #         intersect_y = m1 * intersect_x + c1
    #         if((intersect_x >= p_x1 and intersect_x <= p_x2 and intersect_y >= p_y1 and intersect_y <= p_y2) or \
    #            (intersect_x >= p_x2 and intersect_x <= p_x1 and intersect_y >= p_y2 and intersect_y <= p_y1)) and \
    #           ((intersect_x >= q_x1 and intersect_x <= q_x2 and intersect_y >= q_y1 and intersect_y <= q_y2) or \
    #            (intersect_x >= q_x2 and intersect_x <= q_x1 and intersect_y >= q_y2 and intersect_y <= q_y1)) :
    #             return True
    #     return False

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

    # def intersection(self, a, b, c, d, e, f, g, h):
    #     if c == a:
    #         m1 = math.inf
    #         c1 = a
    #     elif b == d:
    #         self.check_log.write("****" + str(b) + " " + str(d) + "\n")
    #         m1 = 0
    #         c1 = b
    #     else:
    #         m1 = (d - b) / (c - a)
    #         c1 = -1 * a * m1 + b

    #     if g == e:
    #         m2 = math.inf
    #         c2 = e
    #     else:
    #         m2 = (h - f) / (g - e)
    #         c2 = -1 * e * m2 + f

    #     if m1 == 0 and m2 == 0:
    #         # Cond 1
    #         if c1 != c2:
    #             self.check_log.write("Cond 1\n")
    #             return False
    #         elif (a <= e and e <= c) or \
    #              (c <= e and e <= a) or \
    #              (a <= g and g <= c) or \
    #              (c <= g and g <= a):
    #             #  Cond 2
    #             self.check_log.write("Cond 2\n")
    #             return True
    #         else:
    #             # Cond 3
    #             self.check_log.write("Cond 3\n")
    #             return False
    #     elif m1 == math.inf and m2 == math.inf:
    #         if c1 != c2:
    #             # Cond 4
    #             self.check_log.write("Cond 4\n")
    #             return False
    #         elif (b <= f and f <= d) or \
    #              (d <= f and f <= b) or \
    #              (b <= h and h <= d) or \
    #              (d <= h and h <= b):
    #             #  Cond 5
    #             self.check_log.write("Cond 5\n")
    #             return True
    #         else:
    #             # Cond 6
    #             self.check_log.write("Cond 6\n")
    #             return False
    #     elif m1 == 0 and m2 == math.inf:
    #         # Cond 7
    #         self.check_log.write("Cond 7\n")
    #         px, py = c1, c2
    #     elif m1 == math.inf and m2 == 0:
    #         # Cond 8
    #         self.check_log.write("Cond 8\n")
    #         px, py = c2, c1
    #     elif m1 == 0:
    #         # Cond 9
    #         self.check_log.write("Cond 9: m2 = " + str(m2) + " c1 = " + str(c1) + " c2 = " + str(c2) + "\n")
    #         px, py = (c1 - c2) / m2, c1
    #     elif m1 == math.inf:
    #         # Cond 10
    #         self.check_log.write("Cond 10m2 = " + str(m2) + " c1 = " + str(c1) + " c2 = " + str(c2) + "\n")
    #         px, py =  c1, m2 * c1 + c2

    #     if ((a <= px and px <= c) or (c <= px and px <= a)) and ((b <= py and py <= d) or (d <= py and py <= b)) and \
    #        ((e <= px and px <= f) or (f <= px and px <= e)) and ((g <= py and py <= h) or (h <= py and py <= g)):
    #             # Cond 11
    #             self.check_log.write("Cond 11: (" + str(px) + ", " + str(py) + ")\n")
    #             self.check_log.write("Cond 11: (" + str(a) + ", " + str(b) + ")\n")
    #             self.check_log.write("Cond 11: (" + str(c) + ", " + str(d) + ")\n")
    #             self.check_log.write("Cond 11: (" + str(e) + ", " + str(f) + ")\n")
    #             self.check_log.write("Cond 11: (" + str(g) + ", " + str(h) + ")\n")
    #             return True
    #     else:
    #         # Cond 12
    #         self.check_log.write("Cond 12(" + str(px) + ", " + str(py) + ")\n")
    #         self.check_log.write("Cond 12: (" + str(a) + ", " + str(b) + ")\n")
    #         self.check_log.write("Cond 12: (" + str(c) + ", " + str(d) + ")\n")
    #         self.check_log.write("Cond 12: (" + str(e) + ", " + str(f) + ")\n")
    #         self.check_log.write("Cond 12: (" + str(g) + ", " + str(h) + ")\n")
    #         return False
    
    # original version
    # def check_collision_obstacle(self, stall_id, stall_x, stall_y, p_x, p_y, new_p_x, new_p_y, color):
    #     # 
    #     #                  Segment 1
    #     # 
    #     #         c1x, c1y -------- c2x, c2y
    #     #           |                   |
    #     #           |                   |
    #     # Segment 4 |      Obstacle     | Segment 2
    #     #           |                   |
    #     #           |                   |
    #     #         c4x, c4y -------- c3x, c3y
    #     # 
    #     #                  Segment 3

    #     c1x, c1y = stall_x - 1, stall_y - 1
    #     c2x, c2y = stall_x + 1, stall_y - 1
    #     c3x, c3y = stall_x + 1, stall_y + 1
    #     c4x, c4y = stall_x - 1, stall_y + 1

    #     self.check_log.write("_______________________________________________________________\n")
    #     self.check_log.write("STALL ID: " + str(stall_id) + "\n")
    #     self.check_log.write("PLAYER COLOR: " + color + "\n")
    #     self.check_log.write("PLAYER INITIAL POSITIONS: (" + str(p_x) + ", " + str(p_y) + ")\n")
    #     self.check_log.write("PLAYER FINAL POSITIONS: (" + str(new_p_x) + ", " + str(new_p_y) + ")\n")
    #     self.check_log.write("STALL CORNER 1: (" + str(c1x) + ", " + str(c1y) + ")\n")
    #     self.check_log.write("STALL CORNER 2: (" + str(c2x) + ", " + str(c2y) + ")\n")
    #     self.check_log.write("STALL CORNER 3: (" + str(c3x) + ", " + str(c3y) + ")\n")
    #     self.check_log.write("STALL CORNER 4: (" + str(c4x) + ", " + str(c4y) + ")\n")
    #     self.check_log.write(str(self.intersection(c1x, c1y, c2x, c2y, p_x, p_y, new_p_x, new_p_y)) + "\n")
    #     self.check_log.write(str(self.intersection(c2x, c2y, c3x, c3y, p_x, p_y, new_p_x, new_p_y)) + "\n")
    #     self.check_log.write(str(self.intersection(c3x, c3y, c4x, c4y, p_x, p_y, new_p_x, new_p_y)) + "\n")
    #     self.check_log.write(str(self.intersection(c4x, c4y, c1x, c1y, p_x, p_y, new_p_x, new_p_y)) + "\n")
    #     self.check_log.write("_______________________________________________________________\n\n")

    #     if self.intersection(c1x, c1y, c2x, c2y, p_x, p_y, new_p_x, new_p_y):
    #         return True
        
    #     if self.intersection(c2x, c2y, c3x, c3y, p_x, p_y, new_p_x, new_p_y):
    #         return True
        
    #     if self.intersection(c3x, c3y, c4x, c4y, p_x, p_y, new_p_x, new_p_y):
    #         return True
        
    #     if self.intersection(c4x, c4y, c1x, c1y, p_x, p_y, new_p_x, new_p_y):
    #         return True

    #     return False

    def check_collision_obstacle(self, stall_id, stall_x, stall_y, p_x, p_y, new_p_x, new_p_y, color):
        # 
        #                  Segment 1
        #                       c1x, c1y - 0.5      c2x, c2y - 0.5
        #                           |                   |
        #                           |                   |
        #    c1x - 0.5, c1y ----  c1x, c1y -------- c2x, c2y ---- c2x + 0.5, c2y
        #                   |       |                   |
        #                   |       |                   |
        #                 Segment 4 |      Obstacle     | Segment 2
        #                   |       |                   |
        #                   |       |                   |
        #     c4x - 0.5, c4y ---- c4x, c4y -------- c3x, c3y ---- c3x + 0.5, c3y
        #                           |                   |
        #                           |                   |
        #                         c4x, c4y + 0.5    c3x, c3y + 0.5
        #                  Segment 3

        c1x, c1y = stall_x - 1, stall_y - 1
        c2x, c2y = stall_x + 1, stall_y - 1
        c3x, c3y = stall_x + 1, stall_y + 1
        c4x, c4y = stall_x - 1, stall_y + 1

        self.check_log.write("_______________________________________________________________\n")
        self.check_log.write("STALL ID: " + str(stall_id) + "\n")
        self.check_log.write("PLAYER COLOR: " + color + "\n")
        self.check_log.write("PLAYER INITIAL POSITIONS: (" + str(p_x) + ", " + str(p_y) + ")\n")
        self.check_log.write("PLAYER FINAL POSITIONS: (" + str(new_p_x) + ", " + str(new_p_y) + ")\n")
        self.check_log.write("STALL CORNER 1: (" + str(c1x) + ", " + str(c1y) + ")\n")
        self.check_log.write("STALL CORNER 2: (" + str(c2x) + ", " + str(c2y) + ")\n")
        self.check_log.write("STALL CORNER 3: (" + str(c3x) + ", " + str(c3y) + ")\n")
        self.check_log.write("STALL CORNER 4: (" + str(c4x) + ", " + str(c4y) + ")\n")
        # self.check_log.write(str(self.intersection(c1x, c1y - 0.5, c2x, c2y - 0.5, p_x, p_y, new_p_x, new_p_y)) + "\n")
        # self.check_log.write(str(self.intersection(c2x + 0.5, c2y, c3x + 0.5, c3y, p_x, p_y, new_p_x, new_p_y)) + "\n")
        # self.check_log.write(str(self.intersection(c3x, c3y + 0.5, c4x, c4y + 0.5, p_x, p_y, new_p_x, new_p_y)) + "\n")
        # self.check_log.write(str(self.intersection(c4x - 0.5, c4y, c1x - 0.5, c1y, p_x, p_y, new_p_x, new_p_y)) + "\n")

        if self.intersection(c1x, c1y - 0.5, c2x, c2y - 0.5, p_x, p_y, new_p_x, new_p_y):
            return True
        self.check_log.write("--------\n")
        if self.intersection(c2x + 0.5, c2y, c3x + 0.5, c3y, p_x, p_y, new_p_x, new_p_y):
            return True
        self.check_log.write("--------\n")
        if self.intersection(c3x, c3y + 0.5, c4x, c4y + 0.5, p_x, p_y, new_p_x, new_p_y):
            return True
        self.check_log.write("--------\n")
        if self.intersection(c4x - 0.5, c4y, c1x - 0.5, c1y, p_x, p_y, new_p_x, new_p_y):
            return True
        self.check_log.write("--------\n")
        if self.check_collision(c1x, c1y, c1x, c1y, p_x, p_y, new_p_x, new_p_y):
            return True
        
        if self.check_collision(c2x, c2y, c2x, c2y, p_x, p_y, new_p_x, new_p_y):
            return True
        
        if self.check_collision(c3x, c3y, c3x, c3y, p_x, p_y, new_p_x, new_p_y):
            return True
        
        if self.check_collision(c4x, c4y, c4x, c4y, p_x, p_y, new_p_x, new_p_y):
            return True

        self.check_log.write(str(self.check_collision(c1x, c1y, c1x, c1y, p_x, p_y, new_p_x, new_p_y)) + "\n")
        self.check_log.write(str(self.check_collision(c2x, c2y, c2x, c2y, p_x, p_y, new_p_x, new_p_y)) + "\n")
        self.check_log.write(str(self.check_collision(c3x, c3y, c3x, c3y, p_x, p_y, new_p_x, new_p_y)) + "\n")
        self.check_log.write(str(self.check_collision(c4x, c4y, c4x, c4y, p_x, p_y, new_p_x, new_p_y)) + "\n")

        self.check_log.write("_______________________________________________________________\n\n")

        return False
    
    def check_inside(self, stall_x, stall_y, p_x, p_y):
        if (p_x >= stall_x - 1 and p_x <= stall_x + 1 and p_y >= stall_y - 1 and p_y <= stall_y + 1):
            return True

        if (p_x >= stall_x - 1.5 and p_x <= stall_x - 1 and p_y >= stall_y - 1 and p_y <= stall_y + 1) or \
           (p_x >= stall_x + 1 and p_x <= stall_x + 1.5 and p_y >= stall_y - 1 and p_y <= stall_y + 1) or \
           (p_x >= stall_x - 1 and p_x <= stall_x + 1 and p_y >= stall_y + 1 and p_y <= stall_y + 1.5) or \
           (p_x >= stall_x - 1 and p_x <= stall_x + 1 and p_y >= stall_y - 1.5 and p_y <= stall_y - 1) or \
           self.compute_distance(stall_x - 1, stall_y - 1, p_x, p_y) <= 0.5 or \
           self.compute_distance(stall_x - 1, stall_y + 1, p_x, p_y) <= 0.5 or \
           self.compute_distance(stall_x + 1, stall_x - 1, p_x, p_y) <= 0.5 or \
           self.compute_distance(stall_x + 1, stall_x + 1, p_x, p_y) <= 0.5:
            return True
        return False
    
    def compute_scores(self):
        pass

    def lookup(self):
        other_players, stalls = None, None
        return other_players, stalls
    
    def check_collision(self, x1, y1, new_x1, new_y1, x2, y2, new_x2, new_y2):
        vx = new_x1 - x1
        vy = new_y1 - y1
        wx = new_x2 - x2
        wy = new_y2 - y2

        A = vx**2 + wx**2 + vy**2 + wy**2 - 2*vx*wx - 2*vy*wy
        B = 2*x1*vx - 2*x2*vx - 2*x1*wx + 2*x2*wx + 2*y1*vy - 2*y2*vy - 2*y1*wy + 2*y2*wy
        C = x1**2 + x2**2 + y1**2 + y2**2 - 2*x1*x2 - 2*y1*y2 - 0.25

        D = B**2 - 4*A*C

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

            if root1 >= 0 and root1 <= 1:
                return True
            if root2 >= 0 and root2 <= 1:
                return True
            
        return False

    def _play_game(self):
        new_positions = []
        updates = []
        for index, player in enumerate(self.players):
            # get player action
            action = player.get_action(self.player_states[index].pos_x, self.player_states[index].pos_y)
            pos_x, pos_y = self.player_states[index].pos_x, self.player_states[index].pos_y

            if action == 'lookup':
                other_players, stalls = self.lookup()
                player.pass_lookup_info(other_players, stalls)
                new_positions.append([pos_x, pos_y])
                updates.append(False)

            elif action == 'move':
                if self.player_states[index].wait == 0:
                    new_pos_x, new_pos_y = player.get_next_move()
                    if self.compute_distance(pos_x, pos_y, new_pos_x, new_pos_y) <= 1.0005:
                        new_positions.append([new_pos_x, new_pos_y])
                        updates.append(True)
                    else:
                        new_positions.append([pos_x, pos_y])
                        updates.append(False)
                else:
                    self.player_states[index].wait -= 1
                    new_positions.append([pos_x, pos_y])
                    updates.append(False)
        
        # check collision with other players
        for i, player in enumerate(self.player_states):
            for j, other_player in enumerate(self.player_states):
                if i != j:
                    if self.check_collision(player.pos_x, player.pos_y, \
                                            new_positions[i][0], new_positions[i][1], \
                                            other_player.pos_x, other_player.pos_y, \
                                            new_positions[j][0], new_positions[j][1]):
                        
                        updates[i] = False
                        self.player_states[i].wait = 10
                        self.players[i].encounter_obstacle()
                        self.obstacle_log.write("Player Name: " + player.name + " Old Position: (" + str(player.pos_x) + ", " + str(player.pos_y) + ")" + \
                                                " New Position: (" + str(new_positions[i][0]) + ", " + str(new_positions[i][1]) + ")" + \
                                                " Player Encountered: " + other_player.name + " Position: (" + str(other_player.pos_x) + ", " + \
                                                str(other_player.pos_y) + ")" + " New Position: (" + str(new_positions[j][0]) + ", " + str(new_positions[j][1]) + ")\n\n")

        # check collision with obstacles
        for i, player_state in enumerate(self.player_states):
            for stall in self.obstacles:
                # if self.check_inside(stall.x, stall.y, new_positions[i][0], new_positions[i][1]):
                # if self.check_inside(stall.x, stall.y, new_positions[i][0], new_positions[i][1]) or \
                if self.check_collision_obstacle(stall.id, stall.x, stall.y, player_state.pos_x, player_state.pos_y, new_positions[i][0], new_positions[i][1], \
                                                  player_state.color):
                    updates[i] = False
                    self.player_states[i].wait = 10
                    self.players[i].encounter_obstacle()
                    self.obstacle_log.write("Player Name: " + player_state.color + " Old Position: (" + str(player_state.pos_x) + ", " + str(player_state.pos_y) + ")" + \
                                            " New Position: (" + str(new_positions[i][0]) + ", " + str(new_positions[i][1]) + ")" + \
                                            " Obstacle Encountered: " + str(stall.id) + " Position: (" + str(stall.x) + ", " + str(stall.y) + ")\n\n" )

        # update positions
        for i, update in enumerate(updates):
            if update:
                self.player_states[i].increment_interaction()
                self.player_states[i].pos_x, self.player_states[i].pos_y = new_positions[i][0], new_positions[i][1]

        for player_state in self.player_states:
            for index, stall in enumerate(self.stalls_to_visit):
                if stall.id not in player_state.visited_stalls and self.check_inside(stall.x, stall.y, player_state.pos_x, player_state.pos_y):
                    player_state.add_stall_visited(stall.id)
                    player_state.add_items(self.items_to_collect[index])

        # update player positions on game board
        for index, player_state in enumerate(self.player_states):
            self.canvas.moveto(self.player_comp[index], (player_state.pos_x + 0.5) * constants.canvas_scale, (player_state.pos_y + 0.5) * constants.canvas_scale)

        self.after(100, self._play_game)