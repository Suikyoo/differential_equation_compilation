import sys, pygame, math

SCREEN_SIZE = (400, 400)

def get_distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def safe_divide(a, b):
    return a/b if b != 0 else 0

class Point:
    def __init__(self, loc):
        self.prev_loc = list(loc)
        self.loc = list(loc)
        self.origin_loc = loc
        self.velocity = [0, 0]
        self.acceleration = [0, 0]
        #{matrix loc : Point()}
        self.connected_points = {}
        self.grav_constant = 0.25
        self.motion_resistance = 0.005
        self.radius = 5
        self.pinned = False

    def event_handler(self, mouse_loc):
        self.loc = list(mouse_loc)
        
    def acceleration_handler(self):
        #try a more stick-like performance rather than this spring thing that never ends in its stretch
        self.acceleration[1] = self.grav_constant

    def location_handler(self, dt):
        future_loc = [self.loc[i] + (self.loc[i] - self.prev_loc[i]) * self.motion_resistance + self.acceleration[i] * self.motion_resistance * (dt ** 2) for i in range(2)]
        future_loc = [max(0, min(future_loc[i], SCREEN_SIZE[i])) for i in range(2)]
        self.prev_loc = self.loc.copy()
        self.loc = future_loc.copy()

    def draw(self, surf):
        #draw point
        pygame.draw.circle(surf, (255, 255, 255), self.loc, self.radius)

        #draw connection segments
        for k in self.connected_points:
            pygame.draw.line(surf, (255, 255, 255), self.loc, self.connected_points[k].loc, 5)
        
    def update(self, surf, dt):
        self.draw(surf)
        if not self.pinned:
            self.acceleration_handler()
            for i in range(5):
                self.location_handler(dt)
        else:
            self.loc = [i for i in self.origin_loc]


class Line:
    #a and b are points
    def __init__(self, a, b, l=20):
        self.a = a
        self.b = b
        self.length = l

    def update(self, surf):
        #constraints
        delta_pos = [self.a.loc[i] - self.b.loc[i] for i in range(2)]
        factor = 1 - safe_divide(self.length, get_distance(self.a.loc, self.b.loc))

        self.a.loc = [self.a.loc[i] - delta_pos[i] * factor * 0.5 for i in range(2)]
        self.b.loc = [self.b.loc[i] + delta_pos[i] * factor * 0.5 for i in range(2)]

        #display
        pygame.draw.line(surf, (255, 255, 255), self.a.loc, self.b.loc, 3)


class Mesh:
    def __init__(self, loc, size, dimension):
        self.loc = list(loc)
        self.size = list(size)
        self.dimension = list(dimension)

        self.point_map = {}
        self.lines = []
        
        self.set_mesh()

        
    def set_mesh(self):

        #create points
        for y in range(self.dimension[1]):
            for x in range(self.dimension[0]):
                idx = (x, y)
                point = Point([self.loc[i] + (self.size[i]/self.dimension[i]) * idx[i] for i in range(2)])
                self.point_map[idx] = point

        #create lines

        #row lines
        for y in range(self.dimension[1]):
            for x in range(self.dimension[0] - 1):
                self.lines.append(Line(self.point_map[(x, y)], self.point_map[(x + 1, y)]))

        
        #column lines
        for y in range(self.dimension[1] - 1):
            for x in range(self.dimension[0]):
                self.lines.append(Line(self.point_map[(x, y)], self.point_map[(x, y + 1)]))
        
    def update(self, surf, dt):
        for line in self.lines:
            line.update(surf)

        for k in self.point_map:
            self.point_map[k].update(surf, dt)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.time = pygame.time.Clock()
        self.mesh = Mesh((100, 50), (200, 200), (10, 10))
        self.target_points = {}
        self.mouse_down = False
        self.prev_mouse_pos = pygame.mouse.get_pos()
        self.select_radius = 50
        self.mesh.point_map[(0, 0)].pinned = True
        self.mesh.point_map[(self.mesh.dimension[0] - 1, 0)].pinned = True

    def game(self):
        while True:
            dt = self.time.tick(60)
            
            mouse_press = False
            mouse_pos = pygame.mouse.get_pos()
            
            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if i.type == pygame.MOUSEBUTTONDOWN:
                    if i.button == 1:
                        self.mouse_down = True

                if i.type == pygame.MOUSEBUTTONUP:
                    if i.button == 1:
                        self.mouse_down = False
                        self.target_points = {}

            if not len(self.target_points):
                if self.mouse_down:
                    for k in self.mesh.point_map:
                        if get_distance(self.mesh.point_map[k].loc, mouse_pos) <= self.mesh.point_map[k].radius + self.select_radius:
                            self.target_points[tuple([self.mesh.point_map[k].loc[i] - mouse_pos[i] for i in range(2)])] = self.mesh.point_map[k]

            else:
                for loc in self.target_points.keys():
                    self.target_points[loc].loc = [mouse_pos[i] + loc[i] for i in range(2)]
                        

            self.prev_mouse_pos = mouse_pos
            self.screen.fill((0, 0, 0))
            
            self.mesh.update(self.screen, dt)

            pygame.display.update()

Game().game()
