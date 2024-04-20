# These classes form the foundations for all simulations
import numpy as np
from random import randint


class Particle:
    def __init__(self, mass, _radius, container, position=None, velocity=None):
        self.damping = 0.8  # energy loss factor after a collision
        self.radius = _radius  # size of the particle
        self.mass = mass  # particle mass
        self.container = container  # the container which the particle is bound to

        self.velocity = np.zeros(2, dtype=float) if velocity is None else velocity
        if position is not None:
            self.position = position
        else:
            width, height = self.container.screen_width, self.container.screen_height
            self.position = np.array(
                [randint(self.radius, width - self.radius), randint(self.radius, height - self.radius)], dtype=float)
        self.next_position = self.position.copy()  # typically used for collision detection
        if self.container:
            self.container.insert_particle(self)  # into the spatial map

    def collision_event_obstacles(self):  # Used for collision detection with Obstacle Object
        for obstacle in self.container.obstacles:
            if self.check_obstacle_collision(obstacle.position, obstacle.width, obstacle.height):  # if collision
                self.resolve_obstacle_collision(obstacle)  # Put particle into a valid position
                return True
        return False

    def resolve_obstacle_collision(self, obstacle, is_object=True):  # resolve particle position relative to obstacle
        if is_object:  # If obstacle is an object of class Obstacle
            position = obstacle.position
            width, height = obstacle.width, obstacle.height
            is_platform = obstacle.is_platform
        else:  # If obstacle is a list of values instead, parse it
            is_platform = False
            position = obstacle[0]
            width, height = obstacle[1], obstacle[2]

        # calculating displacement vector from the rectangle to the circle
        # unlike particle collisions, the vector must be either vertical or horizontal
        displacement = self.position - np.array([max(position[0], min(self.position[0], position[0] + width)),
                                                 max(position[1], min(self.position[1], position[1] + height))])

        # needed to determine how ball got into the rectangle
        penetration_x = max(0, self.radius - abs(displacement[0]))
        penetration_y = max(0, self.radius - abs(displacement[1]))

        # direction of displacement
        direction_x = 1 if displacement[0] > 0 else -1
        direction_y = 1 if displacement[1] > 0 else -1

        # if platform, have greater damping
        if is_platform:
            damping = 0.4
        else:
            damping = self.container.damping

        # determines if ball moves horizontally or vertically
        if penetration_x < penetration_y:
            # resolving position
            self.next_position[0] += penetration_x * direction_x
            # reversing velocity
            self.velocity[0] *= -1 * damping
            if is_platform:
                self.velocity[1] *= damping
        else:
            self.next_position[1] += penetration_y * direction_y
            self.velocity[1] *= -1 * damping
            if is_platform:
                self.velocity[0] *= damping

        if np.isclose(self.velocity[1], 0, atol=2):
            self.velocity[1] = 0

    def check_obstacle_collision(self, obstacle_pos, width, height, custom_radius=None):

        closest_x = max(obstacle_pos[0], min(self.next_position[0], obstacle_pos[0] + width))
        closest_y = max(obstacle_pos[1], min(self.next_position[1], obstacle_pos[1] + height))

        square_distance = (self.next_position[0] - closest_x) ** 2 + (self.next_position[1] - closest_y) ** 2

        if not custom_radius:
            return square_distance < self.radius ** 2
        return square_distance < custom_radius ** 2

    def collision_event(self, save_collision=True):  # handles particle collisions
        for particle in self.container.particles:
            if self.is_collision(particle, save_collisions=save_collision):
                self.resolve_static_collision(particle)

    def is_collision(self, next_particle, save_collisions=True):  # checks for a particle collision
        distance = self.container.get_square_magnitude(next_particle.next_position - self.next_position)
        if self != next_particle:  # A particle should collide with itself
            # if distance between particles is less than the two radii, then there has been a collision. Note that if
            # a > b, then a^2 > b^2. Sqrt is an expensive function, so we improve efficiency by using square distances
            if 0 < distance <= (self.radius + next_particle.radius) ** 2:
                if save_collisions:
                    self.container.colliding_balls_pairs.append((self, next_particle))
                return True  # collision detected
        return False  # no collision detected

    def resolve_static_collision(self, next_particle):  # Resolve particle position in collision event
        # Finding magnitude of vector
        distance = self.container.get_magnitude(next_particle.next_position - self.next_position)
        overlap = 0.5 * (distance - (self.radius + next_particle.radius))

        # Finding direction vector and applying final vector
        self.next_position -= overlap * (self.next_position - next_particle.next_position) / distance
        next_particle.next_position += overlap * (self.next_position - next_particle.next_position) / distance

        # Sorting inaccuracies with dividing
        if np.isclose(self.velocity, np.zeros_like(self.velocity), atol=1).all():
            self.velocity = np.zeros_like(self.velocity)

    def resolve_dynamic_collision(self, next_particle):
        normal = self.container.normalise_vector(next_particle.next_position - self.next_position)
        tangent = np.array([-normal[1], normal[0]])

        # oblique collisions in vector form
        tangential_vel_i = tangent * np.dot(self.velocity, tangent)
        tangential_vel_j = tangent * np.dot(next_particle.velocity, tangent)

        # using formula
        normal_vel_i = normal * ((np.dot(self.velocity, normal) * (
                self.mass - next_particle.mass) + 2 * next_particle.mass * np.dot(next_particle.velocity,
                                                                                  normal)) / (
                                         self.mass + next_particle.mass))
        normal_vel_j = normal * ((np.dot(next_particle.velocity, normal) * (
                next_particle.mass - self.mass) + 2 * self.mass * np.dot(self.velocity, normal)) / (
                                         self.mass + next_particle.mass))

        self.velocity = tangential_vel_i + normal_vel_i  # Combining the two parallel and perpendicular components
        next_particle.velocity = tangential_vel_j + normal_vel_j

    def update(self, screen, custom_dimensions=None, vector_field=True):  # ran every time step
        if custom_dimensions is None:  # by default, the particles are bound the display size
            dim = np.array([0, 0, screen.get_width(), screen.get_height()])
        else:
            dim = custom_dimensions

        # Checking position with the display dimensions
        # If the particle's x position is above the screen height, then reverse vertical velocity
        # And vice versa with y position
        if self.next_position[0] > dim[2] - self.radius or self.next_position[0] < dim[0] + self.radius:
            self.velocity[0] *= -1 * self.damping
        if self.next_position[1] > dim[3] - self.radius or self.next_position[1] < dim[1] + self.radius:
            self.velocity[1] *= -1 * self.damping

        # Put the particle back in bounds
        self.next_position = np.clip(self.next_position, (dim[0:2] + self.radius),
                                     (dim[2:4] - self.radius))

        if vector_field:  # update the spatial map as needed
            self.container.remove_particle(self)
        self.position = self.next_position
        if vector_field:
            self.container.insert_particle(self)
        self.next_position = self.position + (self.velocity * self.container.dt / self.mass)

    def apply_air_resistance(self):
        vel = self.container.get_magnitude(self.velocity)
        vel_normalised = self.container.normalise_vector(self.velocity)  # just want the direction vector
        # applying formula to find resistive force
        drag_force = -self.container.drag_coefficient * np.pi * self.radius ** 2 * vel ** 2
        self.velocity += (drag_force * vel_normalised) / self.mass

    def get_position(self):
        return int(self.position[0]), int(self.position[1])


