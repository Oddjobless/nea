import numpy as np

from spatialmap import *
#

class Particle:
    def __init__(self, mass, radius, vector_field, damping):
        self.damping = damping
        self.radius = radius  # visual only
        self.mass = mass
        self.vector_field = vector_field

        self.velocity = np.array([randrange(-1000, 1000), randrange(-1000, 1000)])
        self.position = np.array([randrange(2 * self.radius, screen_width - 2 * self.radius),
                                  randrange(2 * self.radius, screen_height - 2 * self.radius)])
        self.next_position = self.position.copy()
        # self.acceleration = np.array([0,9.8]) * self.mass # short term
        self.vector_field.insert_particle(self)
        self.smoothing_radius = 2 * self.radius
        self.kernel = SmoothingKernel(smoothing_radius, poly_6=True)

        """self.spatial_map_update_frequency = 4  # 1 / 4 frames update the spatial map
        self.spatial_map_update_counter = 0"""

    def update(self, screen):

        self.next_position = self.position + self.velocity * dt
        if self.next_position[0] > screen.get_width() - (self.radius) or self.next_position[0] < self.radius:
            self.velocity[0] *= -1 * self.damping
        if self.next_position[1] > screen.get_height() - self.radius or self.next_position[1] < self.radius:
            self.velocity[1] *= -1 * self.damping
        self.next_position = np.clip(self.next_position, (self.radius, self.radius),
                                     (screen.get_width() - self.radius, screen.get_height() - self.radius))

        """if self.next_position[0] > screen.get_width() - (self.radius + 1):
            self.velocity[0] *= -1 * self.damping
            self.next_position[0] = screen.get_width() - self.radius - 1
        elif self.next_position[0] < self.radius:
            self.velocity[0] *= -1 * self.damping
            self.next_position[0] = self.radius + 1

        if self.next_position[1] > screen.get_height() - self.radius:
            self.velocity[1] *= -1 * self.damping
            self.next_position[1] = screen.get_height() - self.radius # - 1

        elif self.next_position[1] < self.radius:
            self.velocity[1] *= -1 * self.damping
            self.next_position[1] = self.radius"""

        """if self.spatial_map_update_counter == self.spatial_map_update_frequency:
            self.vector_field.remove_particle(self)
            self.position = self.next_position
            self.vector_field.insert_particle(self)
            self.spatial_map_update_counter = 0
            print(self.vector_field.grid)
        else:
            self.position = self.next_position
            self.spatial_map_update_counter += 1"""

        self.vector_field.remove_particle(self)
        self.position = self.next_position
        self.vector_field.insert_particle(self)

        # print(self.vector_field.grid)

        # self.velocity = self.velocity + self.acceleration * self.mass

    def calculate_density(self, particle):
        density = 0
        neighbouring_particles = self.vector_field.get_neighbouring_particles(particle)

        for neighbour_particle in neighbouring_particles:
            distance = self.vector_field.get_magnitude(neighbour_particle.position - particle.position)
            density += self.kernel.calculate_density_contribution(distance)
        density *= self.kernel.get_normalised_constant()

        self.density = density
        # (self.density)

        # density += self.mass / (self.get_magnitude(self.velocity) ** 2)
        # self.density = self.mass / (self.get_magnitude(self.velocity) *)

    def get_position(self):
        return int(self.next_position[0]), int(self.next_position[1])
