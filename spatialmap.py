# Programming and drawing vector field
import pygame
import numpy as np
from random import randrange
#
screen_width, screen_height = 940, 940
rows, columns = 8,8
box_width, box_height = screen_width / columns, screen_height / rows

clock = pygame.time.Clock()

frame_rate = 75  # frames per second
dt = 1 / frame_rate  # time elapsed between frames
radius = 8  # radius of particles, purely for visualisation
noOfParticles = 2  # number of particles.
damping = 0.99  # what percentage of energy the particles keep on collision with boundary
drawGrid = True  # draw the grid lines on the screen
using_poly_6 = True  #
using_cubic_spline_kernel = True
smoothing_radius = min(box_height, box_width) # will integrate this into program.
stiffness_constant = 2500


# The fixed-radius near neighbour problem. naive approach = O(n^2)
# width should be equal to smoothing radius, do 2 * radius
# dense spatial grid table
# https://www.youtube.com/watch?v=D2M8jTtKi44

class SmoothingKernel:
    def __init__(self, smoothing_length, poly_6=False, gaussian=False, cubic_spline=False):
        self.h = smoothing_length / 2 if cubic_spline else smoothing_length  # the radius within which a neighbouring particle will have an impact

        self.cubic_spline = cubic_spline
        self.poly_6 = poly_6
        self.gaussian = gaussian
        if poly_6:
            self.normalisation_constant = 315 / (64 * np.pi * self.h**9)
        elif gaussian:
            self.normalisation_constant = 1 / (np.sqrt(2 * np.pi) * self.h)
        elif cubic_spline:
            self.normalisation_constant = 10 / (7 * np.pi * self.h**2)


        # im uneased by this normalisation constant, tempted to just use total mass instead

    def calculate_density_contribution(self, particle_radius):

        if self.poly_6:
            return self.poly_6_kernel(particle_radius)

        elif self.cubic_spline:
            return self.cubic_spline_kernel(particle_radius)

        elif self.gaussian:
            return self.gaussian_kernel(particle_radius)


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
            return abs((self.h ** 2 - particle_radius ** 2) ** 3)
        return 0

    def gaussian_kernel(self, particle_radius):
        return 0 # explain why bad

    def calculate_pressure_contribution(self, particle_radius):
        pass

class SpatialMap:
    def __init__(self, noOfRows, noOfCols):
        self.noOfRows = noOfRows
        self.noOfCols = noOfCols
        self.grid = [set() for _ in
                     range(noOfRows * noOfCols)]  # numpy not useful here because it's constantly changing size??
        # I WANT TO MAKE SELF.HASH INTO A 1D ARRAY
        # self.grid = np.empty((noOfRows, noOfCols))
        # self.grid.fill(set()) # would like to test speed difference

        ### creating vector field
        self.vectorField = list(map(self.normalise_vector, np.random.rand(self.noOfRows * self.noOfCols, 2)))
        self.rest_density = -1 # A ROUGH ESTIMATE BASED ON INTIAL POS OF PARTICLES
        #  CAN CALCULATE ACCURATE REST DENSITY BY SPACING OUT PARTICLES AND CALCULATING DENSITIES

    def get_grid_coords(self, x=False, y=False):
        xCoords = np.linspace(0, screen_width, self.noOfCols, endpoint=False)
        if x:
            return xCoords

        yCoords = np.linspace(0, screen_height, self.noOfRows, endpoint=False)
        if y:
            return yCoords

        xValues, yValues = np.array(np.meshgrid(xCoords, yCoords))
        coords = np.column_stack((xValues.ravel(), yValues.ravel()))
        return coords

    def hash_position(self, position):
        return self.coord_to_index(int(position[0] / box_width), int(position[1] / box_height))

    def coord_to_index(self, x, y):
        # print(x, y, x + (y * self.noOfCols))
        return x + y * self.noOfCols

    def update_particle(self, particle):
        self.remove_particle(particle)
        self.insert_particle(particle)

    def get_neighbouring_particles(self, particle):
        cell_row, cell_col = divmod(self.hash_position(particle.position), self.noOfCols)
        neighbouring_particles = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbour_row, neighbour_col = cell_row + i, cell_col + j
                if 0 <= neighbour_row < self.noOfRows and 0 <= neighbour_col < self.noOfCols:
                    neighbouring_particles.extend(self.grid[self.coord_to_index(neighbour_col, neighbour_row)])

        # neighbouring_particles.remove(particle)
        # print(neighbouring_particles)
        return neighbouring_particles

        # feels inefficient, ought to compare with linear search.

    def calculate_rest_density(self, particle_list):
        total_density = 0
        for particle in particle_list:
            total_density += particle.density
            print(total_density, "\n\n==")
        self.set_rest_density(total_density / noOfParticles)  # rest density

    def set_rest_density(self, rest_density):
        self.rest_density = rest_density

    def remove_particle(self, particle):
        cell = self.hash_position(particle.position)
        self.grid[cell].discard(particle)
        # np.delete(self.grid[int(cell[0]), int(cell[1])], particle)

    def insert_particle(self, particle):
        new_cell = self.hash_position(particle.next_position)
        self.grid[new_cell].add(particle)

        # np.append(self.grid[new_cell[0], new_cell[1]], particle)

    def get_normalised_grid(self):
        return list(map(self.normalise_vector, self.vectorField))

    def get_magnitude(self, vector):
        return np.hypot(vector[0], vector[1])

    def normalise_vector(self, vector):
        return vector / self.get_magnitude(vector)


if __name__ == "__main__":
    field = SpatialMap(rows, columns)

