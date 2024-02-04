import pygame
import numpy as np
from random import randint, randrange
class Particle:
    def __init__(self, mass, _radius, vector_field, damping):
        self.damping = damping
        self.radius = _radius  # visual only
        self.mass = mass
        self.vector_field = vector_field

        # self.velocity = np.array([randint(-100, 100), randint(-100, 100)], dtype=float)
        self.velocity = np.zeros(2, dtype=float)
        self.position = np.array([randint(2 * self.radius, screen_width - 2 * self.radius), randint(2 * self.radius, screen_height - 2 * self.radius)], dtype=float)
        self.next_position = self.position.copy()
        # self.acceleration = np.array([0,9.8]) * self.mass # short term
        if self.vector_field:
            self.vector_field.insert_particle(self)



        """self.spatial_map_update_frequency = 4  # 1 / 4 frames update the spatial map
        self.spatial_map_update_counter = 0"""


    def update(self, screen):
        if self.next_position[0] > screen.get_width() - (self.radius) or self.next_position[
            0] < self.radius:  # or within blocked cell
            self.velocity[0] *= -1 * self.damping
        if self.next_position[1] > screen.get_height() - self.radius or self.next_position[1] < self.radius:

            self.velocity[1] *= -1 * self.damping

        self.next_position = np.clip(self.next_position, (self.radius, self.radius),
                                     (screen.get_width() - self.radius, screen.get_height() - self.radius))


        self.vector_field.remove_particle(self)
        self.position = self.next_position
        self.vector_field.insert_particle(self)

        # print(self.vector_field.grid)

        # self.velocity = self.velocity + self.acceleration * self.mass
        self.next_position = self.position + self.velocity * dt



    def reverse_position(self, steps):

        self.vector_field.remove_particle(self)
        self.position = self.position - self.velocity * steps * dt
        self.next_position = self.position
        self.vector_field.insert_particle(self)







    def get_position(self):
        return int(self.position[0]), int(self.position[1])
import time
"""


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
        try:
            return self.coord_to_index((int(position[0] / box_width), int(position[1] / box_height)))
        except ValueError:
            print(position)
    def undo_hash_position(self, position):
        return np.array(position) // box_width


    def coord_to_index(self, coord):
        return coord[0] + coord[1] * self.noOfCols

    def index_to_coord(self, index):
        return (index % self.noOfCols, index // self.noOfCols)

    def get_square_magnitude(self, vector):
        return (vector[0] ** 2 + vector[1] ** 2)

    def get_neighbouring_coords(self, coord, include_diagonal=False, include_self=False, placeholder_for_boundary=False):
        row, col = coord
        directions = [[1, 0], [-1, 0], [0, -1], [0, 1]] # right, left, up, down
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
        for coord in self.get_neighbouring_coords((cell_row, cell_col), include_diagonal=diagonal, include_self=use_self):
            neighbouring_cells.append(self.grid[self.coord_to_index(coord)])
        return neighbouring_cells

    def get_neighbouring_particles(self, particle):
        cell_row, cell_col = divmod(self.hash_position(particle.position), self.noOfCols)
        neighbour_cells = self.get_neighbouring_cells(cell_row, cell_col, use_self=True, diagonal=True)

        neighbouring_particles = []
        for cell in neighbour_cells:
            neighbouring_particles.extend(cell.cellList)

        return neighbouring_particles

        # feels inefficient, ought to compare with linear search.



    def remove_particle(self, particle):
        cell = self.hash_position(particle.position)
        self.grid[cell].cellList.discard(particle)
        # np.delete(self.grid[int(cell[0]), int(cell[1])], particle)

    def insert_particle(self, particle):
        # print(particle, particle.position, particle.next_position)
        new_cell = self.hash_position(particle.next_position)
        if new_cell == None:
            print("ERROR WHY IS THIS BROKEN")
            print(particle.__dir__())
            input((particle.position, particle.next_position, particle.velocity, particle.mass))

            return


        self.grid[new_cell].cellList.add(particle)

        # np.append(self.grid[new_cell[0], new_cell[1]], particle)


    def get_magnitude(self, vector):
        try:
            return np.hypot(vector[0], vector[1])
        except:
            print("ZERO MAGNITUDE")
            return np.array([0,0])

    def normalise_vector(self, vector):
        if vector[0] == 0 and vector[1] == 0:


            print("WARNING: DIVIDE BY ZERO!!!\n\n\nWHEN NORMALISING VELOCITY FIELD, THERE WAS A VECTOR WITH ZERO MAGNITUDE")
            return vector
        return vector / self.get_magnitude(vector)



screen_width, screen_height = 1920, 1080 # 960, 960
rows, columns = 16,16
box_width, box_height = screen_width / columns, screen_height / rows

clock = pygame.time.Clock()

frame_rate = 75  # frames per second
dt = 1 / frame_rate  # time elapsed between frames
radius = 5  # radius of particles, purely for visualisation
noOfParticles = 200  # number of particles.
wall_damping = 1.0  # what percentage of energy the particles keep on collision with boundary
drawGrid = True  # draw the grid lines on the screen
using_poly_6 = True  #
using_cubic_spline_kernel = True
smoothing_radius = box_width # will integrate this into program.# todo
stiffness_constant = 10
draw_distances = True