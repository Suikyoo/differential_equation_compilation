import pygame, math, random, core_functs

orbit_colors = [(153, 106, 247), (202, 146, 209)]
# (222, 114, 42)

class Orbit:
    def __init__(self, center, radius, color=(255, 255, 255), width=1):
        #this setup assumes orbital center to be the center of the wheel
        #this defaults to a rotating orbit

        #wheel
        self.wheel_radius = radius
        self.wheel_angle = 0

        #angle relative to the mouse at first click
        self.virtual_angle = 0
        self.angle_vel = 0
        self.spring_const = 0.0001
        self.point_mass = 5
        self.mouse_pressed = False
        self.color = color
        self.width = width


        #orbit
        self.orbit_angle = 0
        self.orbit_radius = 0
        self.orbit_point = center
        self.colors = [(209, 98, 214), (255, 219, 136), (248, 13, 100), (133, 192, 90), (0, 179, 245)]
        self.spread = 0
        #self.img = pygame.image.load("img.jpg")

        self.sub_orbit = None

    def create_sub_orbit(self):
        self.sub_orbit = Orbit(self.get_wheel_center(), min(max(random.random(), 0.6), 0.8) * self.wheel_radius, color=random.choice(orbit_colors), width=random.randint(1, 6))
        self.sub_orbit.orbit_point = self.get_wheel_center()
        self.sub_orbit.orbit_radius = self.wheel_radius - self.sub_orbit.wheel_radius

    def get_wheel_center(self):
        return [self.orbit_point[i] + core_functs.trig_functs[i](self.orbit_angle) * self.orbit_radius for i in range(2)]

    def physics(self):

        #calculations need to be in radians
        if pygame.mouse.get_pressed()[0]:
            center = self.get_wheel_center()

            mouse_pos = [round(i/2) for i in pygame.mouse.get_pos()]

            if not self.mouse_pressed:
                self.virtual_angle = core_functs.get_angle(center, mouse_pos)
                self.mouse_pressed = True


            virtual_point = [center[i] + self.wheel_radius * core_functs.trig_functs[i](self.virtual_angle) for i in range(2)]
            virtual_acc = -(self.spring_const * core_functs.get_distance(mouse_pos, virtual_point))/self.point_mass
            #vecs are in the form of (x, y)
            vec1 = [mouse_pos[i] - virtual_point[i] for i in range(2)]
            vec2 = [center[i] - virtual_point[i] for i in range(2)][::-1]
            vec2[0] = -vec2[0]

            tangent_angle = math.atan2(*vec1[::-1]) - math.atan2(*vec2[::-1])
            #a.b = |a||b|cos0
            #a.b/|a||b|=cos0
            #0 = cos^-1(a.b/|a||b|)

            tangent_acc = virtual_acc*math.cos(tangent_angle)
            angular_acc = tangent_acc/self.wheel_radius
        else: 
            self.mouse_pressed = False
            angular_acc = 0

        self.angle_vel += angular_acc - (self.angle_vel * 0.003)
        self.virtual_angle += self.angle_vel

        self.wheel_angle += self.angle_vel
        self.orbit_angle += -self.angle_vel * (core_functs.divide(self.wheel_radius, self.orbit_radius + self.wheel_radius))

    def draw(self, surf):
        center = self.get_wheel_center()
        for i in range(8):
            fract_angle = 2 * math.pi / 8
            point_1 = center
            point_2 = [center[j] + self.wheel_radius * core_functs.trig_functs[j](self.wheel_angle + i * fract_angle) for j in range(2)]
            point_3 = [center[j] + self.wheel_radius * core_functs.trig_functs[j](self.wheel_angle + (i + 1) * fract_angle) for j in range(2)]
            points = [point_1, point_2, point_3]
            points = [[p[j] + core_functs.trig_functs[j](self.wheel_angle + i * fract_angle) * self.spread for j in range(2)] for p in points]

            pygame.draw.polygon(surf, self.colors[i%len(self.colors)], points)
            pygame.draw.polygon(surf, (255, 255, 255), points, width=4)

        #if self.mouse_pressed:
        #    pygame.draw.line(surf, (255, 180, 0), [center[i] + (self.spread + self.wheel_radius) * core_functs.trig_functs[i](self.virtual_angle) for i in range(2)], [round(p/2) for p in pygame.mouse.get_pos()], 5)
        #pygame.draw.circle(surf, self.color, center, self.wheel_radius, self.width)
        #pygame.draw.circle(surf, (235, 232, 157), [center[i] + core_functs.trig_functs[i](self.wheel_angle) * self.wheel_radius for i in range(2)], self.width)

    def update(self, surf):
        self.physics()
        self.draw(surf)

        if self.sub_orbit:
            self.sub_orbit.orbit_point = self.get_wheel_center()
            self.sub_orbit.update(surf)

