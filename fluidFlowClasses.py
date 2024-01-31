
# import numpy as np

from baseClasses import *
#

class FluidParticle(Particle):
    def __init__(self, mass, radius, vector_field, damping):
        super().__init__(mass, radius, vector_field, damping)
        self.damping = damping
        self.radius = radius  # visual only
        self.mass = mass
        self.vector_field = vector_field
        self.force = np.zeros(2, dtype=float)

        # self.velocity = np.array([randrange(-200, 200), randrange(-200, 200)]) # poo
        self.velocity = np.zeros(2, dtype=float)
        print(self.position)
        self.position = np.array([randint(2 * self.radius, screen_width - 2 * self.radius), randint(2 * self.radius, screen_height - 2 * self.radius)], dtype=float)
        print("Adsf", self.position)



        self.calculate_density()
        self.calculate_pressure()

        """self.spatial_map_update_frequency = 4  # 1 / 4 frames update the spatial map
        self.spatial_map_update_counter = 0"""

    def update(self, screen):
        super().update(screen)

        self.calculate_density()  # todo i want it to do this less often
        self.calculate_pressure()

        # self.force = self.calculate_pressure_force()



    def apply_forces(self):
        # todo ditto
        self.force = np.zeros_like(self.velocity)
        self.force = self.force - self.calculate_pressure_force()


        self.velocity = dt * np.array((self.force / self.mass), dtype=float)

    def calculate_density(self): # can i use self instead?
        density = 0
        neighbouring_particles = self.vector_field.get_neighbouring_particles(self)

        for neighbour_particle in neighbouring_particles:
            distance = self.vector_field.get_magnitude(neighbour_particle.position - self.position)
            density += self.vector_field.kernel.calculate_density_contribution(distance) * neighbour_particle.mass



        # print(self.density == density)
        self.density = density

        # self.calculate_pressure()


        # (self.density)

        # density += self.mass / (self.get_magnitude(self.velocity) ** 2)
        # self.density = self.mass / (self.get_magnitude(self.velocity) *)

    def get_pressure_force(self): # interpolate pressure force
        return self.pressure

    def calculate_pressure(self): # ideal gas law
        self.pressure = stiffness_constant * (self.density - self.vector_field.rest_density)

    def calculate_property(self):
        property = 0
        neighbouring_particles = self.vector_field.get_neighbouring_particles(self)

        for neighbour_particle in neighbouring_particles:
            distance = self.vector_field.get_magnitude(neighbour_particle.position - self.position)
            influence = self.vector_field.kernel.calculate_density_contribution(distance)
            property += influence * (neighbour_particle.mass / neighbour_particle.density)



        # print(self.density == density)
        return self.vector_field.kernel.get_normalised_density(property)

    def calculate_pressure_force(self):
        pressure_force = np.zeros(2, dtype=float)
        neighbouring_particles = self.vector_field.get_neighbouring_particles(self)

        for neighbour_particle in neighbouring_particles:
            if neighbour_particle == self:
                continue
            vector = neighbour_particle.position - self.position
            distance = self.vector_field.get_magnitude(vector)
            if distance == 0:
                direction_vector = np.random.rand(2)
            else:
                direction_vector = self.vector_field.normalise_vector(vector)
            influence = self.vector_field.pressure_kernel.calculate_density_contribution(distance)
            avg_pressure = 0.5 * (self.pressure + neighbour_particle.pressure)
            if neighbour_particle.density != 0:
                pressure_force += direction_vector * influence * avg_pressure * (neighbour_particle.mass / neighbour_particle.density)

        return pressure_force

    def get_density(self):
        return self.density

    def get_position(self):
        return int(self.next_position[0]), int(self.next_position[1])













class SmoothingKernel:
    def __init__(self, smoothing_length, poly_6=False, gaussian=False, cubic_spline=False, spiky=False):
        self.h = smoothing_length / 2 if cubic_spline else smoothing_length  # the radius within which a neighbouring particle will have an impact

        self.cubic_spline = cubic_spline
        self.poly_6 = poly_6
        self.gaussian = gaussian
        self.spiky = spiky
        if poly_6:
            self.normalisation_constant = 315 / (64 * np.pi * self.h**4) # ** 9
        elif gaussian:
            self.normalisation_constant = 1 / (np.sqrt(2 * np.pi) * self.h)
        elif cubic_spline:
            self.normalisation_constant = 10 / (7 * np.pi * self.h**2)
        elif spiky:
            self.normalisation_constant = 15 / (np.pi * (self.h ** 2)) # ** 6


        # im uneased by this normalisation constant, tempted to just use total mass instead

    def calculate_density_contribution(self, particle_radius):

        if self.poly_6:
            print(self.poly_6_kernel(particle_radius))
            return self.poly_6_kernel(particle_radius)


        elif self.cubic_spline:
            return self.cubic_spline_kernel(particle_radius)

        elif self.gaussian:
            return self.gaussian_kernel(particle_radius)

        elif self.spiky:
            return self.spikey_kernel(particle_radius)

        raise ValueError("Unknown kernel type")

    def get_normalised_density(self, density):
        return self.normalisation_constant * density

    def cubic_spline_kernel(self, particle_radius): # Article. Numerical Model of Oil Film Diffusion in Water Based on SPH Method
        ratio = particle_radius / self.h

        if 0 <= ratio < 1:
            return (1 - (1.5 * ratio ** 2) + (0.75 * ratio ** 3))
        elif 1 <= ratio < 2:
            return 0.25 * ((2 - ratio) ** 3)
        else:
            return 0

    def poly_6_kernel(self, particle_radius):
        if particle_radius <= self.h:
            return self.normalisation_constant * ((self.h ** 2 - particle_radius ** 2) ** 3)
        return 0

    def gaussian_kernel(self, particle_radius):
        return 0 # :(

    def spikey_kernel(self, particle_radius):
        if particle_radius <= self.h:
            return self.normalisation_constant * (self.h - particle_radius) ** 3
        return 0


class FluidSpatialMap(SpatialMap):
    def __init__(self, noOfRows, noOfCols):
        super().__init__(noOfRows, noOfCols)
        self.rest_density = 100 # A ROUGH ESTIMATE BASED ON INTIAL POS OF PARTICLES
        # USER SHOULD ADJUST AS PER NEEDED
        self.smoothing_radius = box_width
        self.kernel = SmoothingKernel(self.smoothing_radius, poly_6=True)
        self.pressure_kernel = SmoothingKernel(self.smoothing_radius, spiky=True)









    def calculate_rest_density(self, particle_list):
        total_density = 0
        for particle in particle_list:
            total_density += particle.density
            print(total_density, "\n\n==")

        self.set_rest_density(total_density / noOfParticles)  # rest density

    def set_rest_density(self, rest_density):
        self.rest_density = rest_density







if __name__ == "__main__":
    field = SpatialMap(rows, columns)

