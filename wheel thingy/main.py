import sys, pygame, world

pygame.init()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 520))
        self.display_surf = pygame.Surface([i/2 for i in self.screen.get_size()])
        self.clock = pygame.time.Clock()

    def set_world(self):
        self.world = world.World()
        self.run()

    def run(self):
        while True:
            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.display_surf.fill((0, 0, 0))
                
            self.world.update(self.display_surf)

            self.screen.blit(pygame.transform.scale(self.display_surf, self.screen.get_size()), (0, 0))

            pygame.display.update()

Game().set_world()
