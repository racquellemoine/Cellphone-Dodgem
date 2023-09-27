import tkinter as tk
from tkinter import *
# import tkFont as tkfont
import time
import math
import random
import numpy as np
import fast_tsp
import os

import constants
from players.default_player import Player as DefaultPlayer
from player_state import PlayerState

class Stall():
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

class DodgemGame(tk.Tk):
    def __init__(self, args):
        super().__init__()

        # seed
        random.seed(int(args.seed))

        # time
        self.start_time = time.time()
        self.iteration = 0
        self.time_interval = 0

        # arguments
        self.no_of_stalls = int(args.no_of_stalls)
        self.no_to_visit = int(args.no_to_visit)

        if self.no_to_visit > self.no_of_stalls:
            self.no_to_visit = self.no_of_stalls - 1

        # stalls and obstacles
        self.stalls = []
        self.stalls_to_visit = []
        self.obstacles = []

        # player
        self.players = []
        self.player_states = []

        # tkinter canvas components (used for updating text and color)
        self.player_comp = []
        self.score_comp = []
        self.circles = []
        self.title_comp = None
        self.header_comp = None

        # distance matrix for stalls
        self.dist_matrix = [[0] * self.no_of_stalls] * self.no_of_stalls
        # np.zeros((self.no_of_stalls, self.no_of_stalls))

        self.theta = int(args.theta)
        self.T = 0

        # log files
        self.stall_log = os.path.join("logs", "stall.txt")
        self.result_log = os.path.join("logs", "result.txt")

        with open(self.result_log, 'w') as f:
            f.write("Results\n")

        with open(self.stall_log, 'w') as f:
            f.write("Stall Info\n")
        self.turn_no = 1
        self.turn_comp = None

        self.game_state = "resume"

        self._configure_game()
        if int(args.total_time) < 0:
            self.T = self.tsp()
            self.T = self.theta * self.T
        else:
            self.T = int(args.total_time)
        
        self._create_players(args.players)
        self._render_frame()
        self.bind("<KeyPress-Left>", lambda _: self._play_game())
        self.mainloop()

    def calculate_distance(self):
        # find distances between stalls
        for i in range(self.no_to_visit):
            for j in range(self.no_to_visit):
                self.dist_matrix[i][j] = math.sqrt((self.stalls_to_visit[i].x - self.stalls_to_visit[j].x)**2 + \
                                                   (self.stalls_to_visit[i].y - self.stalls_to_visit[j].y)**2)

    def tsp(self):
        self.calculate_distance()

        # take ceil of distance values to make distances integers
        dist = [[0] * self.no_of_stalls] * self.no_of_stalls
        for i in range(self.no_of_stalls):
            for j in range(self.no_of_stalls):
                dist[i][j] = math.ceil(self.dist_matrix[i][j])
        
        # obtain tour using travelling salesman approximation algorithm
        tour = fast_tsp.find_tour(list(dist))

        # calculate path length
        path_length = 0
        for index, i in enumerate(tour):
            if index != len(tour) - 1:
                path_length += self.dist_matrix[tour[index]][tour[index + 1]]
        
        T = math.ceil(path_length)
        return T

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


        # obstacles
        self.obstacles = []
        for stall in self.stalls:
            if stall not in self.stalls_to_visit:
                self.obstacles.append(stall)

        # Log data
        with open(self.stall_log, 'a') as f:
            f.write("_"*250 + "\n\n")
            f.write("STALLS\n")
            f.write("_"*250 + "\n\n")
            f.write("Stall ID".ljust(20, " ") + "Stall Position (Center)".ljust(50, " ") + "Vertex 1 (Top Left)".ljust(50, " ") + "Vertex 2 (Top Right)".ljust(50, " ") + "Vertex 3 (Bottom Right)".ljust(50, " ") + "Vertex 4 (Bottom Left)".ljust(50, " ") + "\n")
            f.write("_"*250 + "\n\n")
            for stall in self.stalls:
                c1x, c1y = stall.x - 1, stall.y - 1
                c2x, c2y = stall.x + 1, stall.y - 1
                c3x, c3y = stall.x + 1, stall.y + 1
                c4x, c4y = stall.x - 1, stall.y + 1
                str1 = "(" + str(stall.x) + ", " + str(stall.y) + ")"
                str2 = "(" + str(c1x) + ", " + str(c1y) + ")"
                str3 = "(" + str(c2x) + ", " + str(c2y) + ")"
                str4 = "(" + str(c3x) + ", " + str(c3y) + ")"
                str5 = "(" + str(c4x) + ", " + str(c4y) + ")"
                f.write(str(stall.id).ljust(20) + str1.ljust(50, " ") + str2.ljust(50, " ") + str3.ljust(50, " ") + str4.ljust(50, " ") + str5.ljust(50, " ") + "\n")

            f.write("\n\n" + "_"*250 + "\n\n")
            f.write("STALLS TO VISIT\n")
            f.write("_"*250 + "\n\n")
            f.write("Stall ID".ljust(20, " ") + "Stall Position".ljust(50, " ") + "\n")
            f.write("_"*250 + "\n\n")
            for index, stall in enumerate(self.stalls_to_visit):
                str1 = "(" + str(stall.x) + ", " + str(stall.y) + ")"
                f.write(str(stall.id).ljust(20) + str1.ljust(50, " ") + "\n")

            
            f.write("\n\n" + "_"*250 + "\n\n")
            f.write("OBSTACLES\n")
            f.write("_"*250 + "\n\n")
            f.write("Stall ID".ljust(20, " ") + "Stall Position".ljust(50, " ") + "\n")
            f.write("_"*250 + "\n\n")
            for index, stall in enumerate(self.obstacles):
                str1 = "(" + str(stall.x) + ", " + str(stall.y) + ")"
                f.write(str(stall.id).ljust(20) + str1.ljust(50, " ") + "\n")

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
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.T)
                player = DefaultPlayer(name, self.stalls_to_visit, self.T)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '1':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.T)
                player = DefaultPlayer(name, self.stalls_to_visit, self.T)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '2':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.T)
                player = DefaultPlayer(name, self.stalls_to_visit, self.T)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '3':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.T)
                player = DefaultPlayer(name, self.stalls_to_visit, self.T)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '4':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.T)
                player = DefaultPlayer(name, self.stalls_to_visit, self.T)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '5':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.T)
                player = DefaultPlayer(name, self.stalls_to_visit, self.T)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '6':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.T)
                player = DefaultPlayer(name, self.stalls_to_visit, self.T)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '7':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.T)
                player = DefaultPlayer(name, self.stalls_to_visit, self.T)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '8':
                state = PlayerState(name, colors[index], positions[index][0], positions[index][1], self.stalls_to_visit, self.T)
                player = DefaultPlayer(name, self.stalls_to_visit, self.T)
                self.players.append(player)
                self.player_states.append(state)

    def _render_frame(self):
        self.canvas = tk.Canvas(self, height=constants.vis_height + 2 * constants.canvas_scale, width=constants.vis_width + 80 * constants.canvas_scale, bg="#ADD8E6")
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

        self.turn_comp = self.canvas.create_text((131) * constants.canvas_scale, (10) * constants.canvas_scale, anchor="nw", font=('freemono', 18, 'bold'), text="TURN: " + str(self.turn_no) + "/" + str(self.T))

        self.title_comp = self.canvas.create_text((133) * constants.canvas_scale, (15) * constants.canvas_scale, anchor="nw", font=('freemono', 18, 'bold'), text="SCORES")
        
        s1 = "Interaction"
        s2 = "Satisfaction"
        s3 = "Items"
        self.header_comp = self.canvas.create_text((110) * constants.canvas_scale, (20) * constants.canvas_scale, anchor="nw", font=('freemono', 15, 'bold'), text="             " + s3.ljust(12, " ") + s1.ljust(15, " ") + s2.ljust(15, " "))
            
            
        
        for index, player_state in enumerate(self.player_states):
            s = self.canvas.create_text((110) * constants.canvas_scale, (5 * index + 25) * constants.canvas_scale, font=('freemono', 15, 'bold'), anchor="nw", text="PLAYER " + str(index + 1) + ":    " + str(player_state.items_obtained) + "/" + str(len(self.stalls_to_visit)).ljust(12, " ") + str(player_state.interaction).ljust(15, " ") + str(round(player_state.satisfaction, 2)).ljust(15, " "))
            c = self.canvas.create_oval((107 - 0.8) * constants.canvas_scale, (5 * index + 26 - 0.8) * constants.canvas_scale, (107 + 0.2) * constants.canvas_scale, \
            (5 * index + 26 + 0.2) * constants.canvas_scale, fill=player_state.color)
            self.score_comp.append(s)
            self.circles.append(c)

        pause_btn = Button(self.canvas, width=4, height=3, bd='10', command=self.pause, font=('freemono', 13, 'bold'), text ="Pause")
        pause_btn.place(x=1250, y=700)

        resume_btn = Button(self.canvas, width=4, height=3, bd='10', command=self.resume, font=('freemono', 13, 'bold'), text ="Resume")
        resume_btn.place(x=1350, y=700)

        step_btn = Button(self.canvas, width=4, height=3, bd='10', command=self.step, font=('freemono', 13, 'bold'), text ="Step")
        step_btn.place(x=1450, y=700)
            
        self.canvas.pack()

    def resume(self):
        if self.game_state != "over":
            self.game_state = "resume"
            self.after(100, self._play_game)

    def pause(self):
        if self.game_state != "over":
            self.game_state = "pause"

    def step(self):
        if self.game_state != "over":
            self.game_state = "pause"
            self.after(100, self._play_game)

    def compute_distance(self, x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

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

        if self.intersection(c1x, c1y - 0.5, c2x, c2y - 0.5, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.intersection(c2x + 0.5, c2y, c3x + 0.5, c3y, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.intersection(c3x, c3y + 0.5, c4x, c4y + 0.5, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.intersection(c4x - 0.5, c4y, c1x - 0.5, c1y, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.check_collision(c1x, c1y, c1x, c1y, p_x, p_y, new_p_x, new_p_y):
            return True
        
        if self.check_collision(c2x, c2y, c2x, c2y, p_x, p_y, new_p_x, new_p_y):
            return True
        
        if self.check_collision(c3x, c3y, c3x, c3y, p_x, p_y, new_p_x, new_p_y):
            return True
        
        if self.check_collision(c4x, c4y, c4x, c4y, p_x, p_y, new_p_x, new_p_y):
            return True
        
        return False

    def check_visit_stall(self, stall_id, stall_x, stall_y, p_x, p_y, new_p_x, new_p_y, color):
        # 
        #                  Segment 1
        #                       c1x, c1y - 0.5      c2x, c2y - 0.5
        #                           |                   |
        #                           |                   |
        #    c1x - 0.5, c1y ----  c1x, c1y -------- c2x, c2y ---- c2x + 0.5, c2y
        #                   |       |                   |
        #                   |       |                   |
        #                 Segment 4 |        Stall      | Segment 2
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

        if self.intersection(c1x, c1y - 1, c2x, c2y - 1, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.intersection(c2x + 1, c2y, c3x + 1, c3y, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.intersection(c3x, c3y + 1, c4x, c4y + 1, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.intersection(c4x - 1, c4y, c1x - 1, c1y, p_x, p_y, new_p_x, new_p_y):
            return True
        if self.check_collision(c1x, c1y, c1x, c1y, p_x, p_y, new_p_x, new_p_y):
            return True
        
        if self.check_collision(c2x, c2y, c2x, c2y, p_x, p_y, new_p_x, new_p_y):
            return True
        
        if self.check_collision(c3x, c3y, c3x, c3y, p_x, p_y, new_p_x, new_p_y):
            return True
        
        if self.check_collision(c4x, c4y, c4x, c4y, p_x, p_y, new_p_x, new_p_y):
            return True
        
        if self.compute_distance(c1x, c1y, p_x, p_y) <= 1 or self.compute_distance(c2x, c2y, p_x, p_y) < 1 or \
            self.compute_distance(c3x, c3y, p_x, p_y) < 1 or self.compute_distance(c4x, c4y, p_x, p_y) < 1:
            return True
        
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
        results = []
        for index, player in enumerate(self.player_states):
            if player.interaction > 0:
                player.satisfaction += (player.interaction * math.log2(player.interaction))
            results.append((index + 1, player.items_obtained, player.satisfaction))

        # sort by items obtained and satisfaction
        res = sorted(results, key=lambda element: (element[1], element[2]))
        
        return res[::-1]

    def lookup(self, player):
        other_players, obstacles = [], []
        for index, player_state in enumerate(self.player_states):
            if player_state.name != player.name:
                if self.compute_distance(player_state.pos_x, player_state.pos_y, player.pos_x, player.pos_y) <= 10:
                    other_players.append((player_state.name, player_state.pos_x, player_state.pos_y))

        for index, obstacle in enumerate(self.obstacles):
            if self.compute_distance(player_state.pos_x, player_state.pos_y, obstacle.x, obstacle.y) <= 10:
                obstacles.append((obstacle.id, obstacle.x, obstacle.y))
        
        return other_players, obstacles
    
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

            if root1 > 0 and root1 <= 1:
                return True
            if root2 > 0 and root2 <= 1:
                return True
            
        return False

    def _play_game(self):
        # Check if game is over over
        if self.iteration == self.T:
            self.game_state = "over"
            scores = self.compute_scores()

            self.canvas.itemconfigure(self.title_comp, text="RESULTS")
            s1 = "Items"
            s2 = "Satisfaction"
            self.canvas.itemconfigure(self.header_comp, text="             " + s1.ljust(15, " ") + s2.ljust(12, " "))
            self.canvas.create_text((110) * constants.canvas_scale, (20) * constants.canvas_scale, anchor="nw", font=('freemono', 15, 'bold'), text="             " + s1.ljust(15, " ") + s2.ljust(15, " "))
            
            with open(self.result_log, 'a') as f:
                f.write("             " + s1.ljust(15, " ") + s2.ljust(15, " ") + "\n")

            for index, score in enumerate(scores):
                self.canvas.itemconfigure(self.score_comp[index], text="PLAYER " + str(score[0]) + ":    " + str(score[1]) + "/" + str(len(self.stalls_to_visit)).ljust(12, " ") + str(round(score[2], 2)).ljust(15, " "))
                self.canvas.itemconfigure(self.circles[index], fill=self.player_states[score[0] - 1].color)
                with open(self.result_log, 'a') as f:
                    f.write("PLAYER " + str(score[0]) + ":    " + str(score[1]) + "/" + str(len(self.stalls_to_visit)).ljust(12, " ") + str(round(score[2], 2)).ljust(15, " ") + "\n")
            
            with open(self.result_log, 'a') as f:
                f.write("Game Over!")
            return
        
        self.iteration += 1
        new_positions = []
        updates = []
        update_wait = []
        logs = []
        for index, player in enumerate(self.players):
            # get player action
            action = player.get_action(self.player_states[index].pos_x, self.player_states[index].pos_y)
            pos_x, pos_y = self.player_states[index].pos_x, self.player_states[index].pos_y

            if action == 'lookup':
                other_players, stalls = self.lookup(self.player_states[index])
                player.pass_lookup_info(other_players, stalls)
                new_positions.append([pos_x, pos_y])
                updates.append(False)
                logs.append("Lookup")

            elif action == 'move':
                if self.player_states[index].wait == 0:
                    new_pos_x, new_pos_y = player.get_next_move()
                    if self.compute_distance(pos_x, pos_y, new_pos_x, new_pos_y) <= 1.0005:
                        new_positions.append([new_pos_x, new_pos_y])
                        updates.append(True)
                        logs.append("Move to (" + str(new_pos_x) + ", " + str(new_pos_y) + ")")
                    else:
                        new_positions.append([pos_x, pos_y])
                        updates.append(False)
                        logs.append("Cannot move to (" + str(new_pos_x) + ", " + str(new_pos_y) + ") as distance > 1 unit")
                    update_wait.append(False)
                else:
                    update_wait.append(True)
                    new_positions.append([pos_x, pos_y])
                    updates.append(False)
                    logs.append("Cannot move as wait time = " + str(self.player_states[index].wait))
            # else:
            #     new_positions.append([pos_x, pos_y])
        
        # check collision with other players
        for i, player in enumerate(self.player_states):
            for j, other_player in enumerate(self.player_states):
                if i != j and player.wait == 0:
                    if self.check_collision(player.pos_x, player.pos_y, \
                                            new_positions[i][0], new_positions[i][1], \
                                            other_player.pos_x, other_player.pos_y, \
                                            new_positions[j][0], new_positions[j][1]) or \
                        self.compute_distance(new_positions[i][0], new_positions[i][1], new_positions[j][0], new_positions[j][1]) <= 0.5:
                        
                        updates[i] = False
                        self.player_states[i].wait = 10
                        if self.player_states[i].interaction > 0:
                            val = math.log2(self.player_states[i].interaction)
                            self.player_states[i].satisfaction += (self.player_states[i].interaction * val)
                        self.player_states[i].interaction = 0
                        self.players[i].encounter_obstacle()
                        logs[i] = "Collided with Player " + str(other_player.name) + ": (" + str(new_positions[i][0]) + ", " + str(new_positions[i][1]) + ")"

        # check collision with obstacles
        for i, player_state in enumerate(self.player_states):
            for stall in self.obstacles:
                collision = False
                if player_state.wait == 0 and self.check_collision_obstacle(stall.id, stall.x, stall.y, player_state.pos_x, player_state.pos_y, \
                                                                            new_positions[i][0], new_positions[i][1], player_state.color):
                    updates[i] = False
                    logs[i] = "Collided with obstacle " + str(stall.id)
                    collision = True

                if new_positions[i][0] > 100 and new_positions[i][1] > 100:
                    new_positions[i][0], new_positions[i][1] = 100, 100
                    logs[i] = "Collided with boundary"
                    collision = True
                elif new_positions[i][0] > 100:
                    new_positions[i][0] = 100
                    logs[i] = "Collided with boundary"
                    collision = True
                elif new_positions[i][1] > 100:
                    new_positions[i][1] = 100
                    logs[i] = "Collided with boundary"
                    collision = True
                elif new_positions[i][0] < 0 and new_positions[i][1] < 0:
                    new_positions[i][0], new_positions[i][1] = 0, 0
                    logs[i] = "Collided with boundary"
                    collision = True
                elif new_positions[i][0] < 0:
                    new_positions[i][0] = 0
                    logs[i] = "Collided with boundary"
                    collision = True
                elif new_positions[i][1] < 0:
                    new_positions[i][1] = 0
                    logs[i] = "Collided with boundary"
                    collision = True
                
                if collision:
                    self.player_states[i].wait = 10
                    self.players[i].encounter_obstacle()
                    if self.player_states[i].interaction > 0:
                        self.player_states[i].satisfaction += self.player_states[i].interaction * math.log2(self.player_states[i].interaction)
                    self.player_states[i].interaction = 0

        # collect items
        for i, player_state in enumerate(self.player_states):
            if updates[i]:
                for index, stall in enumerate(self.stalls_to_visit):
                    if stall.id not in player_state.visited_stalls and self.check_visit_stall(stall.id, stall.x, stall.y, player_state.pos_x, player_state.pos_y, new_positions[i][0], new_positions[i][1], \
                                                    player_state.color):
                        player_state.add_stall_visited(stall.id)
                        player_state.add_items(1)
                        if self.player_states[i].interaction > 0:
                            self.player_states[i].satisfaction += self.player_states[i].interaction * math.log2(self.player_states[i].interaction)
                        self.player_states[i].interaction = 0
                        logs[i] += " and collected 1 item"
                        

        # update positions
        for i, update in enumerate(updates):
            if update:
                self.player_states[i].increment_interaction()
                self.player_states[i].pos_x, self.player_states[i].pos_y = new_positions[i][0], new_positions[i][1]

            if update_wait[i]:
                self.player_states[i].wait -= 1
                

        # update player positions on game board
        for index, player_state in enumerate(self.player_states):
            if updates[index]:
                self.canvas.moveto(self.player_comp[index], (player_state.pos_x + 0.5) * constants.canvas_scale, (player_state.pos_y + 0.5) * constants.canvas_scale)
            self.canvas.itemconfigure(self.score_comp[index], text="PLAYER " + str(index + 1) + ":    " + str(player_state.interaction).ljust(15, " ") + str(round(player_state.satisfaction, 2)).ljust(15, " ") + str(player_state.items_obtained) + "/" + str(len(self.stalls_to_visit)).ljust(12, " "))
            with open(player_state.log, 'a') as f:
                f.write("TURN " + str(self.turn_no) + ": " + logs[index] + "\n")

        self.canvas.itemconfigure(self.turn_comp, text="TURN: " + str(self.turn_no) + "/" + str(self.T))
        self.turn_no += 1
        
        # Next turn after 100 ms
        if self.game_state == "resume":
            self.after(100, self._play_game)