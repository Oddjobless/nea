import pygame
from Simulations.SimulationFiles.baseClasses import *


def run(rows, columns, max_velocity):
    pygame.init()
    screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = VelocityField(rows, columns, max_velocity)
    frame_rate = vector_field.frame_rate
    box_width, box_height = vector_field.box_width, vector_field.box_height
    radius = vector_field.particle_to_add_radius

    vector_field.particles = [Pathfinder(radius // 3, radius, vector_field) for _ in range(30)]
    # container.calculate_rest_density(particles) # integrate into __init
    font = pygame.font.SysFont("comicsans", int(box_width // 2.6))

    clock = pygame.time.Clock()

    """
    LEFT CLICK: set new goal 
    RIGHT CLICK: toggle blocked cells
    Q: quit
    
    """

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    return
                elif event.key == pygame.K_a:  # switch between adding particles and changing goal
                    vector_field.is_adding_particles = not vector_field.is_adding_particles
                elif event.key == pygame.K_c:  # Toggle collisions. Disable to reduce latency
                    vector_field.enable_collision_between_particles = not vector_field.enable_collision_between_particles
                elif event.key == pygame.K_EQUALS:  # Plus symbol --> increase radius
                    vector_field.particle_to_add_radius += 1
                elif event.key == pygame.K_MINUS:  # Minus symbol --> decrease radius
                    vector_field.particle_to_add_radius = max(vector_field.particle_to_add_radius - 1, 3)
                elif event.key == pygame.K_h:
                    vector_field.draw_heatmap = not vector_field.draw_heatmap
                elif event.key == pygame.K_g:
                    vector_field.draw_grid = not vector_field.draw_grid
                elif event.key == pygame.K_r:
                    vector_field.clear_obstacles()


            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    cell = vector_field.index_to_coord(vector_field.hash_position(pygame.mouse.get_pos()))
                    vector_field.toggle_adding_cells(cell)  # Set toggle type accordingly

            click_event = pygame.mouse.get_pressed()
            if any(click_event):
                pos_cell_index = vector_field.index_to_coord(vector_field.hash_position(pygame.mouse.get_pos()))
                if click_event[0]:  # Set new goal
                    vector_field.update_velocity_field(pos_cell_index)

                elif click_event[2]:
                    if not vector_field.is_adding_particles:
                        vector_field.toggle_blocked_cell(pos_cell_index)
                    else:
                        vector_field.add_particle(pygame.mouse.get_pos())

        screen.fill((186, 217, 210))
        if vector_field.draw_heatmap:
            vector_field.display_heatmap(screen)

        if vector_field.enable_collision_between_particles:  # Particle collisions
            for particle in vector_field.particles:
                particle.collision_event_particles()

        vector_field.update()
        for particle in vector_field.particles:
            particle.update(screen)  # Standard particle update

        for particle in vector_field.particles:
            pygame.draw.circle(screen, (130, 46, 129), particle.get_position(), particle.radius)

        for cell in vector_field.obstacles:
            pygame.draw.rect(screen, (0, 0, 0, 0.5), (cell[0] * box_width, cell[1] * box_height, box_width, box_height))

        if vector_field.draw_grid:  # Draw distances, gridlines, and direction vector
            for x in vector_field.get_grid_coords(x=True):
                pygame.draw.line(screen, "#353252", (x, 0), (x, screen_height), 1)

            for y in vector_field.get_grid_coords(y=True):
                pygame.draw.line(screen, "#353252", (0, y), (screen_width, y), 1)

            for coord, cell, distance in zip(vector_field.get_grid_coords(), vector_field.grid,
                                             vector_field.cell_distances):

                box_centre = np.array([coord[0] + box_width / 2, coord[1] + box_height / 2])
                line_radius = (box_width / 2.2) * cell.velocity
                if not any(np.isnan(cell.velocity)):
                    pygame.draw.line(screen, "#ff3542", box_centre, box_centre + line_radius)
                if draw_distances and distance > 0:
                    number = font.render(f"{distance:.1f}", True, (255, 255, 255))
                    screen.blit(number, box_centre - (box_width // 4))

        pygame.display.update()

        clock.tick(frame_rate)


if __name__ == "__main__":
    print("Hi")


#
class Pathfinder(Particle):
    def __init__(self, mass, radius, container, position=None):
        super().__init__(mass, radius, container, position)
        self.damping = 0.7

    def check_for_collision_X(self, obstacle_x, obstacle_width):  # Alternative collision detection = efficient
        radius = self.radius
        if self.next_position[0] + self.radius > obstacle_x + obstacle_width or self.next_position[0] - radius < obstacle_x:
            return False
        return True

    def collision_event_obstacles(self, obstacle_pos, obstacle_width):  # Obstacle collision handler
        # overriding the parent method with this new idea instead
        # runs much faster than the full collision resolution of the Particle Class
        # I used the spatial map to check if the particle is currently in an obstacle
        # Below I am checking if it has hit an obstacle from the sides, or from the top or bottom
        x_collision = self.check_for_collision_X(obstacle_pos[0], obstacle_width)
        if x_collision:  # if collision in x direction
            self.velocity[0] *= -1
        else:  # If not x collision, then is y collision
            self.velocity[1] *= -1
        self.next_position = self.position + self.velocity * -1 * self.container.dt

    def collision_event_particles(self, track_collisions=False):  # Particle collision handler
        try:
            cell_index = self.container.hash_position(self.position)
            particles_to_check = self.container.grid[cell_index].cell_list
            for particle in particles_to_check:
                if self.is_collision(particle, save_collisions=track_collisions):
                    self.resolve_static_collision(particle)
                    return

        except Exception as e:
            print("Debug: Particle collision", e)  # Debugging


class VelocityField(SpatialMap):
    def __init__(self, noOfRows, noOfCols, max_velocity):
        screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        super().__init__(noOfRows, noOfCols, screen_size=screen_size)
        self.cell_distances = np.zeros_like(self.grid)  # Used in pathfinding algorithm
        self.damping = 0.80  # Energy factor in particle collision with walls

        self.obstacles = set()  # Stores obstacles
        self.goal = np.array([0, 0])
        self.particle_max_velocity = max_velocity  # Desired velocity magnitude in steering behaviours

        self.is_adding_particles = False
        self.is_adding_cells = False
        self.enable_collision_between_particles = False
        self.draw_heatmap = True

        self.particle_to_add_radius = 5

        self.max_distance = 0

    def display_heatmap(self, screen):  # drawing a colour gradient depending on cell distance
        for i in range(self.cols):
            for j in range(self.rows):
                distance = self.cell_distances[self.coord_to_index((i, j))]
                if distance > 0:
                    if np.isinf(distance):  # give inf cell a harsh colour
                        pygame.draw.rect(screen, (255, 160, 255),
                                         (i * self.box_width, j * self.box_height, self.box_width, self.box_height))
                    else:
                        norm_distance = distance / self.max_distance  # Normalising distance between 0 and 1
                        colour = np.array([255 * (1 - norm_distance), 190, 255 * norm_distance], dtype=int)
                        pygame.draw.rect(screen, colour,
                                         (i * self.box_width, j * self.box_height, self.box_width, self.box_height))

    def find_max_distance(self):  # Time saving. Only find max_distance when new goal set
        self.max_distance = np.max(list(filter(lambda x: np.isfinite(x), self.cell_distances)))

    def print_visited(self):  # Testing if algorithm is working
        for i in range(self.rows):
            for j in range(self.cols):
                print(self.cell_distances[self.coord_to_index((i, j))], end=" | ")
            print()

    def toggle_adding_cells(self, mouse_cell):  # ... and adding particles
        if mouse_cell in self.obstacles:
            self.is_adding_cells = False
        else:
            self.is_adding_cells = True

    def toggle_blocked_cell(self, coord):  # Seamless obstacle toggling
        if self.is_adding_cells:
            if coord not in self.obstacles:
                self.obstacles.add(coord)
        else:
            if coord in self.obstacles:
                self.obstacles.remove(coord)

    def add_particle(self, mouse_position):
        obj = Pathfinder(self.particle_to_add_radius // 3, self.particle_to_add_radius, self,
                         np.array(mouse_position, dtype=float))

        self.particles.append(obj)

    def generate_heatmap(self, goal_coords):  # Calculate distance field
        self.cell_distances = np.empty_like(self.grid)
        # Initialise cell distances with infinity, obstacles with -1
        for cell_index, cell in enumerate(self.cell_distances):
            cell_coord = self.index_to_coord(cell_index)
            if cell_coord in self.obstacles:
                self.cell_distances[cell_index] = -1
            else:
                self.cell_distances[cell_index] = float('inf')

        # Set distance to the goal cell to 0
        goal_coords = np.clip(np.array(goal_coords), np.zeros_like(goal_coords), np.array([self.cols, self.rows]) - 1)
        goal_index = self.coord_to_index(goal_coords)

        self.cell_distances[goal_index] = 0

        # queue needed for breadth-first search
        queue = [goal_coords]

        while queue:
            current_coord = queue.pop(0)  # Pull from queue
            current_index = self.coord_to_index(current_coord)
            current_distance = self.cell_distances[current_index]
            neighbouring_coords = self.get_neighbouring_coords(current_coord, include_diagonal=True)
            for next_coord in neighbouring_coords:
                try:
                    next_index = self.coord_to_index(next_coord)

                    if next_coord not in self.obstacles and self.cell_distances[next_index] == float('inf'):
                        # update distance if  cell is not blocked and not visited
                        change_x = abs(next_coord[0] - current_coord[0])
                        change_y = abs(next_coord[1] - current_coord[1])
                        if change_x == 1 and change_y == 1:
                            path_cost = 1.41421  # np.sqrt(2) to 5 d.p: diagonal movement
                        else:  # Orthogonal movement
                            path_cost = 1
                        self.cell_distances[next_index] = current_distance + path_cost
                        queue.append(next_coord)
                except IndexError:  # Invalid coordinate --> ignore
                    pass

    #########################################################
    def calculate_vectors(self):  # Calculate velocity field from distance field
        for cell_coord in self.obstacles:
            self.cell_distances[self.coord_to_index(cell_coord)] = -1

        for counter, (values) in enumerate(zip(self.cell_distances, self.grid)):  # Gather necessary values
            distance, cell = values
            if self.index_to_coord(counter) in self.obstacles:
                cell.velocity = np.array([0, 0])
                continue
            coords = self.get_neighbouring_coords(self.index_to_coord(counter), placeholder_for_boundary=True)

            distances = [0, 0, 0, 0]  # right, left, up , down etc. Temp distances for validation purposes
            for index, eachcoord in enumerate(coords):
                if eachcoord and eachcoord not in self.obstacles:
                    distances[index] = self.cell_distances[self.coord_to_index(eachcoord)]
                else:
                    distances[index] = -1

            # Handling velocity of cells adjacent to blocked cells
            dist_copy = distances.copy()
            for index, distance in enumerate(distances):
                if distance == -1:  # Blocked cell
                    if index == 0 and distances[1] != -1:
                        dist_copy[0] = distances[1] + 1  # Change from + 1 to + 2 if repulsive effect desired
                    elif index == 1 and distances[0] != -1:
                        dist_copy[1] = distances[0] + 1
                    if index == 2 and distances[3] != -1:
                        dist_copy[2] = distances[3] + 1
                    elif index == 3 and distances[2] != -1:
                        dist_copy[3] = distances[2] + 1

            # Find velocity components
            x_vector = dist_copy[1] - dist_copy[0]
            y_vector = dist_copy[2] - dist_copy[3]

            # Apply normalised velocity to cell
            cell.velocity = self.normalise_vector(np.array([x_vector, y_vector]))

    def update_velocity_field(self, coords_of_goal):  # New goal has been set, so rerun algorithm
        if not any(np.isnan(coords_of_goal)):
            if not (self.goal[0] == coords_of_goal[0] and self.goal[1] == coords_of_goal[
                1]) and coords_of_goal not in self.obstacles:
                self.goal = coords_of_goal
                self.generate_heatmap(coords_of_goal)
                self.calculate_vectors()
                self.find_max_distance()  # Time saving for displaying heatmap

    def clear_obstacles(self):
        self.obstacles.clear()

    def calculate_avoidance_force(self, position):  # Steering behaviour, now deprecated
        radius = 1 * self.box_width
        avoidance_strength = 150
        steering_force = np.zeros(2)

        for obstacle in self.obstacles:
            distance = np.linalg.norm(position - obstacle)
            if distance < radius:
                # Adjust steering force to help avoid the obstacle
                steering_force += avoidance_strength * (position - obstacle) / distance
        return steering_force

    def calculate_collision_avoidance(self, particle):  # Steering behaviour, now deprecated
        magnitude = 1000
        ahead = particle.position + self.normalise_vector(particle.velocity) * self.box_width
        box_centre_add = self.box_width / 2
        for coord in self.obstacles:
            distance_vector = ahead - (self.undo_hash_position(coord) + box_centre_add)
            if self.get_magnitude(distance_vector) < self.box_width:
                return self.normalise_vector(distance_vector) * magnitude
        return 0

    def zero_vel_for_obstacles(self, particle):  # Lose energy on wall collision, now deprecated
        pos = particle.position
        current_cell = self.index_to_coord(self.hash_position(pos))
        if current_cell in self.obstacles:
            particle.velocity *= 0
        else:
            return

    def update(self):  # update and apply field
        field_strength = 0.02
        for eachCell in self.grid:

            # Applying cell velocity onto particles
            desired_velocity = eachCell.velocity * self.particle_max_velocity
            if any(np.isnan(desired_velocity)) or any(np.isinf(desired_velocity)):  # Debugging
                continue
            for eachParticle in eachCell.cell_list:  # Get particles within cell via spatial map
                steering_force = desired_velocity - eachParticle.velocity  # Change

                eachParticle.velocity += (steering_force * field_strength)  # Steadily apply desired velocity

                # Obstacle collision handling
                coord = self.index_to_coord(self.hash_position(eachParticle.next_position))
                if coord in self.obstacles:
                    eachParticle.collision_event_obstacles(coord, self.box_width)
