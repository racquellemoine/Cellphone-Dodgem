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

        #keep track of current walking direction 
        #we want to walk counter clockwise
        print("starting at: ", self.pos_x, self.pos_y) 
        if self.pos_x == self.rightLimit: 
            print("starting walking up")
            self.walkingDirection = "up"
        if self.pos_y == self.upperLimit: 
            print("starting walking left")
            self.walkingDirection = "left"
        if self.pos_x == self.leftLimit:
            print("starting walking down")
            self.walkingDirection = "down"
        if self.pos_y == self.lowerLimit: 
            print("starting walking right")
            self.walkingDirection = "right"

    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        #remove stall_id from stalls_to_visit 
        if stall_id in self.stalls_to_visit: self.stalls_to_visit.remove(stall_id)

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        pass

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
        #we want to snake board, explore in a spiral, idea of following the wall 

        print("\nupperLimit: ", self.upperLimit)
        print("lowerLimit: ", self.lowerLimit)
        print("leftLimit: ", self.leftLimit)
        print("rightLimit: ", self.rightLimit)
        print("currently at: ", self.pos_x, ", ", self.pos_y)
        #within 10 steps of right boundary while walking right 
        if self.walkingDirection == "right" and self.pos_x in range(self.rightLimit-10, self.rightLimit): 
            print("walking right, approached limit")
            self.rightLimit = self.rightLimit-10 
            self.walkingDirection = "back track left"
            new_pos_x = self.pos_x-1
            new_pos_y = self.pos_y
            return new_pos_x, new_pos_y
        #walking right but haven't approached rightLimit yet, continue 
        if self.walkingDirection == "right": 
            print("walking right")
            new_pos_x = self.pos_x + 1
            new_pos_y = self.pos_y
            return new_pos_x, new_pos_y
        
        #within 10 steps of upper boundary while walking up 
        if self.walkingDirection == "up" and self.pos_y in range(self.upperLimit, self.upperLimit+11): 
            #move boundary 10 steps down from current upper boundary 
            print("walking up and approached limit")
            self.upperLimit = self.upperLimit+10
            self.walkingDirection = "back track down"
            new_pos_x = self.pos_x
            new_pos_y = self.pos_y+1
            return new_pos_x, new_pos_y
        #walking up but haven't approached upperLimit yet
        #continue walking up for 20 steps 
        if self.walkingDirection == "up": 
            print("walking up, haven't approached limit")
            new_pos_x = self.pos_x
            new_pos_y = self.pos_y - 1
            return new_pos_x, new_pos_y
        
        #within 10 steps of left boundary while walking left 
        if self.walkingDirection == "left" and self.pos_x in range(self.leftLimit, self.leftLimit+10): 
            print("walking left and approached limit")
            #move boundary 10 steps right from current leftLimit and walk down 
            self.leftLimit = self.leftLimit - 10
            self.walkingDirection = "back track right"
            new_pos_x = self.leftLimit - 1
            new_pos_y = self.pos_y
        #walking left but haven't approached leftLimit yet, continue
        if self.walkingDirection == "left":
            new_pos_x = self.pos_x - 1 
            print("walking left")
            new_pos_y = self.pos_y
            return new_pos_x, new_pos_y
        
        #within 10 steps of lower boundary while walking down 
        if self.walkingDirection == "down" and self.pos_y in range(self.lowerLimit-10, self.lowerLimit): 
            print("walking down and approached lowerLimit")
            #move boundary 10 steps up from current lowerLimit and walk right 
            self.lowerLimit = self.lowerLimit - 10 
            new_pos_x = self.pos_x
            new_pos_y = self.pos_y - 1
            self.walkingDirection = "back track up"
            return new_pos_x, new_pos_y
        #walking down but haven't approached lowerLimit yet 
        #continue walking down for 20 steps 
        if self.walkingDirection == "down": 
            print("walking down")
            new_pos_x = self.pos_x
            new_pos_y = self.pos_y+1
            return new_pos_x, new_pos_y
        
        #we reached right limit and are backtracking left 
        if self.walkingDirection == "back track left": 
            print("back tracking left")
            new_pos_x = self.pos_x - 1
            new_pos_y = self.pos_y
            if new_pos_x == self.rightLimit - 10: 
                #once we are 10 steps left from the right limit, walk up
                self.walkingDirection = "up"
            return new_pos_x, new_pos_y
        
        #we reached upper limit and are backtracking down 
        if self.walkingDirection == "back track down": 
            print("back tracking down")
            new_pos_x = self.pos_x 
            new_pos_y = self.pos_y + 1
            if new_pos_y == self.upperLimit + 10: 
                #once we are 10 steps below upper limit, walk left 
                self.walkingDirection = "left"
            return new_pos_x, new_pos_y
        
        #we hit left bound and are backtracking right
        if self.walkingDirection == "back track right": 
            print("back tracking right")
            new_pos_x = self.pos_x + 1
            new_pos_y = self.pos_y
            if new_pos_y == self.leftLimit + 10: 
                #once we are 10 steps right of left limit, walk down 
                self.walkingDirection = "down"
            return new_pos_x, new_pos_y

        #we hit lower limit and are backtracking up 
        if self.walkingDirection == "back track up": 
            print("back tracking up")
            new_pos_x = self.pos_x
            new_pos_y = self.pos_y - 1
            if new_pos_y == self.lowerLimit - 10: 
                #once we are 10 steps up from lower limit, walk right
                self.walkingDirection = "right"
            return new_pos_x, new_pos_y

        #no more board left to explore 
        if self.lowerLimit <= self.upperLimit and self.leftLimit >= self.rightLimit:  
            print("no more board left")
            return self.pos_x, self.pos_y

        print("returning same position")
        return self.pos_x, self.pos_y