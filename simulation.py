import pygame
import sys
pygame.init()
import numpy as np
from random import randrange

clock = pygame.time.Clock()
frame_rate = 60
dt = 1 / frame_rate

class Particle():
    def __init__(self, mass, radius, damping=0.8):
        self.damping = damping
        self.radius = radius
        self.mass = mass
        self.velocity = np.array([randrange(-400,400),randrange(-400,400)])
        #self.displacement = np.array([50,50])
        self.displacement = np.array([randrange(self.radius, 800 - self.radius), randrange(self.radius, 800 - self.radius)])
        self.acceleration = np.array([0,9.8]) * self.mass

    def update(self, screen):
        new_displacement = self.displacement + self.velocity * dt

        if new_displacement[0] > screen.get_width() - (self.radius + 1):
            self.velocity[0] *= -1 * self.damping
            new_displacement[0] = screen.get_width() - self.radius - 1
        elif new_displacement[0] < self.radius:
            self.velocity[0] *= -1 * self.damping
            new_displacement[0] = self.radius + 1

        if new_displacement[1] > screen.get_height() - self.radius:
            self.velocity[1] *= -1 * self.damping
            new_displacement[1] = screen.get_height() - self.radius # - 1

        elif new_displacement[1] < self.radius:
            self.velocity[1] *= -1 * self.damping
            new_displacement[1] = self.radius

        self.displacement = new_displacement
        self.velocity = self.velocity + self.acceleration * self.mass


    def get_position(self):
        return int(self.displacement[0]), int(self.displacement[1])



def run():
    screen = pygame.display.set_mode((1600,1000))
    pygame.display.set_caption("Pygame Boilerplate")

    particles = [Particle(0.8, 15),Particle(0.5, 15),Particle(0.5, 15),Particle(0.5, 15),Particle(0.5, 15),Particle(0.5, 15),Particle(0.5, 15),Particle(0.5, 15)]


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        screen.fill((255, 69, 180))


        # logic goes here

        # Drawing code goes here

        for particle in particles:
            particle.update(screen)
            pygame.draw.circle(screen, (123,12,90), particle.get_position(), particle.radius)


        # Update display

        pygame.display.update()

        clock.tick(frame_rate)

    return

if __name__ == "__main__":
    run()
