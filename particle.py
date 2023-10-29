from vector_field import *

class Particle:
    def __init__(self, mass, radius, vector_field, damping=0.8):
        self.damping = damping
        self.radius = radius
        self.mass = mass
        self.vector_field = vector_field

        self.velocity = np.array([randrange(-1000,1000),randrange(-1000,1000)])
        self.position = np.array([randrange(self.radius, screen_width - self.radius), randrange(self.radius, screen_height - self.radius)])
        # self.acceleration = np.array([0,9.8]) * self.mass # short term

    def update(self, screen):
        new_position = self.position + self.velocity * dt

        if new_position[0] > screen.get_width() - (self.radius + 1):
            self.velocity[0] *= -1 * self.damping
            new_position[0] = screen.get_width() - self.radius - 1
        elif new_position[0] < self.radius:
            self.velocity[0] *= -1 * self.damping
            new_position[0] = self.radius + 1

        if new_position[1] > screen.get_height() - self.radius:
            self.velocity[1] *= -1 * self.damping
            new_position[1] = screen.get_height() - self.radius # - 1

        elif new_position[1] < self.radius:
            self.velocity[1] *= -1 * self.damping
            new_position[1] = self.radius

        self.position = new_position
        # self.velocity = self.velocity + self.acceleration * self.mass


    def get_position(self):
        return int(self.position[0]), int(self.position[1])