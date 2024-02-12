# import numpy as np
# PATHFINDER
import numpy as np

from baseClasses import *
# todo euclidean distance?? max(x_2-x_1,y_2-y_1) + (sqrt(2) - 1) * min(x_2-x_1,y_2-y_1): DONE
#  deal with blocked cells no idea how to. maybe set particle velocity to zero upon hitting blocked cell? or cell has reverse velocity of neighbouring cell?
#   mouse interaction...

#
class Pathfinder(Particle):
    def __init__(self, mass, radius, vector_field, damping):
        super().__init__(mass, radius, vector_field, damping)

    def check_for_collision_X(self, obstacle_x, obstacle_width):
        if self.position[0] + self.radius > obstacle_x + obstacle_width or self.next_position[0] - self.radius < obstacle_x:
            return False
        return True
    def check_for_collision_Y(self, obstacle_y, obstacle_height):
        if self.position[1] + self.radius > obstacle_y + obstacle_height or self.next_position[1] - self.radius < obstacle_y:
            return False
        return True







    def is_moving_horizontally(self):
        if abs(self.velocity[0]) > abs(self.velocity[1]):
            return True
        return False

    def collision_event(self, obstacle_pos, obstacle_width):
        if self.check_for_collision_X(obstacle_pos[0], obstacle_width):
            self.velocity[0] *= -1

        else:
            self.velocity[1] *= -1
        self.next_position = self.position + self.velocity * -1 * dt


    def is_collision(self, next_particle):
        distance = self.vector_field.get_square_magnitude(next_particle.next_position - self.next_position)
        if self != next_particle:
            if 0 < distance <= (self.radius + next_particle.radius)**2:
                # self.vector_field.colliding_balls_pairs.append((self, next_particle))
                return True
        return False

    def resolve_static_collision(self, next_particle):
        distance = self.vector_field.get_magnitude(next_particle.next_position - self.next_position)

        overlap = 0.5 * (distance - (self.radius + next_particle.radius))
        self.next_position -= overlap * (self.next_position - next_particle.next_position) / distance

        next_particle.next_position += overlap * (self.next_position - next_particle.next_position) / distance

    def collision_event_particles(self):
        try:
            cell_index = self.vector_field.hash_position(self.next_position)
            particles_to_check = self.vector_field.grid[cell_index].cellList
            for particle in particles_to_check:
                if self.is_collision(particle):
                    self.resolve_static_collision(particle)

        except:
            print(Exception("Collision unresolved"))

class VelocityField(SpatialMap):
    def __init__(self, noOfRows, noOfCols):
        super().__init__(noOfRows, noOfCols)
        for i in self.grid:
            print(i.velocity)
        self.blocked_cells = set()
        self.goal = np.array([0,0])
        # self.update_velocity_field(self.goal)
        self.particle_max_velocity = 500
        self.print_visited()
        self.blocked_cell_radius = box_width
        # self.particle_damping = 0.996 # dont like this

        self.is_adding_cells = False
        self.enable_collision_between_particles = False

        """for i in range(noOfRows):
            self.blocked_cells.add((i,0))
            self.blocked_cells.add((i,noOfCols-1))
        for i in range(noOfRows):
            self.blocked_cells.add((0,i))
            self.blocked_cells.add((noOfRows-1,i))"""


    def print_visited(self):
        for i in range(rows):
            for j in range(columns):
                print(self.grid[self.coord_to_index((i, j))].distance, end=" | ")
            print()

    def toggle_adding_cells(self, mouse_cell):
        if mouse_cell in self.blocked_cells:
            self.is_adding_cells = False
        else:
            self.is_adding_cells = True

    def toggle_blocked_cell(self, coord):
        if self.is_adding_cells:
            if coord not in self.blocked_cells:
                self.blocked_cells.add(coord)
        else:
            self.blocked_cells.remove(coord)


    def generate_heatmap(self, goal_coords):
        # Initialize distances with a large value, obstacles with -1
        for cell_index, cell in enumerate(self.grid):
            cell_coord = self.index_to_coord(cell_index)
            if cell_coord in self.blocked_cells:
                cell.distance = -1
            else:
                cell.distance = float('inf')

        # Set distance to the goal cell to 0
        goal_index = self.coord_to_index(goal_coords)
        self.grid[goal_index].distance = 0

        # Queue for breadth-first search
        queue = [goal_coords]

        while queue:
            current_coord = queue.pop(0)
            current_index = self.coord_to_index(current_coord)
            current_distance = self.grid[current_index].distance

            neighbouring_coords = self.get_neighbouring_coords(current_coord, include_diagonal=False)
            for next_coord in neighbouring_coords:
                next_index = self.coord_to_index(next_coord)
                if next_coord not in self.blocked_cells and self.grid[next_index].distance == float('inf'):
                    # Only update distance if the cell is not blocked and not yet visited
                    self.grid[next_index].distance = current_distance + 1
                    queue.append(next_coord)

        """for index, bool in enumerate(visited):
            if False:
                print("WARNING")
                self.grid[index].velocity = np.zeros(2)"""




