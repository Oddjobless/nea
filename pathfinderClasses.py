# import numpy as np
# PATHFINDER
import numpy as np

from baseClasses import *


class Pathfinder(Particle):
    def __init__(self, mass, radius, vector_field, damping):
        super().__init__(mass, radius, vector_field, damping)


class VelocityField(SpatialMap):
    def __init__(self, noOfRows, noOfCols):
        super().__init__(noOfRows, noOfCols)
        for i in self.grid:
            print(i.velocity)
        self.STRENGTH = 3
        # todo: distance from a cell to its neighbouring diagonal is sqrt(2) or 2?

    def generate_heatmap(self, goal_coords):  # (x,y)
        self.grid[self.coord_to_index(goal_coords)].distance = 0
        queue = [goal_coords]  # where the number is the distance from the cell to the goal
        visited = np.full_like(self.grid, False, dtype=bool)  # to avoid revisiting the same cell over and over again
        visited[self.coord_to_index(goal_coords[0], goal_coords[1])] = True

        while len(queue) > 0:
            current_coord = queue.pop(0)
            index = self.coord_to_index(current_coord[0], current_coord[1])
            current_distance = self.grid[index].distance
            for coord in self.get_neighbouring_coords(current_coord[0], current_coord[1]):
                if not visited[index]:
                    visited[index] = True
                    queue.append(coord)
                    self.grid[index].distance = current_distance + 1

    def update(self):

        for eachCell in self.grid:
            velChange = self.normalise_vector(eachCell.velocity) * self.STRENGTH
            for eachParticle in eachCell.cellList:
                eachParticle.velocity += velChange

    """def get_normalised_grid(self):
        return list(map(self.normalise_vector, self.grid))"""
