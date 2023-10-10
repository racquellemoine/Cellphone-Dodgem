import fast_tsp, math, random
from sys import maxsize as INT_MAX

random.seed(2)

HORIZON = 10 # how far we can look
DANGER_ZONE = 0.5 # how close we can get to an obstacle/person

class Vector:
    def __init__(self, _x, _y):
        self.x = _x
        self.y = _y
    
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

class Player:
    def __init__(self, id, name, color, initial_pos_x, initial_pos_y, stalls_to_visit, T_theta, tsp_path, num_players):
        self.id = id
        self.name = name
        self.color = color
        self.pos = Vector(initial_pos_x, initial_pos_y)
        self.all_stalls = stalls_to_visit
        self.stalls_next = list()

        self.obstacles_known = list()
        self.players_cached = list()
        self.t_since_lkp = INT_MAX
        self.last_ckpt = Vector(initial_pos_x, initial_pos_y)

        self.T_theta = T_theta
        self.tsp_path = tsp_path
        self.num_players = num_players

        self.dir = Vector(1, 0) # unit vector representing direction of movement
        # self.next_ckpt = Vector(initial_pos_x, initial_pos_y) # next lookup checkpoint       
        # self.epsilon = 0.0005 # tolerance for reaching a checkpoint
        self.__tsp()
    
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
        for i in self.tsp_path[1:]:
            self.stalls_next.append(self.all_stalls[i-1])

    # returns (x,y) of next stall we wanna visit
    def __next_stall(self) -> Vector:
        if len(self.stalls_next) == 0:
            return Vector(0,0)
        return Vector(self.stalls_next[0].x, self.stalls_next[0].y)
    
    # simulator calls this function when the player collects an item from a stall
    def collect_item(self, stall_id):
        #if you are at the next stall to visit, collect the item and remove the stall from the list
        if stall_id == self.stalls_next[0].id:
            self.stalls_next.pop(0)
        print('Warning: The current stall is not the scheduled stall to visit.')

    # simulator calls this function when it passes the lookup information
    # this function is called if the player returns 'lookup' as the action in the get_action function
    def pass_lookup_info(self, other_players, obstacles):
        self.t_since_lkp = 0
        self.players_cached = [Vector(p[1],p[2]) for p in other_players]
        self.dir = self.pos.normalized_dir(self.__next_stall())

    # simulator calls this function when the player encounters an obstacle
    def encounter_obstacle(self):
        # theoretically, we would never encounter an obstacle
        self.dir = self.dir.left_90() if random.random()<0.5 else self.dir.right_90()
        print(self.dir.x, self.dir.y)
        print('Warning: Encountered obstacle.')

    # simulator calls this function to get the action 'lookup' or 'move' from the player
    def get_action(self, pos_x, pos_y):
        # return 'lookup' or 'move'
        self.t_since_lkp += 1
        self.pos = Vector(pos_x, pos_y) # update current position
        return 'lookup' if self.t_since_lkp>=HORIZON/2 or any([self.pos.dist2(p)<=DANGER_ZONE+self.t_since_lkp for p in self.players_cached]) else 'move'
    
    # simulator calls this function to get the next move from the player
    # this function is called if the player returns 'move' as the action in the get_action function
    def get_next_move(self):
        return self.pos.x + self.dir.x, self.pos.y + self.dir.y
