import fast_tsp, math, random
from queue import Queue
from queue import PriorityQueue
from sys import maxsize as INT_MAX

random.seed(2023)

HORIZON = 10 # how far we can look
DANGER_ZONE = 0.5 # how close we can get to an obstacle/person
EPSILON = 0.001 # tolerance for floating point comparisons
WALL_BOUNDARY = 100

class Vector:    

    def __init__(self, _x, _y, _parent=None, _stall=None, _distTraveled=0):
        self.x = _x
        self.y = _y
        self.parent = _parent #parent of vector, used in a* search route
        self.stall = _stall #next stall of vector, used in a* search route
        self.dist = _distTraveled #distance traveled in route so far, used in a* search route

    #two vectors are equal if they have the same position
    def __eq__(self, other):
        direction =  (self.x == other.x) and (self.y == other.y)
        return direction
    
    # euclideian distance heuristic to the next stall, used for the priority queue in a* search
    def __lt__(self, other):
        self_d = self.dist2stall(self.stall)
        other_d = other.dist2stall(other.stall)
        return (self_d + self.dist) < (other_d + other.dist)
    
    def out_of_obstacle(self, obstacle) -> bool:
        """Whether the vector is outside of the obstacle."""
        if abs(self.x - obstacle.x)<=1:
            return abs(self.y - obstacle.y)>1.5+DANGER_ZONE
        if abs(self.y - obstacle.y)<=1:
            return abs(self.x - obstacle.x)>1.5+DANGER_ZONE
        return self.dist2stall(obstacle) > DANGER_ZONE+1.5

    def dist2stall(self, stall):
        """Shortest distance to a corner of the stall"""
        return min(self.dist2(Vector(stall.x+1, stall.y+1)), self.dist2(Vector(stall.x-1, stall.y+1)), self.dist2(Vector(stall.x-1, stall.y-1)), self.dist2(Vector(stall.x+1, stall.y-1)))
    
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
        return Vector(0,0) if dist<EPSILON else (other - self) / dist
    
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
        self.preprev_pos = Vector(-1, -1)
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
        self.should_lookup = True # there could be obstacles near to the initial position

        self.__tsp()
        self.times_lkp = 0

        self.dir = self.pos.normalized_dir(self.__next_stall()) # unit vector representing direction of movement
        self.phase1done = False 
    
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
    def __update_astar(self):
        #returns 12 directional vectors, each seperated by 30 degrees, that are possible moves from the current vector
        unitvec = self.__randunit()
        N = 6
        ds = [unitvec.rotate(theta*2*math.pi/N) for theta in range(N)]
        def aStar_expand(vector, stall):
            newvecs = list()
            for d in ds:
                newvec =  Vector(vector.x+d.x, vector.y+d.y, vector, stall, vector.dist + 1)
                fruitful = (newvec.dist2stall(stall) < 1)
                if newvec.x>0 and newvec.x<WALL_BOUNDARY and \
                    newvec.y>0 and newvec.y<WALL_BOUNDARY:
                        if fruitful:
                            if all(newvec.out_of_obstacle(obstacle) for obstacle in self.obstacles_known) and \
                                all(newvec.dist2(player) > DANGER_ZONE for player in self.players_cached):
                                newvecs.append(newvec)
                        elif all(newvec.dist2(obstacle) > DANGER_ZONE+1.75 for obstacle in self.obstacles_known) and \
                            all(newvec.dist2(player) > 2*DANGER_ZONE+1 for player in self.players_cached):
                            newvecs.append(newvec)
            return newvecs
        
        #get the path of vectors chosen by a* search
        def get_astar_path(vector):
            astar_path = []
            while vector.parent:
                astar_path.insert(0, vector)
                vector = vector.parent
            return astar_path

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
                    if curr.dist2stall(nextStall) < max(1, self.pos.dist2stall(nextStall) - 18) or curr.dist >= 20:
                        self.aStarRoute = get_astar_path(curr)
                        return
                    for child_vector in aStar_expand(curr, nextStall):
                        if (child_vector.x, child_vector.y) not in explored:
                            toExplore.put(child_vector)
        return
            
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
        self.aStarRoute = list()
        self.should_lookup = True

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        self.t_since_lkp = 0

        # update other players
        self.players_cached = [Vector(p[1],p[2]) for p in other_players]
        player_nearby = any(self.pos.dist2(player) < HORIZON/2 for player in self.players_cached)

        # update obstacles
        new_obstacle_observed = False
        for o in obstacles:
            ob = Vector(o[1],o[2])
            if ob not in self.obstacles_known:
                self.obstacles_known.append(ob)
                new_obstacle_observed = True
        # print(self.obstacles_known)

        # update astar path base on new info
        if self.should_lookup or player_nearby or new_obstacle_observed:
            self.__update_astar()

        self.should_lookup = False

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        # theoretically, we would never encounter an obstacle
        print("Warning: Encountered an obstacle.")
        self.preprev_pos.update_val(self.prev_pos)
        self.prev_pos.update_val(self.pos)
        self.should_lookup = True

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup move' or 'move'
        self.preprev_pos.update_val(self.prev_pos)
        self.prev_pos.update_val(self.pos)
        self.pos = Vector(pos_x, pos_y) # update current position
        self.t_since_lkp += 1

        if len(self.stalls_next) == 0:
            self.dir = Vector(0,0)
            return 'move'
            # if self.phase1done:
            #     self.dir = Vector(0,0)
            #     return 'move'
            # else:
            #     self.phase1done = True
            #     self.stalls_next.
        
        
        if self.pos.dist2(self.prev_pos) < EPSILON or self.pos.dist2(self.preprev_pos) < 0.5: # if we are oscilating/not moving
            self.dir = self.__randunit()
            npos = self.pos + self.dir
            while any(npos.dist2stall(obstacle) <= DANGER_ZONE for obstacle in self.obstacles_known) or any(npos.dist2(player) < DANGER_ZONE+2 for player in self.players_cached):
                self.dir = self.__randunit()
                npos = self.pos + self.dir
            self.should_lookup = True
            return 'move'

        if self.should_lookup \
            or self.pos.dist2(self.pos_last_lkp) >= (HORIZON-2* DANGER_ZONE)/2 \
            or any(self.pos.dist2(player) <= 2*(DANGER_ZONE+1) + self.t_since_lkp for player in self.players_cached):
            self.pos_last_lkp.update_val(self.pos)
            return 'lookup move'
        
        if len(self.aStarRoute) < 1 and any(self.pos.dist2(obstacle) < DANGER_ZONE+HORIZON for obstacle in self.obstacles_known):
            self.__update_astar()
        return 'move'
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        if len(self.stalls_next) == 0:
            return self.pos.x, self.pos.y
        
        self.dir = self.pos.normalized_dir(self.aStarRoute.pop(0)) \
            if len(self.aStarRoute) > 0 else \
            self.pos.normalized_dir(self.__next_stall())
        return self.pos.x + self.dir.x, self.pos.y + self.dir.y
