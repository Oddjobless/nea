import pygame
import numpy as np
from random import randint, randrange

class Particle:
    def __init__(self, mass, _radius, vector_field, damping, position=None, velocity=None):
        self.damping = damping
        self.radius = _radius  # visual only
        self.mass = mass
        self.vector_field = vector_field

        # self.velocity = np.array([randint(-100, 100), randint(-100, 100)], dtype=float)
        self.velocity = np.zeros(2, dtype=float) if velocity is None else velocity
        if position is not None:
            self.position = position
        else:
            self.position = np.array([randint(2 * self.radius, screen_width - 2 * self.radius), randint(2 * self.radius, screen_height - 2 * self.radius)], dtype=float)
        self.next_position = self.position.copy()
        # self.acceleration = np.array([0,9.8]) * self.mass # short term
        if self.vector_field:
            self.vector_field.insert_particle(self)



        """self.spatial_map_update_frequency = 4  # 1 / 4 frames update the spatial map
        self.spatial_map_update_counter = 0"""

    def collision_event_obstacles(self):
        for obstacle in self.vector_field.obstacles:
            if self.check_obstacle_collision(obstacle.position, obstacle.width, obstacle.height):

                return self.resolve_obstacle_collision(obstacle)
    def collision_event(self, save_collision=True):
        for particle in self.vector_field.particles:
            if self.is_collision(particle, save_collisions=save_collision):
                self.resolve_static_collision(particle)

    def is_collision(self, next_particle, save_collisions=True):
        distance = self.vector_field.get_square_magnitude(next_particle.next_position - self.next_position)
        if self != next_particle:
            if 0 < distance <= (self.radius + next_particle.radius) ** 2:
                if save_collisions:
                    self.vector_field.colliding_balls_pairs.append((self, next_particle))
                return True
        return False

    def resolve_dynamic_collision(self, next_particle):
        distance = self.vector_field.get_magnitude(next_particle.next_position - self.next_position)
        normal = self.vector_field.normalise_vector(next_particle.next_position - self.next_position)
        tangent = np.array([-normal[1], normal[0]])

        tangential_vel_i = tangent * np.dot(self.velocity, tangent)
        tangential_vel_j = tangent * np.dot(next_particle.velocity, tangent)

        normal_vel_i = normal * ((np.dot(self.velocity, normal) * (self.mass - next_particle.mass) + 2 * next_particle.mass * np.dot(next_particle.velocity, normal)) / (self.mass + next_particle.mass))
        normal_vel_j = normal * ((np.dot(next_particle.velocity, normal) * (next_particle.mass - self.mass) + 2 * self.mass * np.dot(self.velocity, normal)) / (self.mass + next_particle.mass))

        self.velocity = tangential_vel_i + normal_vel_i
        next_particle.velocity = tangential_vel_j + normal_vel_j
    def resolve_static_collision(self, next_particle):
        distance = self.vector_field.get_magnitude(next_particle.next_position - self.next_position)

        overlap = 0.5 * (distance - (self.radius + next_particle.radius))
        self.next_position -= overlap * (self.next_position - next_particle.next_position) / distance

        next_particle.next_position += overlap * (self.next_position - next_particle.next_position) / distance
        if np.isclose(self.velocity, np.zeros_like(self.velocity), atol=1).all():
            self.velocity = np.zeros_like(self.velocity)

    def resolve_obstacle_collision(self, obstacle):
        # Calculate the displacement vector from the rectangle to the circle
        displacement = self.position - np.array([max(obstacle.position[0], min(self.position[0], obstacle.position[0] + obstacle.width)),
                                                      max(obstacle.position[1], min(self.position[1], obstacle.position[1] + obstacle.height))])

        # Calculate the penetration depth for both x and y directions
        penetration_x = max(0, self.radius - abs(displacement[0]))
        penetration_y = max(0, self.radius - abs(displacement[1]))

        # Determine the direction of displacement
        direction_x = 1 if displacement[0] > 0 else -1
        direction_y = 1 if displacement[1] > 0 else -1


        if obstacle.is_platform:
            damping = 0.4
        else:
            damping = self.damping


        if penetration_x < penetration_y:
            # Collided in x-direction
            self.next_position[0] += penetration_x * direction_x
            self.velocity[0] *= -1 * damping
            if obstacle.is_platform:
                self.velocity[1] *= damping
        else:
            # Collided in y-direction
            self.next_position[1] += penetration_y * direction_y
            self.velocity[1] *= -1 * damping
            if obstacle.is_platform:
                self.velocity[0] *= damping

        if np.isclose(self.velocity[1], 0, atol=2):
            self.velocity[1] = 0



    def check_obstacle_collision(self, obstacle_pos, width, height, custom_radius=None):

        closest_x = max(obstacle_pos[0], min(self.next_position[0], obstacle_pos[0] + width))
        closest_y = max(obstacle_pos[1], min(self.next_position[1], obstacle_pos[1] + height))

        distance = np.sqrt((self.next_position[0] - closest_x) ** 2 + (self.next_position[1] - closest_y) ** 2)

        if not custom_radius:
            return distance < self.radius
        print(distance, self.radius)
        return distance < custom_radius##

    def entirely_in_obstacle_check(self, pos, width, height): #
        if self.next_position[0] - self.radius > pos[0] and self.next_position[0] + radius < pos[0] + width and self.next_position[1] - self.radius > pos[1] and self.next_position[1] + self.radius < pos[1] + height:
            return True
        return False



    def update(self, screen, custom_dimensions=None, vector_field=True):
        if custom_dimensions is None:
            dim = np.array([0, 0, screen.get_width(), screen.get_height()])
        else:
            dim = custom_dimensions
        if self.next_position[0] > dim[2] - (self.radius) or self.next_position[0] < dim[0] + self.radius:  # or within blocked cell
            self.velocity[0] *= -1 * self.damping
        if self.next_position[1] > dim[3] - (self.radius) or self.next_position[1] < dim[1] + self.radius:
            self.velocity[1] *= -1 * self.damping


        self.next_position = np.clip(self.next_position, (dim[0:2] + self.radius),
                                         (dim[2:4] - self.radius))

        if vector_field:
            self.vector_field.remove_particle(self)
        self.position = self.next_position
        if vector_field:
            self.vector_field.insert_particle(self)

        # print(self.vector_field.grid)

        # self.velocity = self.velocity + self.acceleration * self.mass
        self.next_position = self.position + (self.velocity * dt / self.mass)



    def reverse_position(self, steps):

        self.vector_field.remove_particle(self)
        self.position = self.position - self.velocity * steps * dt
        self.next_position = self.position
        self.vector_field.insert_particle(self)


    def apply_air_resistance(self):
        vel = self.vector_field.get_magnitude(self.velocity)
        vel_normalised = self.vector_field.normalise_vector(self.velocity)
        drag_force = -self.vector_field.drag_coefficient * np.pi * self.radius ** 2 * vel ** 2
        self.velocity += (drag_force * vel_normalised) / self.mass




    def get_position(self):
        return int(self.position[0]), int(self.position[1])
