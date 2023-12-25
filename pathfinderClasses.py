# import numpy as np
# PATHFINDER
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
        self.heatmap = np.full_like(self.grid, np.inf, dtype=float) # distances from the cells to the goal
        # todo: distance from a cell to its neighbouring diagonal is sqrt(2) or 2?
    def generate_heatmap(self, goal_coords): # (x,y)
        self.heatmap[self.coord_to_index(goal_coords)] = 0
        queue = [(goal, 0)] # where the number is the distance from the cell to the goal
        while len(queue) > 0:
            cell, distance = queue.pop(0)
            self.heatmap[cell] = distance
            for neighbour in self.get_neighbours(cell):
                if neighbour not in self.heatmap:
                    queue.append((neighbour, distance + 1))



    def update(self):

        for eachCell in self.grid:
            velChange = self.normalise_vector(eachCell.velocity) * self.STRENGTH
            for eachParticle in eachCell.cellList:
                eachParticle.velocity += velChange


    """def get_normalised_grid(self):
        return list(map(self.normalise_vector, self.grid))"""





