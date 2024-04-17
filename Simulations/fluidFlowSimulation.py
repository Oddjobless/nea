from Simulations.SimulationFiles.baseClasses import *
import pygame

def run():
    pygame.init()
    screen_width, screen_height = 1920, 1080
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Ideal Gas Law Simulation (deprecated)")
    rows, columns = 18, 32

    vector_field = FluidSpatialMap(rows, columns)
    frame_rate = vector_field.frame_rate
    particles = [FluidParticle(1, 3, vector_field) for _ in range(noOfParticles)]
    print("high")
    vector_field.calculate_rest_density(particles)

    clock = pygame.time.Clock()


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    return


        # drawing grid
        screen.fill((90, 69, 50))
        if vector_field.draw_grid:

            for x in vector_field.get_grid_coords(x=True):
                pygame.draw.line(screen, "#353252", (x, 0), (x, screen_height), 1)

            for y in vector_field.get_grid_coords(y=True):
                pygame.draw.line(screen, "#353252", (0, y), (screen_width, y), 1)


            """for coord, vector in zip(container.get_grid_coords(), container.get_normalised_grid()):
                boxCentre = (coord[0] + box_width/2, coord[1] + box_height/2)
                lineRadius = vector
                #pygame.draw.circle(screen, "#ff3542", (boxCentre), 4, 4)"""

#
        # logic goes here
        for particle in particles:
            particle.update_density() # must be done separately from pressure and viscosity calculations

        for particle in particles:
            particle.update_pressure()
            particle.calculate_pressure_force()
            particle.update(screen)
            pygame.draw.circle(screen, (123, 12, 90), particle.position, particle.radius)

        pygame.display.update()


        clock.tick(frame_rate)



class FluidParticle(Particle):
    def __init__(self, mass, radius, spatial_map):
        super().__init__(mass, radius, spatial_map)
        self.radius = radius  # visual only
        self.mass = mass
        self.spatial_map = spatial_map
        self.force = np.zeros(2, dtype=float)
        self.stiffness_constant = 10 # used for pressure
        # self.velocity = np.array([randrange(-200, 200), randrange(-200, 200)]) # poo
        self.velocity = np.zeros(2, dtype=float) # initially no velcity
        self.position = np.array([randint(2 * self.radius, 1920 - 2 * self.radius),
                                  randint(2 * self.radius, 1080 - 2 * self.radius)], dtype=float)

        self.pressure_force = np.zeros(2, dtype=float)
        self.density = None
        self.pressure = None
        self.calculate_density()
        self.calculate_pressure()



    def update(self, screen): # overriding parent method
        self.next_position = self.position + self.velocity * self.container.dt
        if self.next_position[0] > screen.get_width() - (self.radius) or self.next_position[
            0] < self.radius:  # or within blocked cell
            # out of bounds
            self.velocity[0] *= -1 * self.damping
        if self.next_position[1] > screen.get_height() - self.radius or self.next_position[1] < self.radius:

            self.velocity[1] *= -1 * self.damping

        self.next_position = np.clip(self.next_position, (self.radius, self.radius),
                                     (screen.get_width() - self.radius, screen.get_height() - self.radius))

        self.spatial_map.remove_particle(self)
        self.position = self.next_position
        self.spatial_map.insert_particle(self)




    def update_density(self):
        self.calculate_density()

    def update_pressure(self):
        self.calculate_pressure()

    def apply_forces(self): # apply the navier-stokes equation to get delta velocity
        self.force = np.zeros_like(self.velocity)
        self.force = self.force + self.calculate_pressure_force()

        self.velocity += self.container.dt * np.array((self.force / self.mass), dtype=float)

    def calculate_density(self):
        density = 0
        neighbouring_particles = self.spatial_map.get_neighbouring_particles(self)

        for neighbour_particle in neighbouring_particles:
            if neighbour_particle != self: # don't include self in density
                distance = self.spatial_map.get_magnitude(neighbour_particle.position - self.position)
                influence = self.spatial_map.kernel.calculate_density_contribution(distance)
                density += influence * neighbour_particle.mass # scale by particle's mass

        self.density = density

    def get_pressure_force(self):  # interpolate pressure force
        return self.pressure

    def calculate_pressure(self):  # ideal gas law application
        self.pressure = self.stiffness_constant * (self.density - self.spatial_map.rest_density)

    def calculate_property(self): # generic property finder, like for pressure
        property = 0
        neighbouring_particles = self.spatial_map.get_neighbouring_particles(self)

        for neighbour_particle in neighbouring_particles:
            distance = self.spatial_map.get_magnitude(neighbour_particle.position - self.position)
            influence = self.spatial_map.kernel.calculate_density_contribution(distance)
            property += influence * (neighbour_particle.mass / neighbour_particle.density)

        return property



    def calculate_pressure_force(self):
        self.pressure_force = np.zeros(2, dtype=float)
        neighbouring_particles = self.spatial_map.get_neighbouring_particles(self)
        for neighbour_particle in neighbouring_particles: # Use pressure of neighbouring particles
            if self != neighbour_particle:
                distance = self.spatial_map.get_magnitude(self.position - neighbour_particle.position)
                self.pressure_force -= self.calculate_pressure_contribution(self, neighbour_particle, distance)
        self.velocity += self.container.dt * self.pressure_force / self.mass
    def calculate_pressure_contribution(self, particle, neighbour_particle, dist):
        # similar function to self.calculate_pressure_force. Currently testing this implementation
        direction_vector = self.spatial_map.normalise_vector(particle.position - neighbour_particle.position)
        if particle.density == 0 or neighbour_particle.density == 0:
            return np.array([0,0])
        pressure = particle.pressure / (particle.density ** 2)
        neighbour_pressure = neighbour_particle.pressure / (neighbour_particle.density ** 2)
        smoothing_kernel_gradient = self.spatial_map.kernel.cubic_spline_kernel_gradient(dist)
        pressure_force = -neighbour_particle.mass * 0.5 * (
                pressure + neighbour_pressure) * smoothing_kernel_gradient * direction_vector
        return pressure_force

    def get_density(self):
        return self.density

    def get_position(self):
        return int(self.next_position[0]), int(self.next_position[1])


