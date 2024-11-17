import pygame, orbit, random

class World:
    def __init__(self):
        #use tuples for the center loc since orbital_point don't change much I think 
        self.main_orbit = orbit.Orbit((200, 130), 70, color=random.choice(orbit.orbit_colors), width=3)

        self.octaves = 6

        current_orbit = self.main_orbit
        for i in range(self.octaves):
            current_orbit.create_sub_orbit()
            current_orbit = current_orbit.sub_orbit

             


    def update(self, surf):
        self.main_orbit.update(surf)
