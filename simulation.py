import pygame
from pathfinderClasses import *



# todo: heatmap generation (wavefront algo, euclidean), velocity field, complete, deal with fluid flow sim, back to this, kernel convolution, steering,

# like to have blur where it split the grid further and do a kernel convolution.

"""
should I have a spatial map where each cell keeps track of the particles within its boundaries with a list and influence their velocities that way; or find which cell the particle resides and influence its velocity that way?

WILL START WITH OPTION 1 COS I ALREADY HAVE IT SET UP FROM FLUID FLOW SIM
OPTION 2 LIKELY BETTER THOUGH
"""



pygame.init()




def run():
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = VelocityField(rows, columns)

    particles = [Pathfinder(10, 3, vector_field, wall_damping) for _ in range(noOfParticles)]
    print("high")
    # vector_field.calculate_rest_density(particles) # integrate into __init



    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos_cell_index = vector_field.index_to_coord(vector_field.hash_position(pygame.mouse.get_pos()))
                vector_field.update_velocity_field(pos_cell_index)

        ### drawing vectorField
        screen.fill((0, 69, 180))
        if drawGrid:

            for x in vector_field.get_grid_coords(x=True):
                pygame.draw.line(screen, "#353252", (x, 0), (x, screen_height), 1)

            for y in vector_field.get_grid_coords(y=True):
                pygame.draw.line(screen, "#353252", (0, y), (screen_width, y), 1)


            """for coord, vector in zip(vector_field.get_grid_coords(), vector_field.grid()):
                boxCentre = (coord[0] + box_width/2, coord[1] + box_height/2)
                lineRadius = vector
                pygame.draw.circle(screen, "#ff3542", (boxCentre), 4, 4)"""

#
        # logic goes here
        for particle in particles:
            particle.update(screen) # updates position of particles
        vector_field.update()

        """for i in vector_field.grid:
            print(i.cellList, end="")"""


        # Drawing code goes here
        # total_density = 0
        for particle in particles:

            # particle.calculate_density()  # todo i want it to do this less often
            # particle.calculate_pressure()  # todo ditto

            # print(particle.get_pressure_force())
            # total_density += particle.density
            pygame.draw.circle(screen, (123,12,90), particle.get_position(), radius)

        # print("Total density: ", total_density)

        # Update display

        pygame.display.update()


        clock.tick(frame_rate)



if __name__ == "__main__":
    run()


"""def brute_force(particle, particleList):
    neighbouring_particles = []
    for neighbour in particleList:
        distance = (particle.position - neighbour.position).magnitude()
        if distance < smoothing_radius:  # The smoothing radius is predefined
            neighbouring_particles.append(neighbour)

    return neighbouring_particles"""


