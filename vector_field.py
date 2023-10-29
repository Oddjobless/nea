# Programming and drawing vector field
import pygame
import math
import numpy as np
from random import randrange

screen_width, screen_height = 1024,1024
rows, columns = 128, 128
box_width, box_height = screen_width / columns, screen_height / rows

clock = pygame.time.Clock()
frame_rate = 75
dt = 1 / frame_rate

noOfParticles = 1000



class Vector_Field:
    def __init__(self, noOfRows, noOfCols):
        self.noOfRows = noOfRows
        self.noOfCols = noOfCols

        ### creating vector field
        self.grid = list(map(self.normalise_vector, np.random.rand(self.noOfRows * self.noOfCols, 2)))


    def get_grid_coords(self):
        xCoords = np.linspace(0, screen_width, self.noOfCols, endpoint=False)
        yCoords = np.linspace(0, screen_height, self.noOfRows, endpoint=False)
        xValues, yValues = np.array(np.meshgrid(xCoords, yCoords))
        coords = np.column_stack((xValues.ravel(), yValues.ravel()))
        return coords

    def get_x_list(self):
        xCoords = np.linspace(0, screen_width, self.noOfCols, endpoint=False)
        return xCoords

    def get_y_list(self):
        yCoords = np.linspace(0, screen_height, self.noOfRows, endpoint=False)
        return yCoords


    def get_normalised_grid(self):
        return list(map(self.normalise_vector, self.grid))


    def get_magnitude(self, vector):
        return math.hypot(vector[0], vector[1])

    def normalise_vector(self, vector):
        return vector / self.get_magnitude(vector)

if __name__ == "__main__":
    field = Vector_Field(rows, columns)
    print(field.get_grid_coords())


