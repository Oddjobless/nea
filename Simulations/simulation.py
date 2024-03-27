# from pathfinderClasses import *
from Simulations.SimulationFiles.pathfinderClasses import *


# todo: , euclidean), , deal with fluid flow sim, back to this, kernel convolution, steering,

# like to have blur where it split the grid further and do a kernel convolution.

"""
should I have a spatial map where each cell keeps track of the particles within its boundaries with a list and influence their velocities that way; or find which cell the particle resides and influence its velocity that way?

WILL START WITH OPTION 1 COS I ALREADY HAVE IT SET UP FROM FLUID FLOW SIM
OPTION 2 LIKELY BETTER THOUGH
"""







def run(rows, columns, max_velocity):
    pygame.init()
    # todo:
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = VelocityField(rows, columns, max_velocity)
    box_width, box_height = vector_field.box_width, vector_field.box_height

    vector_field.particles = [Pathfinder(radius//3, radius, vector_field, wall_damping) for _ in range(noOfParticles)]
    # vector_field.calculate_rest_density(particles) # integrate into __init
    font = pygame.font.SysFont("comicsans", int(box_width // 2.6))

    clock = pygame.time.Clock()

    """
    LEFT CLICK: set new goal 
    RIGHT CLICK: toggle blocked cells
    Q: quit
    
    """

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    return
                elif event.key == pygame.K_a: # switch between adding particles and changing goal
                    vector_field.is_adding_particles = not vector_field.is_adding_particles
                elif event.key == pygame.K_c: # toggle collisions. turn off to reduce latency
                    vector_field.enable_collision_between_particles = not vector_field.enable_collision_between_particles
                elif event.key == pygame.K_EQUALS: # plus symbol
                    vector_field.particle_to_add_radius += 1
                elif event.key == pygame.K_MINUS: # minus symbol
                    vector_field.particle_to_add_radius = max(vector_field.particle_to_add_radius - 1, 3)
                elif event.key == pygame.K_h:
                    vector_field.draw_heatmap = not vector_field.draw_heatmap
                elif event.key == pygame.K_g:
                    vector_field.draw_grid = not vector_field.draw_grid


            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    cell = vector_field.index_to_coord(vector_field.hash_position(pygame.mouse.get_pos()))
                    vector_field.toggle_adding_cells(cell)


            click_event = pygame.mouse.get_pressed()
            if any(click_event):
                pos_cell_index = vector_field.index_to_coord(vector_field.hash_position(pygame.mouse.get_pos()))
                if click_event[0]: # LEFT CLICK
                    vector_field.update_velocity_field(pos_cell_index)

                elif click_event[2]: # RIGHT CLICK
                    if not vector_field.is_adding_particles:
                        vector_field.toggle_blocked_cell(pos_cell_index)
                    else:
                        vector_field.add_particle(pygame.mouse.get_pos())
        ### drawing vectorField
        screen.fill((200, 200, 200))


        if vector_field.draw_heatmap:
            vector_field.display_heatmap(screen)


        for cell in vector_field.blocked_cells:
            pygame.draw.rect(screen, (0, 0, 0, 0.5), (cell[0] * box_width, cell[1] * box_height, box_width, box_height))

        if vector_field.draw_grid:
            for x in vector_field.get_grid_coords(x=True):
                pygame.draw.line(screen, "#353252", (x, 0), (x, screen_height), 1)

            for y in vector_field.get_grid_coords(y=True):
                pygame.draw.line(screen, "#353252", (0, y), (screen_width, y), 1)


            for coord, cell, distance in zip(vector_field.get_grid_coords(), vector_field.grid, vector_field.cell_distances):

                boxCentre = np.array([coord[0] + box_width/2, coord[1] + box_height/2])
                lineRadius = (box_width/2.2) * cell.velocity
                if not any(np.isnan(cell.velocity)):
                    pygame.draw.line(screen, "#ff3542", (boxCentre), boxCentre+lineRadius)
                if draw_distances and distance > 0:
                    number = font.render(f"{distance:.1f}", True, (255, 255, 255))
                    screen.blit(number, boxCentre - (box_width//4))









        if vector_field.enable_collision_between_particles:
            for particle in vector_field.particles:
                particle.collision_event_particles()

        """for i in vector_field.grid:
            print(i.cellList, end="")"""
        vector_field.update()
        for particle in vector_field.particles:
            particle.update(screen)  # updates position of particles

        # total_density = 0
        for particle in vector_field.particles:
            pygame.draw.circle(screen, (123,12,90), particle.get_position(), particle.radius)



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


