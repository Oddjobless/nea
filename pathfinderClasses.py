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
        goal = np.array([3,3])
        self.field_strength = 80
        self.goal_position = self.undo_hash_position(goal)
        self.update_velocity_field(goal)
        self.particle_max_velocity = 500
        self.print_visited()
        # self.particle_damping = 0.996 # dont like this


        # todo: distance from a cell to its neighbouring diagonal is sqrt(2) or 2?

    def print_visited(self):
        for i in range(rows):
            for j in range(columns):
                print(self.grid[self.coord_to_index((i, j))].distance, end=" | ")
            print()

    def toggle_blocked_cell(self, coord):
        if not coord in self.blocked_cells:
            self.blocked_cells.add(coord)
        else:
            self.blocked_cells.discard(coord)
        print(self.blocked_cells)





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
                    queue.append(next_coord)

                    # Calculate path cost based on movement direction
                    change_x = abs(next_coord[0] - current_coord[0])
                    change_y = abs(next_coord[1] - current_coord[1])
                    if change_x == 1 and change_y == 1:  # Diagonal movement
                        path_cost = np.sqrt(2)
                    else:  # Orthogonal movement
                        path_cost = 1

                    self.grid[index].distance = current_distance + path_cost

    def calculate_vectors(self):

        for index, cell in enumerate(self.grid):
            if self.index_to_coord(index) in self.blocked_cells:
                cell.velocity = np.array([0,0])
                continue
            coords = self.get_neighbouring_coords(self.index_to_coord(index), placeholder_for_boundary=True)

            distances = [0, 0, 0, 0] # left, right, up , down etc
            for index, eachcoord in enumerate(coords):
                if eachcoord and eachcoord not in self.blocked_cells:
                    distances[index] = self.grid[self.coord_to_index(eachcoord)].distance
                else:
                    distances[index] = 10



            x_vector = distances[0] - distances[1]
            y_vector = distances[2] - distances[3]

            cell.velocity = self.normalise_vector(np.array([x_vector, y_vector]))


    def update_velocity_field(self, coords_of_goal):
        self.generate_heatmap(coords_of_goal)
        self.calculate_vectors()

    def calculate_steering_force(self, particle):
        pass





    def update(self):

        for eachCell in self.grid:
            # velChange = self.normalise_vector(eachCell.velocity) * self.STRENGTH
            desired_velocity = eachCell.velocity * self.particle_max_velocity
            print(eachCell.velocity)

            for eachParticle in eachCell.cellList:

                steering_force = desired_velocity - eachParticle.velocity
                eachParticle.velocity += steering_force / self.field_strength

                # speed = self.get_magnitude(eachParticle.velocity) - 100000000
                # if speed > self.particle_max_velocity:
                #     eachParticle.velocity = (eachParticle.velocity / speed) * self.particle_max_velocity
    """def get_normalised_grid(self):
        return list(map(self.normalise_vector, self.grid))"""
