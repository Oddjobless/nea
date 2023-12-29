import pygame
import numpy as np
from random import randint
class Particle:
    def __init__(self, mass, radius, vector_field, damping):
        self.damping = damping
        self.radius = radius  # visual only
        self.mass = mass
        self.vector_field = vector_field

        # self.velocity = np.array([randint(-100, 100), randint(-100, 100)], dtype=float)
        self.velocity = np.zeros(2, dtype=float)
        self.position = np.array([randint(2 * self.radius, screen_width - 2 * self.radius),
                                  randint(2 * self.radius, screen_height - 2 * self.radius)], dtype=float)
        self.next_position = self.position.copy()
        # self.acceleration = np.array([0,9.8]) * self.mass # short term
        self.vector_field.insert_particle(self)
        self.smoothing_radius = 2 * self.radius
        """self.kernel = SmoothingKernel(smoothing_radius, cubic_spline=True)"""

        """self.calculate_density()
        print(self.density)"""

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

    def calculate_density(self): # can i use self instead?
        density = 0
        neighbouring_particles = self.vector_field.get_neighbouring_particles(self)

        for neighbour_particle in neighbouring_particles:
            distance = self.vector_field.get_magnitude(neighbour_particle.position - self.position)
            density += self.kernel.calculate_density_contribution(distance) # self.density


        # print(self.density == density)
        self.density = self.kernel.get_normalised_density(density)

        # self.calculate_pressure()


        # (self.density)

        # density += self.mass / (self.get_magnitude(self.velocity) ** 2)
        # self.density = self.mass / (self.get_magnitude(self.velocity) *)

    def get_pressure(self): #
        return self.pressure

    def calculate_pressure(self): # ideal gas law
        self.pressure = stiffness_constant * (self.density - self.vector_field.rest_density)


    def calculate_pressure_force(self): #pressure force
        pass

    def get_density(self):
        return self.density

    def get_position(self):
        return int(self.next_position[0]), int(self.next_position[1])
import time
"""
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
"""
class Cell:
    def __init__(self):
        self.cellList = set()
        self.velocity = np.array([randint(-1,1), randint(-1,1)], dtype=float)
        self.isBlocked = False
        self.distance = -1

class SpatialMap:
    def __init__(self, noOfRows, noOfCols):
        self.noOfRows = noOfRows
        self.noOfCols = noOfCols
        self.grid = np.array([Cell() for _ in
                     range(noOfRows * noOfCols)])
        # I WANT TO MAKE SELF.HASH INTO A 1D ARRAY
        # self.grid = np.empty((noOfRows, noOfCols))
        # self.grid.fill(set()) # would like to test speed difference

        ### creating vector field

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

    def hash_position(self, position): # todo this
        return self.coord_to_index((int(position[0] / box_width), int(position[1] / box_height)))

    def undo_hash_position(self, position):
        return position * box_width


    def coord_to_index(self, coord):
        return coord[0] + coord[1] * self.noOfCols

    def index_to_coord(self, index):
        return (index % self.noOfCols, index // self.noOfCols)

    def update_particle(self, particle):
        self.remove_particle(particle)
        self.insert_particle(particle)

    def get_neighbouring_coords(self, coord, include_diagonal=False, include_self=False, placeholder_for_boundary=False):
        row, col = coord
        directions = [[-1, 0], [1, 0], [0, -1], [0, 1]] # left, right, up, down
        neighbouring_coords = []
        if include_diagonal:
            directions.extend([[-1, -1], [1, -1], [-1, 1], [1, 1]]) # need to change if using euclidean distance

        if include_self:
            directions.append([0, 0])

        for dir in directions:
            neighbour_row, neighbour_col = row + dir[0], col + dir[1]
            if 0 <= neighbour_row < self.noOfRows and 0 <= neighbour_col < self.noOfCols:
                neighbouring_coords.append((neighbour_row, neighbour_col))
            elif placeholder_for_boundary:
                neighbouring_coords.append(None)
        return neighbouring_coords

    def get_neighbouring_cells(self, cell_row, cell_col, diagonal=False, use_self=False):
        neighbouring_cells = []
        for coord in self.get_coordinates(cell_row, cell_col, include_diagonal=diagonal, include_self=use_self):
            neighbouring_cells.append(self.grid[self.coord_to_index(coord)])
        return neighbouring_cells

    def get_neighbouring_particles(self, particle):
        cell_row, cell_col = divmod(self.hash_position(particle.position), self.noOfCols)
        neighbour_cells = self.get_neighbouring_cells(cell_row, cell_col, include_self=True, diagonal=True)

        neighbouring_particles = []
        for cell in neighbour_cells:
            neighbouring_particles.extend(cell.cellList)

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
        self.grid[cell].cellList.discard(particle)
        # np.delete(self.grid[int(cell[0]), int(cell[1])], particle)

    def insert_particle(self, particle):
        # print(particle, particle.position, particle.next_position)
        new_cell = self.hash_position(particle.next_position)

        self.grid[new_cell].cellList.add(particle)

        # np.append(self.grid[new_cell[0], new_cell[1]], particle)


    def get_magnitude(self, vector):
        return np.hypot(vector[0], vector[1])

    def normalise_vector(self, vector):
        if vector[0] == 0 and vector[1] == 0:
            print("WARNING: DIVIDE BY ZERO!!!\n\n\nWHEN NORMALISING VELOCITY FIELD, THERE WAS A VECTOR WITH ZERO MAGNITUDE")
            return vector
        return vector / self.get_magnitude(vector)



screen_width, screen_height = 940, 940
rows, columns = 32,32
box_width, box_height = screen_width / columns, screen_height / rows

clock = pygame.time.Clock()

frame_rate = 30  # frames per second
dt = 1 / frame_rate  # time elapsed between frames
radius = 3  # radius of particles, purely for visualisation
noOfParticles = 2500  # number of particles.
wall_damping = 0.4  # what percentage of energy the particles keep on collision with boundary
drawGrid = True  # draw the grid lines on the screen
using_poly_6 = True  #
using_cubic_spline_kernel = True
smoothing_radius = min(box_height, box_width) # will integrate this into program.
stiffness_constant = 2500
