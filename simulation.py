import pygame
from particle import *



# todo:
# display vector
# create a spatial grid
# reduce refresh rate of spatial grid
# dynamically calculate which particles are in which box, so if i have slower particles, refresh grid list less often
# attempt to have the vector field influence the velocity of the particles
# integrate all the random variables into program.
# estimate density of each particle
# the smoothing curves, kernels etc. gaussian
# smooth the particles
# add a pressure system
# calculate pressure forces of each particle.
# P_i = k (p_i - p_0) | where p_i is the density of particle, p_0 is rest density, P_i is pressure

# then, complete navier-stokes function
# pressure force = sum_with_neighbours(m_j/p_j * mean pressure * kernel
# viscosity force
# external force, ie gravity
# and acceleration is the sum of these three forces.
# and repeat.



# like to have blur where it split the grid further and do a kernel convolution.





pygame.init()




def run():
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = SpatialMap(rows, columns)

    particles = [Particle(0.8, 3, vector_field, damping) for _ in range(noOfParticles)]
    print("high")
    vector_field.calculate_rest_density(particles) # integrate into __init



    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return


        ### drawing vectorField
        screen.fill((0, 69, 180))
        if drawGrid:

            for x in vector_field.get_grid_coords(x=True):
                pygame.draw.line(screen, "#353252", (x, 0), (x, screen_height), 1)

            for y in vector_field.get_grid_coords(y=True):
                pygame.draw.line(screen, "#353252", (0, y), (screen_width, y), 1)


            for coord, vector in zip(vector_field.get_grid_coords(), vector_field.get_normalised_grid()):
                boxCentre = (coord[0] + box_width/2, coord[1] + box_height/2)
                lineRadius = vector
                #pygame.draw.circle(screen, "#ff3542", (boxCentre), 4, 4)

#
        # logic goes here
        for particle in particles:
            particle.update(screen)

        # Drawing code goes here
        # total_density = 0
        for particle in particles:

            particle.calculate_density()
            # print(particle.density)
            # total_density += particle.density
            pygame.draw.circle(screen, (123,12,90), particle.get_position(), radius)
        # print("Total density: ", total_density)

        # Update display

        pygame.display.update()


        clock.tick(frame_rate)

    return

if __name__ == "__main__":
    run()


"""def brute_force(particle, particleList):
    neighbouring_particles = []
    for neighbour in particleList:
        distance = (particle.position - neighbour.position).magnitude()
        if distance < smoothing_radius:  # The smoothing radius is predefined
            neighbouring_particles.append(neighbour)

    return neighbouring_particles"""