import time
"""


"""
class Cell:
    def __init__(self):
        self.cellList = set()
        self.velocity = np.array([randint(-1,1), randint(-1,1)], dtype=float)



class SpatialMap:
    def __init__(self, noOfRows, noOfCols):
        self.noOfRows = noOfRows
        self.noOfCols = noOfCols
        self.draw_grid = True
        self.grid = np.array([Cell() for _ in
                     range(noOfRows * noOfCols)])
        self.air_resistance = False
        self.drag_coefficient = 0.000000001

        self.rows, self.cols = noOfRows, noOfCols
        self.box_width, self.box_height = screen_width // self.cols, screen_height // self.rows
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

    def hash_position(self, position):
        try:
            return self.coord_to_index((int(position[0] / self.box_width), int(position[1] / self.box_height)))
        except ValueError:
            print(position)

    def undo_hash_position(self, position):
        return np.array(position) // self.box_width


    def coord_to_index(self, coord):
        return coord[0] + coord[1] * self.noOfCols

    def index_to_coord(self, index):
        try:
            return (index % self.noOfCols, index // self.noOfCols)
        except TypeError:
            raise Exception("index_to_coord")
    def get_square_magnitude(self, vector):
        return (vector[0] ** 2 + vector[1] ** 2)

    def get_neighbouring_coords(self, coord, include_diagonal=False, include_self=False, placeholder_for_boundary=False):
        col, row = coord
        directions = [[1, 0], [-1, 0], [0, -1], [0, 1]] # right, left, up, down
        neighbouring_coords = []
        if include_diagonal:
            directions.extend([[-1, -1], [1, -1], [-1, 1], [1, 1]]) # need to change if using euclidean distance

        if include_self:
            directions.append([0, 0])

        for dir in directions:
            neighbour_col, neighbour_row = col + dir[0], row + dir[1]
            if 0 <= neighbour_row < self.noOfRows and 0 <= neighbour_col < self.noOfCols:
                neighbouring_coords.append((neighbour_col, neighbour_row))
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
            print("ERROR")
            # input((particle.position, particle.next_position, particle.velocity, particle.mass))

            return


        self.grid[new_cell].cellList.add(particle)

        # np.append(self.grid[new_cell[0], new_cell[1]], particle)


    def get_magnitude(self, vector):
        try:
            return np.hypot(vector[0], vector[1])
        except:
            return np.array([0,0])

    def normalise_vector(self, vector):
        if vector[0] == 0 and vector[1] == 0:


            # print("WARNING: DIVIDE BY ZERO!!!\n\n\nWHEN NORMALISING VELOCITY FIELD, THERE WAS A VECTOR WITH ZERO MAGNITUDE")
            return vector
        return vector / self.get_magnitude(vector)

    def drag_particle(self, mouse_pos):
        for index, particle in enumerate(self.particles):
            if not particle.radius < mouse_pos[0] < screen_width - particle.radius and particle.radius < mouse_pos[1] < screen_height - particle.radius:
                continue
            distance = particle.vector_field.get_magnitude(np.array(mouse_pos) - particle.position)
            if distance < particle.radius:
                particle.velocity = particle.velocity * 0
                self.selected_particle = index
                return
    def drop_particle(self):
        self.particles[self.selected_particle].velocity *= 0
        self.selected_particle = None

    def move_selected_particle(self, mouse_position):
        self.particles[self.selected_particle].position = mouse_position

    def project_particle(self, mouse_pos):
        for index, particle in enumerate(self.particles):
            if not particle.radius < mouse_pos[0] < screen_width - particle.radius and particle.radius < mouse_pos[1] < screen_height - particle.radius:
                continue
            distance = particle.vector_field.get_magnitude(particle.position - np.array(mouse_pos))
            if distance < particle.radius:
                particle.velocity = particle.velocity * 0
                self.draw_line_to_mouse = True
                self.selected_particle = index
                return

    def release_projected_particle(self, mouse_pos):
        particle = self.particles[self.selected_particle]
        particle.velocity = (np.array(mouse_pos) - particle.position) * self.projected_particle_velocity_multiplier
        self.draw_line_to_mouse = False
        self.selected_particle = None



screen_width, screen_height = 1920, 1080 # 960, 960
# columns, rows = 32,18
# box_width, box_height = screen_width / columns, screen_height / rows


frame_rate = 75  # frames per second
dt = 1 / frame_rate  # time elapsed between frames
radius = 5  # radius of particles, purely for visualisation
noOfParticles = 30  # number of particles.
wall_damping = 0.7  # what percentage of energy the particles keep on collision with boundary
# draw the grid lines on the screen
using_poly_6 = True  #
using_cubic_spline_kernel = True
# smoothing_radius = box_width # will integrate this into program.#
stiffness_constant = 10
draw_distances = True