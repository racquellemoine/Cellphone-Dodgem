import fast_tsp, math, random
from queue import Queue
from queue import PriorityQueue
from sys import maxsize as INT_MAX

random.seed(2)

HORIZON = 10 # how far we can look
DANGER_ZONE = 0.5 # how close we can get to an obstacle/person

class Vector:    

    def __init__(self, _x, _y, _parent=None, _stall=None, _distTraveled=0):
        self.x = _x
        self.y = _y
        self.parent = _parent #parent of vector, used in a* search route
        self.stall = _stall #next stall of vector, used in a* search route
        self.dist = _distTraveled #distance traveled in route so far, used in a* search route

    #two vectors are equal if they have the same direction and distance to next stall
    def __eq__(self, other):
        direction =  (self.x == other.x) and (self.y == other.y)
        distanceToStall =  self.__distance(self.stall) == other.__distance(other.stall)
        return direction and distanceToStall
    
    # euclideian distance heuristic to the next stall, used for the priority queue in a* search
    def __lt__(self, other):
        self_d = self.__distance(self.stall)
        other_d = other.__distance(other.stall)
        return (self_d + self.dist) < (other_d + other.dist)
    
    def __distance(self, other):
        """Euclidean distance"""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
    
    def __str__(self):
        """Human-readable string representation of the vector."""
        return f'{self.x:g}i + {self.y:g}j'

    def __repr__(self):
        """Unambiguous string representation of the vector."""
        return repr((self.x, self.y))

    def __add__(self, other):
        """Vector addition."""
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Vector subtraction."""
        return Vector(self.x - other.x, self.y - other.y)

    def __matmul__(self, other):
        """Vector cross product."""
        if isinstance(other, Vector):
            return self.x*other.y - self.y*other.x
        raise NotImplementedError('Can only take cross product of two vectors')

    def __mul__(self, multiplier):
        """Multiplication of a vector by a scalar/vector."""
        if isinstance(multiplier, Vector): # inner product
            return self.x*multiplier.x + self.y*multiplier.y
        elif isinstance(multiplier, int) or isinstance(multiplier, float): # scalar multiplication
            return Vector(self.x*multiplier, self.y*multiplier)
        raise NotImplementedError('Can only multiply Vector by a scalar or a vector')

    def __rmul__(self, multiplier):
        """Multiplication of a vector by a scalar/vector."""
        return self.__mul__(multiplier)

    def __neg__(self):
        """Negation of the vector (invert through origin.)"""
        return Vector(-self.x, -self.y)

    def __truediv__(self, scalar):
        """True division of the vector by a scalar."""
        return Vector(self.x / scalar, self.y / scalar)

    def __mod__(self, scalar):
        """One way to implement modulus operation: for each component."""
        return Vector(self.x % scalar, self.y % scalar)

    def __abs__(self):
        """Absolute value (magnitude) of the vector."""
        return math.sqrt(self.x**2 + self.y**2)
    
    def dist2(self, other):
        """The distance between vectors self and other."""
        return abs(self - other)
    
    def normalize(self):
        """The normalized vector (unit vector) in the direction of self."""
        return self / abs(self)

    def normalized_dir(self, other):
        """The normalized direction vector from self to other."""
        dist = self.dist2(other)
        return Vector(0,0) if dist==0 else (other - self) / self.dist2(other)
    
    def left_90(self):
        """The vector rotated 90 degrees counter-clockwise."""
        return Vector(-self.y, self.x)
    
    def right_90(self):
        """The vector rotated 90 degrees clockwise."""
        return Vector(self.y, -self.x)
    
    def rotate(self, theta):
        """The vector rotated by theta radians counter-clockwise."""
        return Vector(self.x*math.cos(theta) - self.y*math.sin(theta), self.x*math.sin(theta) + self.y*math.cos(theta))
    
    def update_val(self, new_val):
        """Update the value of the vector."""
        self.x = new_val.x
        self.y = new_val.y

class Player:
    def __init__(self, id, name, color, initial_pos_x, initial_pos_y, stalls_to_visit, T_theta, tsp_path, num_players):
        self.id = id
        self.name = name
        self.color = color
        self.prev_pos = Vector(-1, -1)
        self.pos = Vector(initial_pos_x, initial_pos_y)
        self.all_stalls = stalls_to_visit
        self.stalls_next = list()
        self.aStarRoute = list()

        self.obstacles_known = list()
        self.players_cached = list()
        self.t_since_lkp = INT_MAX
        self.last_ckpt = Vector(initial_pos_x, initial_pos_y)

        self.T_theta = T_theta
        self.tsp_path = tsp_path
        self.num_players = num_players

        self.pos_last_lkp = Vector(initial_pos_x, initial_pos_y)
        self.should_lookup = False

        self.__tsp()
        self.times_lkp = 0

        self.dir = self.pos.normalized_dir(self.__next_stall()) # unit vector representing direction of movement
        # self.next_ckpt = Vector(initial_pos_x, initial_pos_y) # next lookup checkpoint       
        self.vicinity = 0.0005 # tolerance for reaching a checkpoint
    
    def __randunit(self):
        """A random unit vector."""
        theta = random.random() * 2 * math.pi
        return Vector(math.cos(theta), math.sin(theta))
    
    def __tsp(self):
        stalls = self.all_stalls
        num = len(self.all_stalls)
        distances = [[0 for _ in range(num + 1)] for _ in range(num + 1)]

        for i in range(num):
            currVector =  Vector(stalls[i].x, stalls[i].y)
            dist = self.pos.dist2(currVector)
            distances[0][i+1] = math.ceil(dist)

        for i in range(num):
            for j in range(num):
                currVector1 = Vector(stalls[i].x, stalls[i].y)
                currVector2 = Vector(stalls[j].x, stalls[j].y)
                dist = currVector1.dist2(currVector2)
                distances[i+1][j+1] = math.ceil(dist)
                
        self.tsp_path = fast_tsp.find_tour(distances)
        to_print = []
        for i in self.tsp_path[1:]:
            self.stalls_next.append(self.all_stalls[i-1])
            to_print.append(self.all_stalls[i-1].id)

    def __update_tsp(self):
        # Assuming 'stalls_to_visit' is a list of stalls that the player needs to visit
        stalls_to_visit = self.stalls_next

        # Now, find the nearest stall to the player's current position
        nearest_stall_index = min(range(len(stalls_to_visit)), key=lambda i: self.pos.dist2(stalls_to_visit[i]))

        # Reorder the remaining stalls based on the nearest stall to the player
        ordered_stalls = stalls_to_visit[nearest_stall_index:] + stalls_to_visit[:nearest_stall_index]

        self.stalls_next = list()
        self.stalls_next = ordered_stalls

    #main a* search algorithm that finds the best path around obstacle
    def __astar(self):
        nextStall = self.__next_stall()
        toExplore = PriorityQueue()
        if len(self.stalls_next) > 0:
            initial_location = Vector(self.pos.x, self.pos.y, None, nextStall, 0)
            toExplore.put(initial_location)

            explored = []
            while toExplore.qsize() > 0:
                curr = toExplore.get()
                if (curr.x, curr.y) not in explored:
                    explored.append((curr.x, curr.y))
                    # return path 
                    if curr.dist2(nextStall) < 3 or curr.dist >= 10:
                        return self.get_astar_path(curr)
                    for child_vector in self.aStar_expand(curr, nextStall):
                        if (child_vector.x, child_vector.y) not in explored:
                            toExplore.put(child_vector)

        return []

    #returns a list of vectors, rotating the current vector by 15 degrees left and right
    #this represents 12 different directions from the current vector in a 180 degree area
    def aStar_expand(self, vector, stall):
        rotate = 15 
        newVectors = []
        for i in range(0, 6):
            addVector = True
            newX = (vector.x * math.cos(math.radians(rotate))) - (vector.y * math.sin(math.radians(rotate)))
            newY = (vector.x * math.sin(math.radians(rotate))) + (vector.y * math.cos(math.radians(rotate)))
            newVector =  Vector(newX, newY, vector, stall, vector.dist + 1)
            for obstacle in self.obstacles_known:
                if newVector.dist2(obstacle) < DANGER_ZONE+2.3:
                    addVector = False
            if addVector:
                newVectors.append(newVector)
            rotate += 15
        
        rotate = -15
        for i in range(0, 6):
            addVector = True
            newX = (vector.x * math.cos(math.radians(rotate))) - (vector.y * math.sin(math.radians(rotate)))
            newY = (vector.x * math.sin(math.radians(rotate))) + (vector.y * math.cos(math.radians(rotate)))
            newVector =  Vector(newX, newY, vector, stall, vector.dist + 1)
            for obstacle in self.obstacles_known:
                if newVector.dist2(obstacle) < DANGER_ZONE+2.3:
                    addVector = False
            if addVector:
                newVectors.append(newVector)
            rotate -= 15
        
        return newVectors
    
    #get the path of vectors chosen by a* search
    def get_astar_path(self, vector):
        print(vector)
        astar_path = []
        while vector.parent:
            astar_path.insert(0, vector)
            vector = vector.parent
        return astar_path
            
    # returns (x,y) of next stall we wanna visit
    def __next_stall(self) -> Vector:
        if len(self.stalls_next) == 0:
            return Vector(0,0)
        return Vector(self.stalls_next[0].x, self.stalls_next[0].y)
    
    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        #if you are at the next stall to visit, collect the item and remove the stall from the list
        counter = 0
        for stall in self.stalls_next:
            if stall.id == stall_id:
                self.stalls_next.pop(counter)
                if counter != 0:
                    print('Warning: The current stall is not the scheduled stall to visit.')
                break
            counter += 1

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        self.t_since_lkp = 0
        self.players_cached = [Vector(p[1],p[2]) for p in other_players]

        # update obstacles
        self.obstacles_known = [Vector(o[1],o[2]) for o in obstacles]

    def __avoid_players(self):
        for player in self.players_cached:
            if self.pos.dist2(player) < DANGER_ZONE:
                self.dir = self.pos.normalized_dir(player).left_90()
                break

    def __avoid_obstacles(self):
        for obstacle in self.obstacles_known:
            if self.pos.dist2(obstacle) < DANGER_ZONE+2.3:
                #self.dir = self.pos.normalized_dir(obstacle).left_90()
                self.aStarRoute  = self.__astar()
                # self.__update_tsp()
                print("avoiding obstacle")
                break

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        # theoretically, we would never encounter an obstacle
        # print("Warning: Encountered an obstacle.")
        self.prev_pos.update_val(self.pos)
        
        self.should_lookup = True
        print("encountered obstacle")

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        if len(self.stalls_next) == 0:
            self.dir = Vector(0,0)
            return 'move'
        if self.t_since_lkp>0:
            self.prev_pos.update_val(self.pos)
        self.t_since_lkp += 1
        self.pos = Vector(pos_x, pos_y) # update current position
        if self.pos.dist2(self.prev_pos) < self.vicinity: # if we are not moving
            self.dir = self.__randunit()
            # if self.players_cached:
            #     self.avoid_players()
            return 'move'
        elif len(self.aStarRoute) < 1:
            self.dir = self.pos.normalized_dir(self.__next_stall())
            self.__avoid_obstacles()
            # if self.players_cached:
            #     self.avoid_players()

        # if self.t_since_lkp>=HORIZON/2:
        if self.pos_last_lkp.dist2(self.pos) > 3 or self.should_lookup:
            self.pos_last_lkp.update_val(self.pos)
            # self.should_lookup = False
            # self.times_lkp += 1
            self.__update_tsp()
            return 'lookup move'
        
        # if self.times_lkp == 2:
        #     self.times_lkp = 0
        #     self.__update_tsp()
        
        return 'move'
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        if len(self.aStarRoute) > 0:
            print("position:")
            print(self.pos)
            print(self.aStarRoute)
            curr = self.aStarRoute[0]
            curr = self.pos.normalized_dir(curr)
            self.aStarRoute.pop(0)
            self.dir.x = curr.x
            self.dir.y = curr.y
            print(self.dir)
        return self.pos.x + self.dir.x, self.pos.y + self.dir.y
