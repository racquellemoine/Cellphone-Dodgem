import math
import random
random.seed(2)
import fast_tsp
import queue    
from collections import deque
from itertools import chain

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
        self.num_stalls = len(stalls_to_visit)
        self.hasHitObstacle = {}
        for stall in range(self.num_stalls): self.hasHitObstacle[stall] = 0


        self.vx = random.random()
        self.vy = math.sqrt(1 - self.vx**2)

        self.sign_x = 1
        self.sign_y = 1

        ###TSP Implementation from team 5's first implementation###

        #initiating dist as a 2D list with zeros to store distance points
        self.dists = [[0 for _ in range(self.num_stalls + 1)] for _ in range(self.num_stalls + 1)]
        self.q = deque() # stores the path or the sequence of stalls a player will visist

        self.tsp()
        self.path_queue()
        self.encounter_obs = False
        self.obstacle_queue = []
        self.obstacle_movement_queue = []
        self.obstacles = []
        self.lookup_counter = 0
        self.playing_field = [[2 for i in range(100)] for j in range(100)]

    def path_queue(self):
        stv = self.stalls_to_visit
        tsp = self.tsp_path

        if self.num_stalls > 14: #sweet number for when the stalls are on the right order otherwise it shows reverse path
            for i in tsp[1:]:
                self.q.append(stv[i-1])
        else:
            for i in tsp[::-1]:
                stall = stv[i - 1]
                if stall not in self.q:
                    self.q.append(stv[i-1])
    def tsp(self):
        '''Calculates the Traveling Salesman Problem (TSP) path for the player, which is a sequence of stalls to visit in the optimal order.'''
        stv = self.stalls_to_visit
        n = self.num_stalls
        x,y = self.pos_x, self.pos_y
        for i in range(0, n):
            d = self.calc_distance(x, y, stv[i].x, stv[i].y)
            self.dists[0][i+1] = math.ceil(d)

        for i in range(0, n):
            for j in range(0, n):
                d = self.calc_distance(stv[i].x, stv[i].y, stv[j].x, stv[j].y)
                self.dists[i+1][j+1] = math.ceil(d)
        self.tsp_path = fast_tsp.find_tour(self.dists)

    def calc_distance(self, x1, y1, x2, y2):
        '''calculates the Euclidean distance between two points (x1, y1) and (x2, y2)'''
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    def normalize(self, vx, vy):
        '''normalize a vector given its components vx and vy to create a unit vector.'''
        norm = self.calc_distance(vx, vy, 0, 0)
        return vx / norm, vy / norm

     # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        for o in obstacles: 
            self.obstacles.append(o)
            x_pos,y_pos = o[1], o[2]
            #print("checking if obstacle ", o[0], " is on path")
            if self.obstacle_on_path(x_pos, y_pos) and o not in self.obstacle_queue:
                self.obstacle_queue.append(o)
                #print("This Obstacle is on the way:", {o[0]}, " at ", {o[1], o[2]})
                self.encounter_obstacle()
    
    def obstacle_on_path(self, obstacle_x, obstacle_y):
        x1, y1 = self.pos_x, self.pos_y 
        closest_stall = self.q[0]
        #print("checking obstacle on path to stall ", closest_stall.id)
        x2 = closest_stall.x
        y2 = closest_stall.y
        return self.is_point_on_line(obstacle_x, obstacle_y, x1, y1, x2, y2)

    def is_point_on_line(self, x, y, x1, y1, x2, y2):
        """Check if the point (x, y) lies on the line segment between (x1, y1) and (x2, y2)."""
        #if min(x1, x2) <= x <= max(x1, x2) and min(y1, y2) <= y <= max(y1, y2):
            # The point (x, y) is within the bounding box of the line segment
            # Check if it's collinear with the line segment
            #return True
        path = int(self.calc_distance(x1, y1, x2, y2))
        distance1 = self.calc_distance(x1, y1, x, y)
        distance2 = self.calc_distance(x,y, x2, y2)
        sum = distance1+distance2
        #print("sum: ", sum)
        #print("path: ", path)
        onLine = sum > path-1 and sum < path+2
        return onLine
        
    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):

        '''It checks if the item collected matches the stall at the front of the queue (q[0]). If so, 
            it removes that stall from the queue.If the collected item does not match the stall at the 
            front of the queue, it iterates through the queue to find and remove the matching stall.'''
        #print("length of queue is " + str(len(self.q)))
        if stall_id == self.q[0].id:
            self.q.popleft()
        else:
            #temp_length = len(self.q)
            #count = 0
            #while count < temp_length
            copy_deque = self.q.copy()
            for s in copy_deque:
                if stall_id == s.id:
                    self.q.remove(s)
                    break            

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        # find points on circle
        # travel to this point if there is no obstacle on path
        # any points on circle can be found by degrees w/ formulas
        # x=rsin(a), y=rcos(a) where r is radius and a is angle
        #print("in encounter obstacle")
        #print("currently at ", [self.pos_x, self.pos_y])
        if len(self.obstacle_queue) == 0: 
            #print("obstacle queue is empty")
            return
        obstacle = self.obstacle_queue[0]
        if obstacle[0] in self.hasHitObstacle:
            self.hasHitObstacle[obstacle[0]] = self.hasHitObstacle[obstacle[0]] + 1
            #print("has hit obstacle ", self.hasHitObstacle[obstacle[0]], " times")
        else:
            self.hasHitObstacle[obstacle[0]] = 1
        #print("trying to avoid obstacle ", obstacle[0])
        angles = []
        for angle in range(0, 360):
            angles.append(angle)
        for angle in range(0, 360):
            if self.hasHitObstacle[obstacle[0]] > 10:
                angle = random.choice(angles)
            angles.remove(angle)
            #print("trying angle ", angle)
            #print("checking angle ", angle)
            originX = 5*math.sin(angle)
            originY = 5*math.cos(angle)
            x = originX+self.pos_x
            y = originY+self.pos_y
            if self.is_point_on_line(obstacle[1], obstacle[2], self.pos_x, self.pos_y, x, y):
                #print("obstacle on line")
                continue
            if (x >= obstacle[1]-1.5 and x <= obstacle[1]+1.5) and (y >= obstacle[2]-1.5 and y<=obstacle[2]+1.5): 
                #print("direction is too close")
                continue
            vx = x - self.pos_x
            vy = x - self.pos_y
            self.vx, self.vy = self.normalize(vx, vy)
            new_pos_x = self.pos_x + self.sign_x * self.vx
            new_pos_y = self.pos_y + self.sign_y * self.vy
            #print("checking position ", [new_pos_x, new_pos_y])
            #print("obstacle ", obstacle[0], " is at ", [obstacle[1], obstacle[2]])
            if abs(new_pos_x - obstacle[1]) <=1 and abs(new_pos_y - obstacle[2]) <= 1: 
                #print("direction too close")
                continue
            if x > 99: x = 99
            if y > 99: y = 99
            if x < 1: x = 1
            if y < 1: y = 1
            for obstacle in self.obstacle_queue:
                if self.is_point_on_line(obstacle[1], obstacle[2], self.pos_x, self.pos_y, x, y):
                    #print('other obstacle interferes')
                    continue
            #print("move to ", [int(x),int(y)], " obstacle not on line")
            self.obstacle_movement_queue.append([int(x),int(y)])
            break
        self.obstacle_queue.remove(obstacle)

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move' or 'lookup move'
        
        #self.pos_x = pos_x
        #self.pos_y = pos_y

        self.pos_x = pos_x
        self.pos_y = pos_y
        if pos_x >=99 or pos_x <=1:
            return 'move'
        if pos_y >=99 or pos_y <=1:
            return 'move'
        
        if self.lookup_counter == 0:
            self.lookup_counter = 10
            return 'lookup'
        self.lookup_counter -= 1 #subtract one 

        #return 'move'
        
        return 'move'
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        #print("entering move")
        #print(len(self.obstacle_movement_queue))
        #print("next stall ", self.q[0].id)
        possiblePoints = [[math.floor(self.pos_x), math.floor(self.pos_y)], [math.ceil(self.pos_x), math.ceil(self.pos_y)], [math.ceil(self.pos_x), math.floor(self.pos_y)], [math.floor(self.pos_x), math.ceil(self.pos_y)] ]
        for point in possiblePoints:
            if point in self.obstacle_movement_queue:
                self.obstacle_movement_queue.remove(point)
                #print("removing current pos from obstacle movement queue")
                break
        new_pos_x = None
        new_pos_y = None
        if self.obstacle_movement_queue != []:
            #print("obstacle movement queue not empty")
            #print("currently at ", [self.pos_x, self.pos_y])
            next_move = self.obstacle_movement_queue.copy().pop()
            #print(next_move)
            #print("calc vector to move in direction ", next_move[0], ", ", next_move[1])
            vx = next_move[0] - self.pos_x
            vy = next_move[1] - self.pos_y
            #print("vectors: ", [vx, vy])
            self.vx, self.vy = self.normalize(vx, vy)
        else: 
            for o in self.obstacles:
                if self.obstacle_on_path(o[1], o[2]) and o not in self.obstacle_queue:
                    print("obstacle ", o[0], " on path and not in queue")
                    self.obstacle_queue.append(o)
                    self.encounter_obstacle()
                    break
            for o in self.obstacles:
                if self.obstacle_on_path(o[1], o[2]) and o not in self.obstacle_queue:
                    print("obstacle ", o[0], " on path and not in queue")
                    #print("obstacle ", o[0], " on path at ", [o[1], o[2]])
                    #print("currently at ", [self.pos_x, self.pos_y])
                    self.obstacle_queue.append(o)
                    self.encounter_obstacle()
                    break
        if self.obstacle_movement_queue == []:
            '''updates the player's velocity vector based on the next stall to visit. If there are still stalls in the queue (self.q), 
                the player's velocity is adjusted to move toward the first stall in the queue in a way that maintains a constant speed.'''
            if (len(self.q) > 0):
                vx = self.q[0].x - self.pos_x
                vy = self.q[0].y - self.pos_y

                self.vx, self.vy = self.normalize(vx, vy)
        if new_pos_x is None or new_pos_y is None:
            new_pos_x = self.pos_x + self.sign_x * self.vx
            new_pos_y = self.pos_y + self.sign_y * self.vy
            #print("new x and y positions:")
            #print(new_pos_x)
            #print(new_pos_y)
            self.pos_x = new_pos_x
            self.pos_y = new_pos_y
            #print(self.pos_x)
            #print(self.pos_y)
        self.obstacle_queue = []
        return new_pos_x, new_pos_y
