# import numpy as np
# PATHFINDER
from baseClasses import *

class Pathfinder(Particle):
    def __init__(self, mass, radius, vector_field, damping):
        super().__init__(mass, radius, vector_field, damping)


class VelocityField(SpatialMap):
    def __init__(self, noOfRows, noOfCols):
        super().__init__(noOfRows, noOfCols)
        print("\n\n\n\n")
        for i in self.grid:
            print(i.velocity)
        # self.vectorField = list(map(self.normalise_vector, np.random.rand(self.noOfRows * self.noOfCols, 2)))
        self.STRENGTH = 10




    def update(self):

        for eachCell in self.grid:
            velChange = self.normalise_vector(eachCell.velocity) * self.STRENGTH
            for eachParticle in eachCell.cellList:
                eachParticle.velocity += velChange


    """def get_normalised_grid(self):
        return list(map(self.normalise_vector, self.grid))"""





