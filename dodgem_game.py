import tkinter as tk
from tkinter import *
import time
import math
import random
import os
import shutil
import Pmw
import fast_tsp

import constants
from players.default_player import Player as DefaultPlayer
from players.team_1 import Player as Player1
from players.team_2 import Player as Player2
from players.team_3 import Player as Player3
from players.team_4 import Player as Player4
from players.default_player import Player as Player5
from players.team_6 import Player as Player6
from player_state import PlayerState


class Stall():
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y


class DodgemGame(tk.Tk):
    def __init__(self, args):
        if args.disable_tsp == "False" or args.disable_tsp == "false":
            import fast_tsp

        super().__init__()

        shutil.rmtree('logs')
        os.mkdir("logs")

        # checks
        if args.gui == "False" or args.gui == "false":
            self.gui = False
        elif args.gui == "True" or args.gui == "true":
            self.gui = True
        else:
            print("ERROR: Enter a valid gui argument (True/False)")
            return

        if int(args.no_of_stalls) <= 0:
            print("ERROR: Number of stalls has to be greater than 0")
            return

        if int(args.no_to_visit) <= 0:
            print("ERROR: Number of stalls to visit has to be greater than 0")
            return
        elif int(args.no_to_visit) > int(args.no_of_stalls):
            print(
                "ERROR: Number of stalls to visit has to be lesser than the total number of stalls")
            return

        # seed
        random.seed(int(args.seed))

        # time
        self.iteration = 0

        # arguments
        self.no_of_stalls = int(args.no_of_stalls)
        self.no_to_visit = int(args.no_to_visit)
        self.interval = int(args.interval)

        # stalls and obstacles
        self.stalls = []
        self.stalls_to_visit = []
        self.obstacles = []

        # player
        self.players = []
        self.player_states = []
        self.num_players = len(args.players)

        # tkinter canvas components (used for updating text and color)
        self.player_comp = []
        self.score_comp = []
        self.circles = []
        self.title_comp = None
        self.header_comp = None

        # distance matrix for stalls
        self.dist_matrix = [[0] * self.no_of_stalls] * self.no_of_stalls

        self.theta = int(args.theta)
        self.T = 0

        # log files
        self.stall_log = os.path.join("logs", "stall.txt")
        self.result_log = os.path.join("logs", "result.txt")
        self.score_log = os.path.join("logs", "score.txt")
        self.tsp_log = os.path.join("logs", "tsp.txt")

        self.canvas_scale = int(math.floor(float(args.scale)))
        self.canvas_height = 100 * self.canvas_scale
        self.canvas_width = 100 * self.canvas_scale

        with open(self.result_log, 'w') as f:
            f.write("Results\n")

        with open(self.stall_log, 'w') as f:
            f.write("Stall Info\n")

        with open(self.score_log, 'w') as f:
            f.write("Score Info\n")

        with open(self.tsp_log, 'w') as f:
            f.write("Travelling Salesman Path\n")

        self.turn_no = 1
        self.turn_comp = None

        self.game_state = "resume"

        self._configure_game()
        if args.disable_tsp == "False" or args.disable_tsp == "false":
            self.T, self.tsp_path = self.tsp()
        else:
            self.T, self.tsp_path = 10000, []

        # handle edge case
        if self.T <= 0:
            self.T = 1000

        with open(self.tsp_log, 'a') as f:
            f.write(str(self.tsp_path))

        self.T = self.theta * self.T

        if int(args.total_time) > 0:
            self.T = int(args.total_time)

        self._create_players(args.players)
        if self.gui:
            self._render_frame()
            self.mainloop()
        else:
            self._play_game()

    def calculate_distance(self):
        # find distances between stalls
        for i in range(self.no_to_visit):
            for j in range(self.no_to_visit):
                self.dist_matrix[i][j] = math.sqrt((self.stalls_to_visit[i].x - self.stalls_to_visit[j].x)**2 +
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
        return T, tour

    def _configure_game(self):
        root = tk.Tk()
        canvas = tk.Canvas(root, height=constants.vis_height,
                           width=constants.vis_width, bg="#263D42")

        # create stalls
        count = 0
        while count < self.no_of_stalls:
            x = random.uniform(0, 100)
            y = random.uniform(0, 100)
            # avoid overlapping stalls
            while canvas.find_overlapping(x * self.canvas_scale, y * self.canvas_scale,
                                          (x + constants.stall_size) * self.canvas_scale, (y + constants.stall_size) * self.canvas_scale) or \
                    x > 97 or y > 97 or x < 1 or y < 1:
                x = random.uniform(0, 100)
                y = random.uniform(0, 100)
            self.stalls.append(
                Stall(count + 1, x + constants.stall_size / 2, y + constants.stall_size / 2))
            canvas.create_rectangle(x * self.canvas_scale, y * self.canvas_scale, (x + constants.stall_size) *
                                    self.canvas_scale, (y + constants.stall_size) * self.canvas_scale, outline="black", fill="white", width=1)
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
            f.write("Stall ID".ljust(20, " ") + "Stall Position (Center)".ljust(50, " ") + "Vertex 1 (Top Left)".ljust(50, " ") +
                    "Vertex 2 (Top Right)".ljust(50, " ") + "Vertex 3 (Bottom Right)".ljust(50, " ") + "Vertex 4 (Bottom Left)".ljust(50, " ") + "\n")
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
                f.write(str(stall.id).ljust(20) + str1.ljust(50, " ") + str2.ljust(50, " ") +
                        str3.ljust(50, " ") + str4.ljust(50, " ") + str5.ljust(50, " ") + "\n")

            f.write("\n\n" + "_"*250 + "\n\n")
            f.write("STALLS TO VISIT\n")
            f.write("_"*250 + "\n\n")
            f.write("Stall ID".ljust(20, " ") +
                    "Stall Position".ljust(50, " ") + "\n")
            f.write("_"*250 + "\n\n")
            for index, stall in enumerate(self.stalls_to_visit):
                str1 = "(" + str(stall.x) + ", " + str(stall.y) + ")"
                f.write(str(stall.id).ljust(20) + str1.ljust(50, " ") + "\n")

            f.write("\n\n" + "_"*250 + "\n\n")
            f.write("OBSTACLES\n")
            f.write("_"*250 + "\n\n")
            f.write("Stall ID".ljust(20, " ") +
                    "Stall Position".ljust(50, " ") + "\n")
            f.write("_"*250 + "\n\n")
            for index, stall in enumerate(self.obstacles):
                str1 = "(" + str(stall.x) + ", " + str(stall.y) + ")"
                f.write(str(stall.id).ljust(20) + str1.ljust(50, " ") + "\n")

        root.destroy()

    def _create_players(self, player_names):
        no_of_players = len(player_names)

        # create randomized positions
        perimeter = 400
        mod = math.floor(perimeter / no_of_players)
        positions = []

        for i in range(no_of_players):
            pos = mod * i + random.randint(1, mod)
            if 0 <= pos <= 100:
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

        colors = {
            '1': 'yellow',
            '2': 'white',
            '3': 'black',
            '4': 'violet',
            '5': 'green',
            '6': 'gray',
            'd': 'black'
        }

        for index, name in enumerate(player_names):
            if name == '1':
                state = PlayerState(index + 1, name, colors[name], positions[index][0],
                                    positions[index][1], self.stalls_to_visit[:], self.T, self.tsp_path[:])
                player = Player1(index + 1, name, colors[name], positions[index][0], positions[index]
                                 [1], self.stalls_to_visit[:], self.T, self.tsp_path[:], self.num_players)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '2':
                state = PlayerState(index + 1, name, colors[name], positions[index][0],
                                    positions[index][1], self.stalls_to_visit[:], self.T, self.tsp_path[:])
                player = Player2(index + 1, name, colors[name], positions[index][0], positions[index]
                                 [1], self.stalls_to_visit[:], self.T, self.tsp_path[:], self.num_players)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '3':
                state = PlayerState(index + 1, name, colors[name], positions[index][0],
                                    positions[index][1], self.stalls_to_visit[:], self.T, self.tsp_path[:])
                player = Player3(index + 1, name, colors[name], positions[index][0], positions[index]
                                 [1], self.stalls_to_visit[:], self.T, self.tsp_path[:], self.num_players)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '4':
                state = PlayerState(index + 1, name, colors[name], positions[index][0],
                                    positions[index][1], self.stalls_to_visit[:], self.T, self.tsp_path[:])
                player = Player4(index + 1, name, colors[name], positions[index][0], positions[index]
                                 [1], self.stalls_to_visit[:], self.T, self.tsp_path[:], self.num_players)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '5':
                state = PlayerState(index + 1, name, colors[name], positions[index][0],
                                    positions[index][1], self.stalls_to_visit[:], self.T, self.tsp_path[:])
                player = Player5(index + 1, name, colors[name], positions[index][0], positions[index]
                                 [1], self.stalls_to_visit[:], self.T, self.tsp_path[:], self.num_players)
                self.players.append(player)
                self.player_states.append(state)
            elif name == '6':
                state = PlayerState(index + 1, name, colors[name], positions[index][0],
                                    positions[index][1], self.stalls_to_visit[:], self.T, self.tsp_path[:])
                player = Player6(index + 1, name, colors[name], positions[index][0], positions[index]
                                 [1], self.stalls_to_visit[:], self.T, self.tsp_path[:], self.num_players)
                self.players.append(player)
                self.player_states.append(state)
            else:
                state = PlayerState(index + 1, name, colors['d'], positions[index][0],
                                    positions[index][1], self.stalls_to_visit[:], self.T, self.tsp_path[:])
                player = DefaultPlayer(index + 1, name, colors['d'], positions[index][0], positions[index]
                                       [1], self.stalls_to_visit[:], self.T, self.tsp_path[:], self.num_players)
                self.players.append(player)
                self.player_states.append(state)

    def _render_frame(self):
        self.canvas = tk.Canvas(self, height=self.canvas_height + 2 * self.canvas_scale,
                                width=self.canvas_width + 80 * self.canvas_scale, bg="#ADD8E6")
        self.canvas.create_rectangle(self.canvas_scale, self.canvas_scale, self.canvas_height + 1 * self.canvas_scale,
                                     self.canvas_width + 1 * self.canvas_scale, outline="#000000", fill="white", width=1)

        # render stalls
        for stall in self.stalls_to_visit:
            x = stall.x + 1
            y = stall.y + 1
            self.canvas.create_rectangle((x - constants.stall_size / 2) * self.canvas_scale, (y - constants.stall_size / 2) * self.canvas_scale, (x +
                                         constants.stall_size / 2) * self.canvas_scale, (y + constants.stall_size / 2) * self.canvas_scale, outline="#0e9cef", fill="#0e9cef", width=1)
            self.canvas.create_text((x) * self.canvas_scale, (y) *
                                    self.canvas_scale, font=('freemono', 11, 'bold'), text=stall.id)

        for stall in self.obstacles:
            x = stall.x + 1
            y = stall.y + 1
            self.canvas.create_rectangle((x - constants.stall_size / 2) * self.canvas_scale, (y - constants.stall_size / 2) * self.canvas_scale, (x +
                                         constants.stall_size / 2) * self.canvas_scale, (y + constants.stall_size / 2) * self.canvas_scale, outline="#ff9695", fill="#ff9695", width=1)
            self.canvas.create_text((x) * self.canvas_scale, (y) *
                                    self.canvas_scale, font=('freemono', 11, 'bold'), text=stall.id)

        for index, player_state in enumerate(self.player_states):
            x = player_state.pos_x + 1
            y = player_state.pos_y + 1
            color = player_state.color
            p = self.canvas.create_oval((x - 0.5) * self.canvas_scale, (y - 0.5) * self.canvas_scale,
                                        (x + 0.5) * self.canvas_scale, (y + 0.5) * self.canvas_scale, fill=color)
            balloon = Pmw.Balloon()
            balloon.tagbind(self.canvas, p, 'Player ' + str(index + 1))
            self.player_comp.append(p)

        self.turn_comp = self.canvas.create_text((131) * self.canvas_scale, (14) * self.canvas_scale, anchor="nw", font=(
            'freemono', int(1.8 * self.canvas_scale), 'bold'), text="TURN: " + str(self.turn_no) + "/" + str(self.T))

        self.title_comp = self.canvas.create_text((133) * self.canvas_scale, (19) * self.canvas_scale, anchor="nw", font=(
            'freemono', int(1.8 * self.canvas_scale), 'bold'), text="SCORES")

        s1 = "ID"
        s2 = "Team"
        s3 = "Interaction"
        s4 = "Satisfaction"
        s5 = "Items"
        self.header_comp = self.canvas.create_text((110) * self.canvas_scale, (24) * self.canvas_scale, anchor="nw", font=('freemono', int(1.5 * self.canvas_scale), 'bold'), text=s1.ljust(int(
            0.4 * self.canvas_scale), " ") + s2.ljust(int(1 * self.canvas_scale), " ") + s5.ljust(int(1.2 * self.canvas_scale), " ") + s3.ljust(int(1.5 * self.canvas_scale), " ") + s4.ljust(int(1.5 * self.canvas_scale), " ") + "\n")

        for index, player_state in enumerate(self.player_states):
            s = self.canvas.create_text((110) * self.canvas_scale, (5 * index + 29) * self.canvas_scale, font=('freemono', int(1.5 * self.canvas_scale), 'bold'), anchor="nw", text=str(index + 1).ljust(int(0.4 * self.canvas_scale), " ") + str(player_state.name).ljust(int(1 * self.canvas_scale), " ") + (
                str(player_state.items_obtained) + "/" + str(len(self.stalls_to_visit))).ljust(int(1.2 * self.canvas_scale), " ") + str(player_state.interaction).ljust(int(1.5 * self.canvas_scale), " ") + str(round(player_state.satisfaction, 2)).ljust(int(1.5 * self.canvas_scale), " "))
            c = self.canvas.create_oval((107 - 0.8) * self.canvas_scale, (5 * index + 31 - 0.8) * self.canvas_scale, (107 + 0.2) * self.canvas_scale,
                                        (5 * index + 31 + 0.2) * self.canvas_scale, fill=player_state.color)
            self.score_comp.append(s)
            self.circles.append(c)

        pause_btn = Button(self.canvas, width=int(0.4 * self.canvas_scale), height=int(0.3 * self.canvas_scale),
                           bd='10', command=self.pause, font=('freemono', int(1.3 * self.canvas_scale), 'bold'), text="PAUSE")
        pause_btn.place(x=125 * self.canvas_scale, y=0.3 * self.canvas_scale)

        resume_btn = Button(self.canvas, width=int(0.4 * self.canvas_scale), height=int(0.3 * self.canvas_scale),
                            bd='10', command=self.resume, font=('freemono', int(1.3 * self.canvas_scale), 'bold'), text="START/\nRESUME")
        resume_btn.place(x=135 * self.canvas_scale, y=0.3 * self.canvas_scale)

        step_btn = Button(self.canvas, width=int(0.4 * self.canvas_scale), height=int(0.3 * self.canvas_scale),
                          bd='10', command=self.step, font=('freemono', int(1.3 * self.canvas_scale), 'bold'), text="STEP")
        step_btn.place(x=145 * self.canvas_scale, y=0.3 * self.canvas_scale)

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
        return (p0*p1 <= 0) & (p2*p3 <= 0)

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
                player.satisfaction += (player.interaction *
                                        math.log2(player.interaction))
            results.append(
                (player.id, player.name, player.items_obtained, player.satisfaction))

        # sort by items obtained and satisfaction
        res = sorted(results, key=lambda element: (element[2], element[3]))

        return res[::-1]

    def lookup(self, player):
        other_players, obstacles = [], []
        for index, player_state in enumerate(self.player_states):
            if player_state.id != player.id:
                if self.compute_distance(player_state.pos_x, player_state.pos_y, player.pos_x, player.pos_y) <= 10:
                    other_players.append(
                        (player_state.id, player_state.pos_x, player_state.pos_y))

        for index, obstacle in enumerate(self.obstacles):
            if self.compute_distance(player.pos_x, player.pos_y, obstacle.x, obstacle.y) <= 10:
                obstacles.append((obstacle.id, obstacle.x, obstacle.y))

        return other_players, obstacles

    def check_collision(self, x1, y1, new_x1, new_y1, x2, y2, new_x2, new_y2):
        vx = new_x1 - x1
        vy = new_y1 - y1
        wx = new_x2 - x2
        wy = new_y2 - y2

        A = vx**2 + wx**2 + vy**2 + wy**2 - 2*vx*wx - 2*vy*wy
        B = 2*x1*vx - 2*x2*vx - 2*x1*wx + 2*x2*wx + \
            2*y1*vy - 2*y2*vy - 2*y1*wy + 2*y2*wy
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
        # Check if game is over
        if self.iteration == self.T:
            self.game_state = "over"
            scores = self.compute_scores()

            s1 = "ID"
            s2 = "Team"
            s4 = "Satisfaction"
            s5 = "Items"

            if self.gui:
                self.canvas.itemconfigure(self.title_comp, text="RESULTS")
                self.canvas.itemconfigure(self.header_comp, text=s1.ljust(int(0.4 * self.canvas_scale), " ") + s2.ljust(int(
                    1 * self.canvas_scale), " ") + s5.ljust(int(1.2 * self.canvas_scale), " ") + s4.ljust(int(1.5 * self.canvas_scale), " "))

            with open(self.result_log, 'a') as f:
                f.write(s1.ljust(int(0.4 * self.canvas_scale), " ") + s2.ljust(int(1 * self.canvas_scale), " ") +
                        s5.ljust(int(1.2 * self.canvas_scale), " ") + s4.ljust(int(1.5 * self.canvas_scale), " ") + "\n")

            if self.gui:
                for index, score in enumerate(scores):
                    self.canvas.itemconfigure(self.score_comp[index], text=str(score[0]).ljust(4, " ") + str(score[1]).ljust(10, " ") + (str(score[2]) + "/" + str(
                        len(self.stalls_to_visit))).ljust(int(1 * self.canvas_scale), " ") + str(round(score[3], 2)).ljust(int(1.5 * self.canvas_scale), " "))
                    self.canvas.itemconfigure(
                        self.circles[index], fill=self.player_states[score[0] - 1].color)

            for index, score in enumerate(scores):
                with open(self.result_log, 'a') as f:
                    f.write(str(score[0]).ljust(int(0.4 * self.canvas_scale), " ") + str(score[1]).ljust(int(1 * self.canvas_scale), " ") + (str(score[2]) + "/" + str(
                        len(self.stalls_to_visit))).ljust(int(1.2 * self.canvas_scale), " ") + str(round(score[3], 2)).ljust(int(1.5 * self.canvas_scale), " ") + "\n")

            with open(self.result_log, 'a') as f:
                f.write("Game Over!")
            return

        self.iteration += 1
        new_positions = []
        update_move = []
        update_wait = []
        interrupt = []
        logs = []

        for index, player in enumerate(self.players):
            # get player action
            start_time = time.time()
            action = player.get_action(
                self.player_states[index].pos_x, self.player_states[index].pos_y)
            pos_x, pos_y = self.player_states[index].pos_x, self.player_states[index].pos_y

            if action == 'lookup':
                other_players, stalls = self.lookup(self.player_states[index])
                player.pass_lookup_info(other_players, stalls)
                end_time = time.time()
                new_positions.append([pos_x, pos_y])
                update_move.append(False)
                interrupt.append(True)
                if self.player_states[index].wait == 0:
                    update_wait.append(False)
                else:
                    update_wait.append(True)
                logs.append("Time taken: " + str(end_time -
                            start_time).ljust(40, " ") + "Action: Lookup")

            elif action == 'move':
                new_pos_x, new_pos_y = player.get_next_move()
                end_time = time.time()
                if self.player_states[index].wait == 0:
                    interrupt.append(False)
                    if self.compute_distance(pos_x, pos_y, new_pos_x, new_pos_y) <= 1.0005:
                        new_positions.append([new_pos_x, new_pos_y])
                        update_move.append(True)
                        logs.append("Time taken: " + str(end_time - start_time).ljust(
                            40, " ") + " Action: Move to (" + str(new_pos_x) + ", " + str(new_pos_y) + ")")
                    else:
                        new_positions.append([pos_x, pos_y])
                        update_move.append(False)
                        logs.append("Time taken: " + str(end_time - start_time).ljust(40, " ") + " Action: Move to (" + str(
                            new_pos_x) + ", " + str(new_pos_y) + ") Cannot move as distance > 1 unit")
                    update_wait.append(False)
                else:
                    interrupt.append(False)
                    update_wait.append(True)
                    new_positions.append([pos_x, pos_y])
                    update_move.append(False)
                    logs.append("Time taken: " + str(end_time - start_time).ljust(40, " ") + " Action: Move to (" + str(
                        new_pos_x) + ", " + str(new_pos_y) + ") Cannot move as wait time = " + str(self.player_states[index].wait))

            elif action == 'lookup move':
                other_players, stalls = self.lookup(self.player_states[index])
                player.pass_lookup_info(other_players, stalls)
                new_pos_x, new_pos_y = player.get_next_move()
                end_time = time.time()
                interrupt.append(True)
                if self.player_states[index].wait == 0:
                    if self.compute_distance(pos_x, pos_y, new_pos_x, new_pos_y) <= 1.0005:
                        new_positions.append([new_pos_x, new_pos_y])
                        update_move.append(True)
                        logs.append("Time taken: " + str(end_time - start_time).ljust(
                            40, " ") + " Action: Move to (" + str(new_pos_x) + ", " + str(new_pos_y) + ")")
                    else:
                        new_positions.append([pos_x, pos_y])
                        update_move.append(False)
                        logs.append("Time taken: " + str(end_time - start_time).ljust(40, " ") + " Action: Move to (" + str(
                            new_pos_x) + ", " + str(new_pos_y) + ") Cannot move as distance > 1 unit")
                    update_wait.append(False)
                else:
                    update_wait.append(True)
                    new_positions.append([pos_x, pos_y])
                    update_move.append(False)
                    logs.append("Time taken: " + str(end_time - start_time).ljust(40, " ") + " Action: Move to (" + str(
                        new_pos_x) + ", " + str(new_pos_y) + ") Cannot move as wait time = " + str(self.player_states[index].wait))

        # check collision with other players
        for i, player in enumerate(self.player_states):
            for j, other_player in enumerate(self.player_states):
                if i != j and player.wait == 0:
                    if self.check_collision(player.pos_x, player.pos_y,
                                            new_positions[i][0], new_positions[i][1],
                                            other_player.pos_x, other_player.pos_y,
                                            new_positions[j][0], new_positions[j][1]) or \
                            self.compute_distance(new_positions[i][0], new_positions[i][1], new_positions[j][0], new_positions[j][1]) <= 0.5:

                        update_move[i] = False
                        interrupt[i] = True
                        self.player_states[i].wait = 10
                        self.players[i].encounter_obstacle()
                        logs[i] += " Collided with Player id: " + str(other_player.id) + " name: " + str(
                            other_player.name) + ": (" + str(new_positions[i][0]) + ", " + str(new_positions[i][1]) + ")"

        # check collision with obstacles
        for i, player_state in enumerate(self.player_states):
            collision = False
            for stall in self.obstacles:
                if player_state.wait == 0 and self.check_collision_obstacle(stall.id, stall.x, stall.y, player_state.pos_x, player_state.pos_y,
                                                                            new_positions[i][0], new_positions[i][1], player_state.color):
                    update_move[i] = False
                    interrupt[i] = True
                    logs[i] += " Collided with obstacle " + str(stall.id)
                    collision = True

            if self.player_states[i].wait == 0 and new_positions[i][0] >= 100 and new_positions[i][1] >= 100:
                new_positions[i][0], new_positions[i][1] = 100, 100
                logs[i] += " Collided with boundary"
                collision = True
            elif self.player_states[i].wait == 0 and new_positions[i][0] >= 100:
                new_positions[i][0] = 100
                logs[i] += " Collided with boundary"
                collision = True
            elif self.player_states[i].wait == 0 and new_positions[i][1] >= 100:
                new_positions[i][1] = 100
                logs[i] += " Collided with boundary"
                collision = True
            elif self.player_states[i].wait == 0 and new_positions[i][0] <= 0 and new_positions[i][1] <= 0:
                new_positions[i][0], new_positions[i][1] = 0, 0
                logs[i] += " Collided with boundary"
                collision = True
            elif self.player_states[i].wait == 0 and new_positions[i][0] <= 0:
                new_positions[i][0] = 0
                logs[i] += " Collided with boundary"
                collision = True
            elif self.player_states[i].wait == 0 and new_positions[i][1] <= 0:
                new_positions[i][1] = 0
                logs[i] += " Collided with boundary"
                collision = True

            if collision:
                if self.player_states[i].wait == 0:
                    self.player_states[i].wait = 10
                self.players[i].encounter_obstacle()
                interrupt[i] = True

        # collect items
        for i, player_state in enumerate(self.player_states):
            for index, stall in enumerate(self.stalls_to_visit):
                if stall.id not in player_state.visited_stalls and self.check_visit_stall(stall.id, stall.x, stall.y, player_state.pos_x, player_state.pos_y, new_positions[i][0], new_positions[i][1],
                                                                                          player_state.color):
                    self.players[i].collect_item(stall.id)
                    player_state.add_stall_visited(stall.id)
                    player_state.add_items(1)
                    interrupt[i] = True
                    logs[i] += " Collected 1 item from stall " + str(stall.id)

        # update positions
        for i, update in enumerate(update_move):
            if update:
                self.player_states[i].pos_x, self.player_states[i].pos_y = new_positions[i][0], new_positions[i][1]

            if interrupt[i]:
                if self.player_states[i].interaction > 0:
                    self.player_states[i].satisfaction += self.player_states[i].interaction * math.log2(
                        self.player_states[i].interaction)
                self.player_states[i].interaction = 0
            elif self.player_states[i].wait == 0:
                self.player_states[i].increment_interaction()

            if update_wait[i]:
                logs[i] += " wait time is " + str(self.player_states[i].wait)
                self.player_states[i].wait -= 1

        with open(self.score_log, 'a') as f:
            f.write("\nTurn No. : " + str(self.turn_no) + "\n")
            s1 = "Player ID"
            s2 = "Name"
            s3 = "Interaction"
            s4 = "Satisfaction"
            s5 = "Items"
            f.write(s1.ljust(int(1.2 * self.canvas_scale), " ") + s2.ljust(int(1 * self.canvas_scale), " ") + s5.ljust(int(1.2 *
                    self.canvas_scale), " ") + s3.ljust(int(1.5 * self.canvas_scale), " ") + s4.ljust(int(1.5 * self.canvas_scale), " ") + "\n")

        # update player positions on game board
        if self.gui:
            for index, player_state in enumerate(self.player_states):
                if update_move[index]:
                    self.canvas.moveto(self.player_comp[index], (player_state.pos_x + 0.5)
                                       * self.canvas_scale, (player_state.pos_y + 0.5) * self.canvas_scale)
                self.canvas.itemconfigure(self.score_comp[index], text=str(index + 1).ljust(int(0.4 * self.canvas_scale), " ") + str(player_state.name).ljust(int(1 * self.canvas_scale), " ") + (str(player_state.items_obtained) + "/" + str(
                    len(self.stalls_to_visit))).ljust(int(1.2 * self.canvas_scale), " ") + str(player_state.interaction).ljust(int(1.5 * self.canvas_scale), " ") + str(round(player_state.satisfaction, 2)).ljust(int(1.5 * self.canvas_scale), " "))

            self.canvas.itemconfigure(
                self.turn_comp, text="TURN: " + str(self.turn_no) + "/" + str(self.T))

        for index, player_state in enumerate(self.player_states):
            with open(player_state.log, 'a') as f:
                f.write("TURN " + str(self.turn_no) +
                        ": " + logs[index] + "\n")

        for index, player_state in enumerate(self.player_states):
            with open(self.score_log, 'a') as f:
                f.write(str(index + 1).ljust(int(1.2 * self.canvas_scale), " ") + str(player_state.name).ljust(int(1 * self.canvas_scale), " ") + (str(player_state.items_obtained) + "/" + str(len(self.stalls_to_visit))).ljust(
                    int(1.2 * self.canvas_scale), " ") + str(player_state.interaction).ljust(int(1.5 * self.canvas_scale), " ") + str(round(player_state.satisfaction, 2)).ljust(int(1.5 * self.canvas_scale), " ") + "\n")

        self.turn_no += 1

        # Next turn after 100 ms
        if self.game_state == "resume":
            if self.gui:
                self.after(self.interval, self._play_game)
            else:
                time.sleep(1)
                self._play_game()
