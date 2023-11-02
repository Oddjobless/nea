import pygame.draw
from particle import *


"""
TODO: 
display vector
create a spatial hash
reduce refresh rate of spatial hash
dynamically calculate which particles are in which box, so if i have slower particles, refresh hash list less often
attempt to have the vector field influence the velocity of the particles
calculate density of each particle
look into the smoothing curves, kernels etc.
each little box will represent the fluid, ie the density. the 3x3 bit of each thing will influence its density. would 
like to have "motion blur" where it split the grid further and do a kernel convolution.
look into pressure
"""



pygame.init()




def run():
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = Vector_Field(rows, columns)

    particles = [Particle(0.8, 3, vector_field, damping) for _ in range(noOfParticles)]



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


        # logic goes here
        for particle in particles:
            particle.update(screen)


        # Drawing code goes here

        for particle in particles:
            vector_field.get_neighbouring_particles(particle)
            pygame.draw.circle(screen, (123,12,90), particle.get_position(), radius)


        # Update display

        pygame.display.update()


        clock.tick(frame_rate)

    return

if __name__ == "__main__":
    run()
