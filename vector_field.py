# Programming and drawing vector field
import pygame
import math
import numpy as np
from random import randrange

screen_width, screen_height = 768,512
rows, columns = 16, 16
box_width, box_height = screen_width / columns, screen_height / rows

clock = pygame.time.Clock()
frame_rate = 75
dt = 1 / frame_rate
radius = 4
noOfParticles = 40

class Spatial_Hash:
    def __init__(self, noOfRows, noOfCols): # may reshape into 2d array rather than 1d
        self.hash = [[[] for _ in range(noOfRows)] for _ in range(noOfCols)] # numpy not useful here because it's constantly changing size??
        # self.hash = np.empty((noOfRows, noOfCols))
        # self.hash.fill([]) # would like to test speed difference

    def hash_position(self, position):
        return (int(position[0] / box_width), int(position[1] / box_height))

    def update_particle(self, particle):
        self.remove_particle(particle)
        self.insert_particle(particle)




        # feels inefficient, ought to compare with linear search.

    def remove_particle(self, particle):
        cell = self.hash_position(particle.position)
        self.hash[cell[0]][cell[1]].remove(particle)
        # np.delete(self.hash[int(cell[0]), int(cell[1])], particle)


    def insert_particle(self, particle):
        new_cell = self.hash_position(particle.next_position)



        self.hash[new_cell[0]][new_cell[1]].append(particle)

        # np.append(self.hash[new_cell[0], new_cell[1]], particle)





class Vector_Field(Spatial_Hash):
    def __init__(self, noOfRows, noOfCols):
        super().__init__(noOfRows, noOfCols)

        self.noOfRows = noOfRows
        self.noOfCols = noOfCols

        ### creating vector field
        self.vectorField = list(map(self.normalise_vector, np.random.rand(self.noOfRows * self.noOfCols, 2)))


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




    def get_normalised_grid(self):
        return list(map(self.normalise_vector, self.vectorField))


    def get_magnitude(self, vector):
        return math.hypot(vector[0], vector[1])

    def normalise_vector(self, vector):
        return vector / self.get_magnitude(vector)

if __name__ == "__main__":
    field = Vector_Field(rows, columns)
    print(field.get_grid_coords())


