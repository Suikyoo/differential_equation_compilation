import pygame, random, math, core_functs

class ParticleSet(list):
    def particle_handler(self, map_layers, scroll):
        for i in self:
            i.update(map_layers[i.layer_loc], scroll)
            if not i.alive:
                self.remove(i)

    def spawn_particle(self, coords, vel, color):
        self.append(Particle(coords, vel, scale=random.randint(1, 2), color=color))

    def spawn_particle_by_angle(self, coords, angle, color):
        self.append(Particle(coords, [random.random() * math.cos(angle), random.random() * math.sin(angle)], scale=random.randint(1, 2), color=color))

    def spawn_particle_spread(self, coords, angle, color):
        self.spawn_particle_by_angle(coords, angle + math.pi/4 * random.randint(-20, 20)/20, color)

    def spawn_spark(self, coords, angle, color):
        self.append(Spark(coords, angle, random.random() * 1, scale=random.randint(1, 2), color=color))

    def spawn_spark_spread(self, coords, angle, color):
        self.spawn_spark(coords, angle + math.pi/4 * random.randint(-20, 20)/20, color)

    def spawn_shock_wave(self, center, thickness):
        self.append(ShockWave(center, thickness, speed=0.9, friction=0.03))

class Particle:
    def __init__(self, coords, velocity, scale=1, color=(255, 255, 255)):
        self.coords = list(coords).copy()
        self.velocity = list(velocity).copy()
        self.scale = scale
        self.color = color
        self.alive = True
        self.friction = [0.03, 0.009]
        self.douse = 0.03
        self.layer_loc = 2

    def move(self):
        self.velocity = [self.velocity[i] + core_functs.ferp(self.velocity[i], 0, self.friction[i]) for i in range(2)]
        self.coords = [self.coords[i] + self.velocity[i] for i in range(2)]

    def decay(self):
        self.scale = core_functs.clamp(self.scale - self.douse, (0, 10))
        if not self.scale: self.alive = False
    
    def draw(self, surf, scroll):
        pygame.draw.rect(surf, self.color, (*[self.coords[i] - scroll[i] for i in range(2)], *[self.scale] * 2))

    def update(self, surf, scroll):
        self.draw(surf, scroll)
        self.move()
        self.decay()

class Spark:
    def __init__(self, center, angle, speed, scale=1, friction=0.05, color=(255, 255, 255)):
        self.center = center
        self.angle = angle
        self.speed = speed
        self.scale = scale
        self.friction = friction
        self.color = color
        self.alive = True
        self.layer_loc = 2

    def move(self):
        self.center[0] += math.cos(self.angle) * self.speed
        self.center[1] += math.sin(self.angle) * self.speed

        self.speed -= self.friction
        if self.speed <= 0:
            self.alive = False
    def draw(self, surf, scroll):
        center = [self.center[i] - scroll[i] for i in range(2)]
        points = [
            [center[0] + math.cos(self.angle) * self.speed * self.scale, center[1] + math.sin(self.angle) * self.speed * self.scale],
            [center[0] + math.cos(self.angle + (math.pi/2)) * self.speed * self.scale * 0.3, center[1] + math.sin(self.angle + (math.pi/2)) * self.speed * self.scale * 0.3],
            [center[0] + math.cos(self.angle + math.pi) * self.speed  * self.scale * 3.5, center[1] + math.sin(self.angle + math.pi) * self.speed * self.scale * 3.5],
            [center[0] + math.cos(self.angle - (math.pi/2)) * self.speed * self.scale * 0.3, center[1] + math.sin(self.angle - (math.pi/2)) * self.speed * self.scale * 0.3]
        ]
        pygame.draw.polygon(surf, self.color, points)
    
    def update(self, surf, scroll):
        if self.alive:
            self.draw(surf, scroll)
            self.move()
 
class ShockWave:
    def __init__(self, center, thickness, speed=4, friction=0.08, color=(255, 255, 255)):
        self.center = center
        self.thickness = thickness
        self.speed = speed
        self.friction = friction
        self.color = color

        self.radius = 1
        self.alive = True

        self.layer_loc = 2

    def move(self):
        self.speed = core_functs.clamp(self.speed, (0, 10))
        if self.thickness <= 1 + self.friction: self.alive = False

        self.speed -= (self.friction/3)
        self.thickness -= self.friction
        self.radius += self.speed
        
    def draw(self, surf, scroll):
        pygame.draw.circle(surf, self.color, [self.center[i] - scroll[i] for i in range(2)], self.radius, int(self.thickness))
    
    def update(self, surf, scroll):
        self.draw(surf, scroll)
        self.move()

#not a particle but who cares
class Quake:
    def __init__(self):
        self.value = 0
    
    def get_quake(self):
        return random.randint(-20, 20)/100 * self.value

    def quake_handler(self):
        self.value = max(0, self.value - 1)
