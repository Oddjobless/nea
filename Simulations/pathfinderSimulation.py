import pygame
from Simulations.SimulationFiles.baseClasses import *



def run(rows, columns, max_velocity):
    pygame.init()
    screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = VelocityField(rows, columns, max_velocity)
    box_width, box_height = vector_field.box_width, vector_field.box_height

    vector_field.particles = [Pathfinder(radius//3, radius, vector_field) for _ in range(30)]
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
                elif event.key == pygame.K_a: # switch between adding particles and changing goal
                    vector_field.is_adding_particles = not vector_field.is_adding_particles
                elif event.key == pygame.K_c: # toggle collisions. turn off to reduce latency
                    vector_field.enable_collision_between_particles = not vector_field.enable_collision_between_particles
                elif event.key == pygame.K_EQUALS: # plus symbol
                    vector_field.particle_to_add_radius += 1
                elif event.key == pygame.K_MINUS: # minus symbol
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
                    vector_field.toggle_adding_cells(cell)


            click_event = pygame.mouse.get_pressed()
            if any(click_event):
                pos_cell_index = vector_field.index_to_coord(vector_field.hash_position(pygame.mouse.get_pos()))
                if click_event[0]: # LEFT CLICK
                    vector_field.update_velocity_field(pos_cell_index)

                elif click_event[2]: # RIGHT CLICK
                    if not vector_field.is_adding_particles:
                        vector_field.toggle_blocked_cell(pos_cell_index)
                    else:
                        vector_field.add_particle(pygame.mouse.get_pos())
        ### drawing vectorField
        screen.fill((186, 217, 210))


        if vector_field.draw_heatmap:
            vector_field.display_heatmap(screen)

        if vector_field.enable_collision_between_particles:
            for particle in vector_field.particles:
                particle.collision_event_particles()

        """for i in container.grid:
            print(i.cell_list, end="")"""
        vector_field.update()
        for particle in vector_field.particles:
            particle.update(screen)  # updates position of particles

        # total_density = 0
        for particle in vector_field.particles:
            pygame.draw.circle(screen, (130, 46, 129), particle.get_position(), particle.radius)


        for cell in vector_field.obstacles:
            pygame.draw.rect(screen, (0, 0, 0, 0.5), (cell[0] * box_width, cell[1] * box_height, box_width, box_height))

        if vector_field.draw_grid:
            for x in vector_field.get_grid_coords(x=True):
                pygame.draw.line(screen, "#353252", (x, 0), (x, screen_height), 1)

            for y in vector_field.get_grid_coords(y=True):
                pygame.draw.line(screen, "#353252", (0, y), (screen_width, y), 1)


            for coord, cell, distance in zip(vector_field.get_grid_coords(), vector_field.grid, vector_field.cell_distances):

                boxCentre = np.array([coord[0] + box_width/2, coord[1] + box_height/2])
                lineRadius = (box_width/2.2) * cell.velocity
                if not any(np.isnan(cell.velocity)):
                    pygame.draw.line(screen, "#ff3542", (boxCentre), boxCentre+lineRadius)
                if draw_distances and distance > 0:
                    number = font.render(f"{distance:.1f}", True, (255, 255, 255))
                    screen.blit(number, boxCentre - (box_width//4))













        # print("Total density: ", total_density)

        # Update display

        pygame.display.update()


        clock.tick(frame_rate)



if __name__ == "__main__":
    run()





#
class Pathfinder(Particle):
    def __init__(self, mass, radius, container, position=None):
        super().__init__(mass, radius, container, position)

    def check_for_collision_X(self, obstacle_x, obstacle_width):
        if self.position[0] + self.radius > obstacle_x + obstacle_width or self.next_position[0] - self.radius < obstacle_x:
            return False
        return True
    def check_for_collision_Y(self, obstacle_y, obstacle_height):
        if self.position[1] + self.radius > obstacle_y + obstacle_height or self.next_position[1] - self.radius < obstacle_y:
            return False
        return True

    # def is_moving_horizontally(self):
    #     if abs(self.velocity[0]) > abs(self.velocity[1]):
    #         return True
    #     return False

    def collision_event_obstacles(self, obstacle_pos, obstacle_width):
        # overriding the parent method with this new idea instead
        # runs much faster than the full collision resolution of the Particle Class
        # I used the spatial map to check if the particle is currently in an obstacle
        # Below I am checking if it has hit an obstacle from the sides, or from the top or bottom
        x_collision = self.check_for_collision_X(obstacle_pos[0], obstacle_width)
        if x_collision: # if collision in x direction
            self.velocity[0] *= -1
        else:
            self.velocity[1] *= -1
        self.next_position = self.position + self.velocity * -1 * dt


    def collision_event_particles(self, track_collisions=False):
        try:
            cell_index = self.container.hash_position(self.position)
            particles_to_check = self.container.grid[cell_index].cell_list
            for particle in particles_to_check:
                if self.is_collision(particle, save_collisions=track_collisions):
                    self.resolve_static_collision(particle)
                    return

        except Exception as e:
            raise Exception

class VelocityField(SpatialMap):
    def __init__(self, noOfRows, noOfCols, max_velocity):
        screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        super().__init__(noOfRows, noOfCols, screen_size=screen_size)
        self.cell_distances = np.zeros_like(self.grid)
        self.wall_damping = 0.8

        self.obstacles = set()
        self.goal = np.array([0,0])
        # self.update_velocity_field(self.goal)
        self.particle_max_velocity = max_velocity
        # self.particle_damping = 0.996 # dont like this

        self.is_adding_particles = False
        self.is_adding_cells = False
        self.enable_collision_between_particles = False
        self.draw_heatmap = True

        self.particle_to_add_radius = radius

        self.max_distance = 0

        # self.print_visited()

        """for i in range(noOfRows):
            self.obstacles.add((i,0))
            self.obstacles.add((i,noOfCols-1))
        for i in range(noOfRows):
            self.obstacles.add((0,i))
            self.obstacles.add((noOfRows-1,i))"""


    def display_heatmap(self, screen): # drawing a colour gradient depending on the distance
        for i in range(self.cols):
            for j in range(self.rows):
                distance = self.cell_distances[self.coord_to_index((i, j))]
                if distance > 0:
                    if np.isinf(distance): # give inf cell a specific colour
                        pygame.draw.rect(screen, (255,160,255), (i * self.box_width, j * self.box_height, self.box_width, self.box_height))
                    else:
                        norm_distance = distance / self.max_distance
                        colour = np.array([255 * (1 - norm_distance), 190, 255 * (norm_distance)], dtype=int)
                        pygame.draw.rect(screen, colour,
                                         (i * self.box_width, j * self.box_height, self.box_width, self.box_height))

    def find_max_distance(self):
        self.max_distance = np.max(list(filter(lambda x: np.isfinite(x), self.cell_distances)))


    def print_visited(self):
        for i in range(self.rows):
            for j in range(self.cols):
                print(self.cell_distances[self.coord_to_index((i, j))], end=" | ")
            print()

    def toggle_adding_cells(self, mouse_cell):
        if mouse_cell in self.obstacles:
            self.is_adding_cells = False
        else:
            self.is_adding_cells = True

    def toggle_blocked_cell(self, coord):
        if self.is_adding_cells:
            if coord not in self.obstacles:
                self.obstacles.add(coord)
        else:
            if coord in self.obstacles:
                self.obstacles.remove(coord)

    def add_particle(self, mouse_position):
        obj = Pathfinder(self.particle_to_add_radius//3, self.particle_to_add_radius, self, np.array(mouse_position, dtype=float))

        self.particles.append(obj)


    def generate_heatmap(self, goal_coords):

        self.cell_distances = np.empty_like(self.grid)
        # initialise cell distances with infinity, obstacles with -1
        for cell_index, cell in enumerate(self.cell_distances):
            cell_coord = self.index_to_coord(cell_index)
            if cell_coord in self.obstacles:
                self.cell_distances[cell_index] = -1
            else:
                self.cell_distances[cell_index] = float('inf')


        # set distance to the goal cell to 0
        goal_coords = np.clip(np.array(goal_coords), np.zeros_like(goal_coords), np.array([self.cols, self.rows]) - 1)
        goal_index = self.coord_to_index(goal_coords)

        self.cell_distances[goal_index] = 0

        # queue needed for breadth-first search
        queue = [goal_coords]

        while queue:
            current_coord = queue.pop(0)
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
                            path_cost = 1.41421 # np.sqrt(2) to 5 d.p: diagonal movement
                        else:  # Orthogonal movement
                            path_cost = 1
                        self.cell_distances[next_index] = current_distance + path_cost
                        queue.append(next_coord)
                except IndexError:
                    pass
        """for index, bool in enumerate(visited):
            if False:
                print("WARNING")
                self.grid[index].velocity = np.zeros(2)"""




#########################################################
    def calculate_vectors(self):
        for cell_coord in self.obstacles: # todo
            self.cell_distances[self.coord_to_index(cell_coord)] = -1



        for index, (values) in enumerate(zip(self.cell_distances, self.grid)): # added .copy() cos debugging
            distance, cell = values
            if self.index_to_coord(index) in self.obstacles:
                cell.velocity = np.array([0,0])
                continue
            coords = self.get_neighbouring_coords(self.index_to_coord(index), placeholder_for_boundary=True)

            distances = [0, 0, 0, 0] # right, left, up , down etc
            for index, eachcoord in enumerate(coords):
                if eachcoord and eachcoord not in self.obstacles:
                    distances[index] = self.cell_distances[self.coord_to_index(eachcoord)]
                else:

                    distances[index] = -1


            dist_copy = distances.copy()
            for index, distance in enumerate(distances):
                if distance == -1:
                    if index == 0 and distances[1] != -1: # todo: changed from + 2 to + 1
                        dist_copy[0] = distances[1] + 1
                    elif index == 1 and distances[0] != -1:
                        dist_copy[1] = distances[0] + 1
                    if index == 2 and distances[3] != -1:
                        dist_copy[2] = distances[3] + 1
                    elif index == 3 and distances[2] != -1:
                        dist_copy[3] = distances[2] + 1






            x_vector = dist_copy[1] - dist_copy[0]
            y_vector = dist_copy[2] - dist_copy[3]

            cell.velocity = self.normalise_vector(np.array([x_vector, y_vector]))


    def update_velocity_field(self, coords_of_goal):
        if not any(np.isnan(coords_of_goal)):
            if not (self.goal[0] == coords_of_goal[0] and self.goal[1] == coords_of_goal[1]) and coords_of_goal not in self.obstacles:
                self.goal = coords_of_goal
                self.generate_heatmap(coords_of_goal)
                self.calculate_vectors()
                self.find_max_distance()

    def clear_obstacles(self):
        self.obstacles.clear()

    def calculate_steering_force(self, particle):
        pass

    def calculate_avoidance_force(self, position):
        radius = 1 * self.box_width
        avoidance_strength = 150
        steering_force = np.zeros(2)

        for obstacle in self.obstacles:
            distance = np.linalg.norm(position - obstacle)
            if distance < radius:
                # Adjust steering force to avoid the obstacle
                steering_force += avoidance_strength * (position - obstacle) / distance

        return steering_force

    def calculate_collision_avoidance(self, particle):
        force = 0
        magnitude = 1000
        ahead = particle.position + self.normalise_vector(particle.velocity) * self.box_width
        box_centre_add = self.box_width / 2
        for coord in self.obstacles:
            distance_vector = ahead - (self.undo_hash_position(coord) + box_centre_add)

            if self.get_magnitude(distance_vector) < self.box_width:
                return self.normalise_vector(distance_vector) * magnitude
        return 0

    def zero_vel_for_obstacles(self, particle):
        pos = particle.position
        current_cell = self.index_to_coord(self.hash_position(pos))
        if current_cell in self.obstacles:
            particle.velocity *= 0
        else:
            return






    def update(self):
        field_strength = 0.02
        for eachCell in self.grid:
            # velChange = self.normalise_vector(eachCell.velocity) * self.STRENGTH
            desired_velocity = eachCell.velocity * self.particle_max_velocity
            if any(np.isnan(desired_velocity)) or any(np.isinf(desired_velocity)):
                continue

            for eachParticle in eachCell.cell_list:
                steering_force = desired_velocity - eachParticle.velocity

                eachParticle.velocity += (steering_force * field_strength) # + self.calculate_collision_avoidance(eachParticle)
                # self.zero_vel_for_obstacles(eachParticle)
                """for blockedCell in self.obstacles:
                    if eachParticle.extra_boundary_check(self.undo_hash_position(blockedCell), box_width):
                        break"""

                coord = self.index_to_coord(self.hash_position(eachParticle.next_position))

                if coord in self.obstacles:

                    eachParticle.collision_event_obstacles(coord, self.box_width)





