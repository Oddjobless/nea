# import numpy as np
# PATHFINDER
import numpy as np

from baseClasses import *
# todo euclidean distance?? max(x_2-x_1,y_2-y_1) + (sqrt(2) - 1) * min(x_2-x_1,y_2-y_1): DONE
# TODO deal with blocked cells no idea how to. maybe set particle velocity to zero upon hitting blocked cell? or cell has reverse velocity of neighbouring cell?
# TODO  mouse interaction...

#
class Pathfinder(Particle):
    def __init__(self, mass, radius, vector_field, damping):
        super().__init__(mass, radius, vector_field, damping)


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


        # todo: increase force of blcok on particle. do not normalise


    def print_visited(self):
        for i in range(rows):
            for j in range(columns):
                print(self.grid[self.coord_to_index((i, j))].distance, end=" | ")
            print()

    def toggle_blocked_cell(self, coord):
        if coord not in self.blocked_cells:
            self.blocked_cells.add(coord)
            print("asdfsad")
        else:
            print("Hi")
            pass
            # self.blocked_cells.remove(coord) # todo






    def generate_heatmap(self, goal_coords):  # todo: boundary problems idk why. ALSO WANT TO USE EUCLIDEAN DISTANCE COS THIS LOOKS RUBBISH
        self.grid[self.coord_to_index(goal_coords)].distance = 0
        queue = [goal_coords]  # where the number is the distance from the cell to the goal
        visited = np.full_like(self.grid, False, dtype=bool)  # to avoid revisiting the same cell over and over again
        visited[self.coord_to_index(goal_coords)] = True

        while len(queue) > 0:
            current_coord = queue.pop(0)
            current_distance = self.grid[self.coord_to_index(current_coord)].distance

            neighbouring_coords = self.get_neighbouring_coords(current_coord, include_diagonal=True)
            for next_coord in neighbouring_coords:
                index = self.coord_to_index(next_coord)
                if not visited[index]:
                    visited[index] = True
                    if tuple(current_coord) in self.blocked_cells:
                        continue

                    queue.append(next_coord)

                    # Calculate path cost based on movement direction
                    change_x = abs(next_coord[0] - current_coord[0])
                    change_y = abs(next_coord[1] - current_coord[1])
                    if change_x == 1 and change_y == 1:  # Diagonal movement
                        path_cost = np.sqrt(2)
                    else:  # Orthogonal movement
                        path_cost = 1

                    self.grid[index].distance = current_distance + path_cost

        """for index, bool in enumerate(visited):
            if False:
                print("WARNING")
                self.grid[index].velocity = np.zeros(2)"""

    def calculate_vectors(self):

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
            for index, distance in enumerate(distances):
                if distance == -1:
                   distances[index] = maximum + 1




            """if maximum in distances:
                if distances[0] == maximum:
                    distances[0] = distances[1] + 4
                if distances[1] == maximum:
                    distances[1] = distances[0] + 4
                if distances[2] == maximum:
                    distances[2] = distances[3] + 4
                if distances[3] == maximum:
                    distances[3] = distances[2] + 4"""




            x_vector = distances[1] - distances[0]
            y_vector = distances[2] - distances[3]

            cell.velocity = self.normalise_vector(np.array([x_vector, y_vector]))


    def update_velocity_field(self, coords_of_goal):
        if self.goal[0] != coords_of_goal[0] and self.goal[1] != coords_of_goal[1]:
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


    def checkForCollisionX(self, obj):
        pass



    def checkForCollisionY(self):
        pass






    def update(self):
        field_strength = 0.02
        for eachCell in self.grid:
            # velChange = self.normalise_vector(eachCell.velocity) * self.STRENGTH
            desired_velocity = eachCell.velocity * self.particle_max_velocity


            for eachParticle in eachCell.cellList:
                steering_force = desired_velocity - eachParticle.velocity

                eachParticle.velocity += (steering_force * field_strength) # + self.calculate_collision_avoidance(eachParticle)
                # self.zero_vel_for_blocked_cells(eachParticle)
        """for eachCell in self.grid:
            # velChange = self.normalise_vector(eachCell.velocity) * self.STRENGTH
            print(eachCell.velocity)

            for eachParticle in eachCell.cellList:

                eachParticle.velocity += eachCell.velocity"""

                # speed = self.get_magnitude(eachParticle.velocity) - 100000000
                # if speed > self.particle_max_velocity:
                #     eachParticle.velocity = (eachParticle.velocity / speed) * self.particle_max_velocity
    """def get_normalised_grid(self):
        return list(map(self.normalise_vector, self.grid))"""