class Cell:  # The cells in the spatial map
    def __init__(self):
        self.cell_list = set()  # list of particles currently within this cell
        self.velocity = np.array([randint(-1, 1), randint(-1, 1)], dtype=float)  # cell velocity


class SpatialMap:
    def __init__(self, noOfRows, noOfCols, screen_size=(1920, 1080)):
        self.frame_rate = 48
        self.dt = 1 / self.frame_rate
        self.draw_line_to_mouse = None  # Used with firing particles
        self.projected_particle_velocity_multiplier = None  # Used with firing particles
        self.screen_width, self.screen_height = screen_size[0], screen_size[1]
        self.selected_particle = None
        self.draw_grid = True
        self.grid = np.array([Cell() for _ in range(noOfRows * noOfCols)])  # Spatial map; used in pathfinder and fluid flow
        self.air_resistance = False  # dictates if air resistance should be considered
        self.drag_coefficient = 0.000000001  # arbitrary constant that gave good results for air resistance
        self.rows, self.cols = noOfRows, noOfCols
        self.box_width, self.box_height = self.screen_width / self.cols, self.screen_height / self.rows  # cell width and height
        self.damping = 0.8  # The factor of energy the particles lose after a collision
        self.particles = []  # Alternative to spatial map

    def get_grid_coords(self, x=False, y=False):  # get coordinates for spatial map
        x_coords = np.linspace(0, self.screen_width, self.cols, endpoint=False)
        if x:
            return x_coords

        y_coords = np.linspace(0, self.screen_height, self.rows, endpoint=False)
        if y:
            return y_coords

        x_values, y_values = np.array(np.meshgrid(x_coords, y_coords))
        coords = np.column_stack((x_values.ravel(), y_values.ravel()))
        return coords

    def hash_position(self, position):  # Find the cell the particle is on
        try:
            return self.coord_to_index((int(position[0] / self.box_width), int(position[1] / self.box_height)))
        except ValueError:
            print(f"Error hashing position for position {position}")

    def undo_hash_position(self, position):  # get the cartesian coordinates of the cell corner
        return np.array(position) // self.box_width

    def coord_to_index(self, coord):  # Convert a coordinate into an index suitable for 1d arrays
        return coord[0] + coord[1] * self.cols

    def index_to_coord(self, index):  # Inverse operation of coord_to_index
        try:
            return index % self.cols, index // self.cols
        except TypeError:
            raise Exception("index_to_coord")  # logging

    @staticmethod
    def get_magnitude(vector):
        try:
            return np.sqrt(vector[0] ** 2 + vector[1] ** 2)
        except:  # In case of ANY errors (zero magnitude, incorrect datatype, etc.), return zero vector
            return np.zeros_like(vector)

    @staticmethod
    def get_square_magnitude(vector):  #
        try:
            return vector[0] ** 2 + vector[1] ** 2
        except:  # usually vector's magnitude is 0 or type is wrong etc.
            return vector

    def normalise_vector(self, vector):
        if vector[0] == 0 and vector[1] == 0:  # If vector has zero magnitude
            return vector  # Return the zero vector
        return vector / self.get_magnitude(vector)


    def get_neighbouring_coords(self, coord, include_diagonal=False, include_self=False,
                                placeholder_for_boundary=False):
        # given a coord, find the neighbouring coords
        col, row = coord
        directions = [[1, 0], [-1, 0], [0, -1], [0, 1]]  # Right, left, up, down | Orthogonal movement
        neighbouring_coords = []
        if include_diagonal:
            directions.extend([[-1, -1], [1, -1], [-1, 1], [1, 1]])

        if include_self:
            directions.append([0, 0])

        for offset in directions:
            neighbour_col, neighbour_row = col + offset[0], row + offset[1]
            if 0 <= neighbour_row < self.rows and 0 <= neighbour_col < self.cols:
                neighbouring_coords.append((neighbour_col, neighbour_row))
            elif placeholder_for_boundary:
                neighbouring_coords.append(None)  # simulation will deal with this separately
        return neighbouring_coords

    def get_neighbouring_cells(self, cell_row, cell_col, diagonal=False, use_self=False):
        neighbouring_cells = []

        for coord in self.get_neighbouring_coords((cell_row, cell_col), include_diagonal=diagonal,
                                                  include_self=use_self):
            # Getting the cell objects at the requested coordinates
            neighbouring_cells.append(self.grid[self.coord_to_index(coord)])
        return neighbouring_cells

    def get_neighbouring_particles(self, particle):
        cell_row, cell_col = divmod(self.hash_position(particle.position), self.cols)
        neighbour_cells = self.get_neighbouring_cells(cell_row, cell_col, use_self=True, diagonal=True)
        neighbouring_particles = []
        for cell in neighbour_cells:
            # Getting the particles which are currently with the cell according to the spatial map
            neighbouring_particles.extend(cell.cell_list)
        return neighbouring_particles

    def remove_particle(self, particle):  # Remove a particle from the spatial map
        cell = self.hash_position(particle.position)  # find the cell it is in
        self.grid[cell].cell_list.discard(particle)  # remove it from the spatial map

    def insert_particle(self, particle):
        new_cell = self.hash_position(particle.next_position)  # Find the cell the particle is in
        if new_cell is None:
            print("Error in insert_particle method of Particle")
            return
        elif not 0 <= new_cell < self.rows * self.cols:  # particle is outside screen
            # resolving particle position
            r = particle.radius
            particle.next_position = np.clip(particle.next_position, (r, r),
                                             (self.screen_width - r, self.screen_height - r))
            return self.insert_particle(particle)  # return new instance with the updated position

        # add the particle to the cell's particle list
        self.grid[new_cell].cell_list.add(particle)


    def drag_particle(self, mouse_pos):  # moving a particle with the cursor
        for index, particle in enumerate(self.particles):
            rad = particle.radius
            if not rad < mouse_pos[0] < self.screen_width - rad and rad < mouse_pos[1] < self.screen_height - rad:
                continue
            distance = particle.container.get_magnitude(np.array(mouse_pos) - particle.position)
            if distance < rad:  # if cursor is within particle
                particle.velocity = particle.velocity * 0  # stop particle movement when particle first clicked on
                self.selected_particle = index
                return  # as it has found the particle in question, no need to continue searching

    def drop_particle(self):  # When user has released the cursor, release the particle
        self.particles[self.selected_particle].velocity *= 0
        self.selected_particle = None

    def move_selected_particle(self, mouse_position):  # Put particle onto cursor
        self.particles[self.selected_particle].position = mouse_position

    def project_particle(self, mouse_pos):  # now only used for firing projectiles in projectile motion
        # Finding which particle the user is interacting with
        for index, particle in enumerate(self.particles):
            rad = particle.radius
            if not rad < mouse_pos[0] < self.screen_width - rad and rad < mouse_pos[1] < self.screen_height - rad:
                continue
                # if the cursor is not within the radius of the particle, skip
            distance = particle.container.get_magnitude(particle.position - np.array(mouse_pos))
            if distance < rad:  # if the cursor is within the radius of the particle
                particle.velocity = particle.velocity * 0  # stop particle movement
                self.draw_line_to_mouse = True
                self.selected_particle = index  # Used to track a given particle
                return

    def release_projected_particle(self, mouse_pos):
        particle = self.particles[self.selected_particle]
        # update particle velocity with the new direction vector
        particle.velocity = (np.array(mouse_pos) - particle.position) * self.projected_particle_velocity_multiplier
        self.draw_line_to_mouse = False
        self.selected_particle = None  # Stop tracking particle