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

        #wall boundaries for wall following algorithm 
        self.rightLimit = 100 
        self.leftLimit = 0 
        self.upperLimit = 0 
        self.lowerLimit = 100

        self.lookup_counter = 0 #start by looking up 

        #initialize an empty board-> with 1's
        self.playing_field = [[2 for i in range(100)] for j in range(100)]
        self.time_since_last_lookup = 0 # need to figure out how to best keep track of this guy 
        self.obstacle_movement_queue = []
        self.tsp_queue = []
        #r,c represents x,y coordinates
        #2 indicates unexplored
        #3 indicates explored bt unvisiited stall
        #1 indicates visited stall
        #0 indicates space explored - (not a stall or obstacle)
        #-1 indicates an obstacle 


        #keep track of current walking direction 
        #we want to walk counter clockwise
        print("starting at: ", self.pos_x, self.pos_y) 
        if self.pos_x == self.rightLimit: 
            self.walkingDirection = "back track left"
        if self.pos_y == self.upperLimit: 
            self.walkingDirection = "back track down"
        if self.pos_x == self.leftLimit:
            self.walkingDirection = "back track right"
        if self.pos_y == self.lowerLimit: 
            self.walkingDirection = "back track up"

    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        #remove stall_id from stalls_to_visit 
        if stall_id in self.stalls_to_visit: self.stalls_to_visit.remove(stall_id)
        #remove stall_id from stalls_to_visit 
        if stall_id in self.stalls_to_visit: self.stalls_to_visit.remove(stall_id)

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        #given where an obstacle is, can dictate movements 
        #given coordinates of obstacles and other players 

        #for obstacles, update their positions to be -1 
        #format of obstacles? 
        for o in obstacles: 
            x_pos,y_pos = int(o[1]), int(o[2])
            self.playing_field[x_pos][y_pos] = -1 


    def detect_obstacle(self,x_range,y_range): #add a queue of movements to perform 
        for x in x_range:
            for y in y_range:
                self.playing_field[x][y] = -1 
        #so the spots have been identified, now perform movement directions 
        if self.walkingDirection == "right":
            self.obstacle_movement_queue = ["down","down","right","right","up","up","right","right"]
        if self.walkingDirection == "left":
            self.obstacle_movement_queue = ["up","up","left","left","down","down","left","left"]
        if self.walkingDirection == "up":
            self.obstacle_movement_queue = ["right","right","up","up","left","left","up","up"]   
        if self.walkingDirection == "down":
            self.obstacle_movement_queue = ["left","left","down","down","right","right","down","down"]

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        self.playing_field[self.pos_x][self.pos_y] = -1 #butn need a way to tell if it is a player? 
        #self.vx = random.random()
        #self.vy = math.sqrt(1 - self.vx**2)
        #self.sign_x *= -1
        #self.sign_y *= -1
        print("obstacle hit")
        #self.pos_x = 0
        #self.pos_y = 0
        #return self.pos_x, self.pos_y
        if self.walkingDirection == "right" or "back track right":
            print("switching down")
            #self.walkingDirection = "back"
            self.walkingDirection = "down"
            return self.pos_x, self.pos_y
        if self.walkingDirection == "down" or "back track down":
            #self.walkingDirection = "left"
            self.walkingDirection = "left"
            return self.pos_x, self.pos_y
        if self.walkingDirection == "left" or "back track left":
            #self.walkingDirection = "up"
            self.walkingDirection = "up"
            return self.pos_x, self.pos_y
        if self.walkingDirection == "up" or "back track up":
            #self.walkingDirection = "right"
            self.walkingDirection = "right"
            return self.pos_x, self.pos_y
        random_number = random.randint(1, 4)
        if random_number == 1:
            self.walkingDirection = "down" #ok so this works 
        if random_number == 2:
            self.walkingDirection = "up" 
        if random_number == 3:
            self.walkingDirection = "right" 
        if random_number == 4:
            self.walkingDirection = "left" 
        #i think because we created var walkingdirection it cannot detect the direction that it is going -> so just sets as default 
        print("new direction: " + self.walkingDirection)
        

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        
        self.pos_x = pos_x
        self.pos_y = pos_y

        if self.pos_x <=1 or self.pos_x >=99:
            return 'move'
        if self.pos_y <=1 or self.pos_y >=99:
            return 'move'
            
        
        if self.lookup_counter == 0:
            self.lookup_counter = 10
            return 'lookup'
        self.lookup_counter -= 1 #subtract one 

        return 'move'

        #when do we want to lookup 
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        #we want to snake board, explore in a spiral, idea of following the wall 

        print("\nupperLimit: ", self.upperLimit)
        print("lowerLimit: ", self.lowerLimit)
        print("leftLimit: ", self.leftLimit)
        print("rightLimit: ", self.rightLimit)
        print("currently at: ", self.pos_x, ", ", self.pos_y)
        #within 10 steps of right boundary while walking right 

        #see if queue is not, empty -> if not empty, perform those movements 
        if self.obstacle_movement_queue != []:
            #perform these measures 
            cur_walk_dir = self.obstacle_movement_queue.pop(0)
            self.walkingDirection = cur_walk_dir
        nextMove = self.walkingDirection
            
        if nextMove == "up": new_pos_x, new_pos_y = self.__walkingUp()
        if nextMove == "down": new_pos_x, new_pos_y = self.__walkingDown()
        if nextMove == "right": new_pos_x, new_pos_y = self.__walkingRight()
        if nextMove == "left": new_pos_x, new_pos_y = self.__walkingLeft()

        if self.walkingDirection == "back track up": new_pos_x, new_pos_y = self.__backTrackingUp()
        if self.walkingDirection == "back track down": new_pos_x, new_pos_y = self.__backTrackingDown()
        if self.walkingDirection == "back track right": new_pos_x, new_pos_y = self.__backTrackingRight()
        if self.walkingDirection == "back track left": new_pos_x, new_pos_y = self.__backTrackingLeft()

        #no more board left to explore 
        if self.lowerLimit <= self.upperLimit and self.leftLimit >= self.rightLimit:  
            print("no more board left")
            #return self.pos_x, self.pos_y

        #if self.playing_field[new_pos_x][new_pos_y] == -1: 
            #self.detect_obstacle(x_range, y_range)
            #return self.pos_x, self.pos_y

        return new_pos_x, new_pos_y
    
    def __walkingUp(self): 
        print("walking up")
        #within 10 steps of upper bound
        if self.pos_y <= self.upperLimit+10: 
            #move boundary 10 steps down
            print("walking up and approached limit")
            self.upperLimit += 10
            self.walkingDirection = "back track down"
            return self.pos_x, self.pos_y+1
        #continue walking up
        return self.pos_x, self.pos_y-1
    

    def __walkingDown(self): 
        print("walking down")
        #within 10 steps of lower bound 
        if self.pos_y  >= self.lowerLimit-10:
            print("walking down and approached limit")
            #move boundary 10 steps up from limit
            self.lowerLimit -= 10
            self.walkingDirection = "back track up"
            return self.pos_x, self.pos_y-1
        #continue walking down
        return self.pos_x, self.pos_y+1
    
    def __walkingRight(self): 
        print("walking right")
        #within 10 steps of right bound
        if self.pos_x >= self.rightLimit-10:
            print("walking right and approached limit")
            #move boundary 10 steps left 
            self.rightLimit -= 10
            self.walkingDirection = "back track left"
            return self.pos_x-1, self.pos_y
        #continue walking right
        return self.pos_x+1, self.pos_y
    
    def __walkingLeft(self):
        print("walking left")
        #within 10 steps of left bound
        if self.pos_x <= self.leftLimit+10:
            print("walking left and approached limit")
            #move boundary 10 steps right
            self.leftLimit += 10
            self.walkingDirection = "back track right"
            return self.pos_x+1, self.pos_y
        #continue walking left
        return self.pos_x-1, self.pos_y
    
    def __backTrackingUp(self):
        print("back tracking up")
        #we are 10 steps above lower limit
        if self.pos_y == self.lowerLimit-9:
            self.walkingDirection = "right"
        return self.pos_x, self.pos_y-1

    def __backTrackingDown(self):
        print("back tracking down")
        #we are 10 steps below upper limit
        if self.pos_y == self.upperLimit+9:
            self.walkingDirection == "left"
        return self.pos_x, self.pos_y+1
    
    def __backTrackingRight(self):
        print("back tracking right")
        #we are 10 steps left from left limit
        if self.pos_x == self.leftLimit+9:
            self.walkingDirection = "down"
        return self.pos_x+1, self.pos_y
    
    def __backTrackingLeft(self):
        print("back tracking left")
        #we are 10 steps left from right limit
        if self.pos_x == self.rightLimit-9: 
            self.walkingDirection = "up"
        return self.pos_x-1, self.pos_y