#########################################################
    def calculate_vectors(self):
        for cell_coord in self.blocked_cells:
            self.grid[self.coord_to_index(cell_coord)].distance = -1


        for index, cell in enumerate(self.grid): # added .copy() cos debugging
            if self.index_to_coord(index) in self.blocked_cells:
                cell.velocity = np.array([0,0])
                continue
            coords = self.get_neighbouring_coords(self.index_to_coord(index), placeholder_for_boundary=True)

            distances = [0, 0, 0, 0] # right, left, up , down etc
            for index, eachcoord in enumerate(coords):
                if eachcoord and eachcoord not in self.blocked_cells:
                    distances[index] = self.grid[self.coord_to_index(eachcoord)].distance
                else:

                    distances[index] = -1

            maximum = max(distances)
            dist_copy = distances.copy()
            for index, distance in enumerate(distances):
                if distance == -1:

                    if index == 0 and distances[1] != -1:
                        dist_copy[0] = distances[1] + 2
                    elif index == 1 and distances[0] != -1:
                        dist_copy[1] = distances[0] + 2
                    if index == 2 and distances[3] != -1:
                        dist_copy[2] = distances[3] + 2
                    elif index == 3 and distances[2] != -1:
                        dist_copy[3] = distances[2] + 2




            """if maximum in distances:
                if distances[0] == maximum:
                    distances[0] = distances[1] + 4
                if distances[1] == maximum:
                    distances[1] = distances[0] + 4
                if distances[2] == maximum:
                    distances[2] = distances[3] + 4
                if distances[3] == maximum:
                    distances[3] = distances[2] + 4"""




            x_vector = dist_copy[1] - dist_copy[0]
            y_vector = dist_copy[2] - dist_copy[3]

            cell.velocity = self.normalise_vector(np.array([x_vector, y_vector]))


    def update_velocity_field(self, coords_of_goal):
        if not any(np.isnan(coords_of_goal)):
            if self.goal[0] != coords_of_goal[0] and self.goal[1] != coords_of_goal[1] and coords_of_goal not in self.blocked_cells:

                self.generate_heatmap(coords_of_goal)
                self.calculate_vectors()


    def calculate_steering_force(self, particle):
        pass

    def calculate_avoidance_force(self, position):
        radius = 1 * box_width
        avoidance_strength = 150
        steering_force = np.zeros(2)

        for obstacle in self.blocked_cells:
            distance = np.linalg.norm(position - obstacle)
            if distance < radius:
                # Adjust steering force to avoid the obstacle
                steering_force += avoidance_strength * (position - obstacle) / distance

        return steering_force

    def calculate_collision_avoidance(self, particle):
        force = 0
        magnitude = 1000
        ahead = particle.position + self.normalise_vector(particle.velocity) * self.blocked_cell_radius
        box_centre_add = box_width / 2
        for coord in self.blocked_cells:
            distance_vector = ahead - (self.undo_hash_position(coord) + box_centre_add)

            if self.get_magnitude(distance_vector) < self.blocked_cell_radius:
                return self.normalise_vector(distance_vector) * magnitude
        return 0

    def zero_vel_for_blocked_cells(self, particle):
        pos = particle.position
        current_cell = self.index_to_coord(self.hash_position(pos))
        if current_cell in self.blocked_cells:
            particle.velocity *= 0
        else:
            return






    def update(self):
        field_strength = 0.02
        for eachCell in self.grid:
            # velChange = self.normalise_vector(eachCell.velocity) * self.STRENGTH
            desired_velocity = eachCell.velocity * self.particle_max_velocity
            if any(np.isnan(desired_velocity)):
                continue

            for eachParticle in eachCell.cellList:
                steering_force = desired_velocity - eachParticle.velocity

                eachParticle.velocity += (steering_force * field_strength) # + self.calculate_collision_avoidance(eachParticle)
                # self.zero_vel_for_blocked_cells(eachParticle)
                """for blockedCell in self.blocked_cells:
                    if eachParticle.extra_boundary_check(self.undo_hash_position(blockedCell), box_width):
                        break"""
                coord = self.index_to_coord(self.hash_position(eachParticle.next_position))

                if coord in self.blocked_cells:

                    eachParticle.collision_event(coord, box_width)