class SmoothingKernel:
    def __init__(self, smoothing_length, poly_6=False, gaussian=False, cubic_spline=False, spiky=False, test=True):
        # the radius within which a neighbouring particle will have an impact
        self.h = smoothing_length / 2 if cubic_spline else smoothing_length

        # the chosen smoothing_kernel
        self.cubic_spline = cubic_spline
        self.poly_6 = poly_6
        self.gaussian = gaussian
        self.spiky = spiky
        self.test = test

        if poly_6:
            self.normalisation_constant = 315 / (64 * np.pi * self.h ** 2)  # ** 9
        elif gaussian:
            self.normalisation_constant = 1 / (np.sqrt(2 * np.pi) * self.h)
        elif cubic_spline:
            self.normalisation_constant = 10 / (7 * np.pi * self.h ** 2)
        elif spiky:
            self.normalisation_constant = 15 / (np.pi * (self.h ** 6))  # ** 6
        elif test:
            self.normalisation_constant = 1

    def calculate_density_contribution(self, particle_radius):

        if self.poly_6:
            return self.poly_6_kernel(particle_radius)


        elif self.cubic_spline:
            return self.cubic_spline_kernel(particle_radius)

        elif self.gaussian:
            return self.gaussian_kernel(particle_radius)

        elif self.spiky:
            return self.spikey_kernel(particle_radius)

        elif self.test:
            return self.test_kernel(particle_radius)
        raise ValueError("Unknown kernel type")

    def get_normalised_density(self, density):
        return self.normalisation_constant * density

    def test_kernel(self, particle_radius):
        return ((max(0, particle_radius ** 2 - self.h ** 2)) ** 3) / (np.pi * self.h ** 2 / 4)

    def cubic_spline_kernel(self,
                            particle_radius):  # Article. Numerical Model of Oil Film Diffusion in Water Based on SPH Method
        ratio = particle_radius / self.h

        if 0 <= ratio < 1:
            return (1 - (1.5 * ratio ** 2) + (0.75 * ratio ** 3))
        elif 1 <= ratio < 2:
            return 0.25 * ((2 - ratio) ** 3)
        else:
            return 0

    def cubic_spline_kernel_gradient(self, particle_radius):
        ratio = particle_radius / self.h
        if 0 <= ratio < 1:
            return -3 * ratio
        elif 1 <= ratio < 2:
            return -0.75 * (2 - ratio) ** 2
        else:
            return 0

    def poly_6_kernel(self, particle_radius):
        if particle_radius <= self.h: # if particle is within smoothing radius
            return self.normalisation_constant * ((self.h ** 2 - particle_radius ** 2) ** 3)
        return 0

    def gaussian_kernel(self, particle_radius):
        return 0  # :(

    def spikey_kernel(self, particle_radius):
        if particle_radius <= self.h:
            return self.normalisation_constant * (self.h - particle_radius) ** 3

        return 0


class FluidSpatialMap(SpatialMap):
    def __init__(self, noOfRows, noOfCols):
        screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        super().__init__(noOfRows, noOfCols, screen_size=screen_size)
        self.rest_density = 100  # Tinker until reaching desired effect
        self.smoothing_radius = self.box_width # To ensure that spatial grid can be used
        self.kernel = SmoothingKernel(self.smoothing_radius, cubic_spline=True)
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
    rows, cols = 18, 32
    field = SpatialMap(rows, cols)

if __name__ == "__main__":
    run()