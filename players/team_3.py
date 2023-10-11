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
        self.walkingDirection = "right"

        #queue of next steps to move around obstacle or away from wall
        self.queue = []
        #keep track of current walking direction 
        #we want to walk counter clockwise
        print("starting at: ", self.pos_x, self.pos_y) 
        if self.pos_x == self.rightLimit: 
            self.queue = ["left"]*10
            print("starting walking up")
            self.walkingDirection = "up"
        if self.pos_y == self.upperLimit: 
            self.queue = ["down"]*10
            print("starting walking left")
            self.walkingDirection = "left"
        if self.pos_x == self.leftLimit:
            self.queue = ["right"]*10
            print("starting walking down")
            self.walkingDirection = "down"
        if self.pos_y == self.lowerLimit: 
            self.queue = ["up"]*10
            print("starting walking right")
            self.walkingDirection = "right"
        print("queue: ", self.queue)

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
        #self.vx = random.random()
        #self.vy = math.sqrt(1 - self.vx**2)
        #self.sign_x *= -1
        #self.sign_y *= -1
        print("obstacle hit")
        #self.pos_x = 0
        #self.pos_y = 0
        #return self.pos_x, self.pos_y
        if self.walkingDirection == "right":
            print("switching down")
            #self.walkingDirection = "back"
            self.walkingDirection = "down"
            #self.pos_x = self.pos_x
            #self.pos_y = self.pos_x -1
            #print("entering if statement")
            #self.get_next_move()
            return self.pos_x, self.pos_y
        if self.walkingDirection == "down":
            #self.walkingDirection = "left"
            self.walkingDirection = "left"
            return self.pos_x, self.pos_y
        if self.walkingDirection == "left":
            #self.walkingDirection = "up"
            self.walkingDirection = "up"
            return self.pos_x, self.pos_y
        if self.walkingDirection == "up":
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
        print("queue: ", self.queue)
        print("number of stalls: ", len(self.stalls_to_visit))


        nextMove = self.walkingDirection
        if self.queue != []: nextMove = self.queue.pop(0)
        
        if nextMove == "up": return self.__walkingUp()
        if nextMove == "down": return self.__walkingDown()
        if nextMove == "right": return self.__walkingRight()
        if nextMove == "left": return self.__walkingLeft()

        if self.walkingDirection == "back track up": return self.__backTrackingUp()
        if self.walkingDirection == "back track down": return self.__backTrackingDown()
        if self.walkingDirection == "back track right": return self.__backTrackingRight()
        if self.walkingDirection == "back track left": return self.__backTrackingLeft()

        #no more board left to explore 
        if self.lowerLimit >= self.upperLimit and self.leftLimit >= self.rightLimit:  
            print("no more board left")
            return self.pos_x, self.pos_y


        #this is only really occuring if obstacle -> not entirely sure why 
        #self.pos_x -= 1 
        #self.pos_y += 1 
        print("returning same position")
        return self.pos_x, self.pos_y
    
    def __walkingUp(self): 
        print("walking up")
        #within 10 steps of upper bound
        if self.pos_y in range(self.upperLimit, self.upperLimit+11): 
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
        if self.pos_y in range(self.lowerLimit-10, self.lowerLimit):
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
        if self.pos_x in range(self.rightLimit-10, self.rightLimit):
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
        if self.pos_x in range(self.leftLimit, self.leftLimit+11):
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
    
