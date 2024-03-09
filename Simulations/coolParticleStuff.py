import pygame
from baseClasses import *
# ported from projectile sim. could make a ideal gas sim, with adjustable volume and more particles and higher temperature



def run():
    pygame.init()

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = Container(rows, columns)

    vector_field.particles.extend([Particle(1, 20, vector_field, 1.00) for _ in range(100)])  # eccentricity
    font = pygame.font.SysFont("comicsans", int(box_width // 2.6))
    frame = 0
    mouse_rel_refresh = frame_rate * 0.5




    clock = pygame.time.Clock()
    while True:




        screen.fill((70, 69, 5))

        vector_field.draw_slider(screen)
        # draw gas container walls
        vector_field.draw_walls(screen)

        vector_field.temp_slider.update()

        for index, particle in enumerate(vector_field.particles):
            particle.update(screen, custom_dimensions=vector_field.dimensions, vector_field=False)
            if vector_field.air_resistance:
                print("oh no")
                particle.apply_air_resistance()

        for particle in vector_field.particles:
            particle.collision_event()
            pygame.draw.circle(screen, (123, 12, 90), particle.position, particle.radius)



        completed = set()
        for ball_i, ball_j in vector_field.colliding_balls_pairs:
            completed.add(ball_i)
            if ball_j not in completed:
                ball_i.resolve_dynamic_collision(ball_j)
                pygame.draw.line(screen, (0, 255, 0), ball_i.position, ball_j.position)
        vector_field.colliding_balls_pairs.clear()

        if vector_field.draw_line_to_mouse and vector_field.selected_particle != None:
            pygame.draw.line(screen, (255, 0, 0), vector_field.particles[vector_field.selected_particle].position, pygame.mouse.get_pos())
        else:
            vector_field.draw_line_to_mouse = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    return


            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and vector_field.selected_wall_check(event.pos):
                    pygame.mouse.get_rel()
                    vector_field.wall_selected = vector_field.selected_wall_index(event.pos)
                elif vector_field.temp_slider.click_check(event.pos):
                    vector_field.temp_slider.is_clicked = True
                elif event.button == 1 and vector_field.selected_particle == None:
                    vector_field.drag_particle(event.pos)

                elif event.button == 3 and vector_field.selected_particle == None:
                    vector_field.project_particle(event.pos)




            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3 and vector_field.wall_selected != None:
                    vector_field.wall_selected = None


                if event.button == 1 and vector_field.selected_particle != None:
                    vector_field.drop_particle()
                elif event.button == 1:
                    vector_field.temp_slider.is_clicked = False

                elif event.button == 3 and vector_field.selected_particle != None:
                    vector_field.release_projected_particle(event.pos)

            if vector_field.wall_selected != None:
                vector_field.change_wall_dimensions(pygame.mouse.get_rel())

            elif vector_field.selected_particle != None and not vector_field.draw_line_to_mouse:
                vector_field.move_selected_particle(event.pos)




        pygame.display.update()

        clock.tick(frame_rate)


#







class Widget:
    def __init__(self, position, size, colour, slider=False):
        self.position = np.array(position, dtype=float)
        self.size = np.array(size)
        self.colour = colour
        self.slider = slider
        if slider:
            self.knob = self.position + self.size // 2
            self.knob_rest_pos = self.knob.copy()
            self.knob_value = 1

        self.is_clicked = False

    def draw(self, screen):

        pygame.draw.rect(screen, self.colour, tuple(self.position) + tuple(self.size))
        if self.slider:

            pygame.draw.circle(screen, self.colour, (self.position[0], self.position[1] + self.size[1] // 2),
                               self.size[1] // 2)
            pygame.draw.circle(screen, self.colour, (self.position[0] + self.size[0], self.position[1] + self.size[1] // 2) ,
                               self.size[1] // 2)
            pygame.draw.circle(screen, (180, 180, 230), self.knob, self.size[1])



    def update(self):
        if self.is_clicked:
            self.knob[0] = pygame.mouse.get_pos()[0]
        else:
            difference = self.knob_rest_pos - self.knob
            self.knob += difference * 0.1
    def click_check(self, pos):
        if self.slider:
            distance = np.sqrt((self.knob[0] - pos[0])**2 + (self.knob[1] - pos[1])**2)
            if distance < self.size[1]:
                print("Click")
                return True
        else:
            if self.position[0] < pos[0] < self.position[0] + self.size[0] and self.position[1] < pos[1] < self.position[1] + self.size[1]:
                return True
        return False

class Container(SpatialMap):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)
        self.particles = []
        self.selected_particle = None
        self.projected_particle_velocity_multiplier = 80
        self.dimensions = np.array([200,200,900,600]) # left, top, right, bottom

        self.draw_line_to_mouse = False
        self.colliding_balls_pairs = []
        self.wall_selected = None
        self.wall_radius = 20
        self.temp_slider = Widget((1400,900), (400,30), (140,140,140), slider=True)

    def draw_slider(self, screen):
        self.temp_slider.draw(screen)


    def draw_walls(self, screen):
        dim = self.dimensions
        radius = self.wall_radius

        pygame.draw.rect(screen, (200,200,200), (
            dim[0] - radius, dim[1] - radius, dim[2] - dim[0] + 2* radius,
            dim[3] - dim[1] + 2*radius))
        pygame.draw.rect(screen, (255,255,255), (
        dim[0], dim[1], dim[2] - dim[0],
        dim[3] - dim[1]))

    def selected_wall_check(self, mouse_pos):
        dim = self.dimensions
        radius = self.wall_radius
        checks = np.array([
            dim[0] - radius < mouse_pos[0] < dim[2] + radius and not dim[0] < mouse_pos[0] < dim[2],
            dim[1] - radius < mouse_pos[1] < dim[3] + radius and not dim[1] < mouse_pos[1] < dim[3]
        ])
        if checks.any():
            return True

        return False
    
    def selected_wall_index(self, mouse_pos):
        dim = self.dimensions
        radius = self.wall_radius
        if dim[0] - radius < mouse_pos[0] < dim[0]: # left wall
            print("left wall")
            return 0

        elif dim[1] - radius < mouse_pos[1] < dim[1]: # top wall
            print("top wall")
            return 1

        elif dim[2] < mouse_pos[0] < dim[2] + radius: # right wall
            print("right wall")
            return 2

        elif dim[3] < mouse_pos[1] < dim[3] + radius: # bottom wall
            print("bottom wall")
            return 3
        else:
            print(ValueError("no wall selected, but collision event"))
            return None # should never happen
    def change_wall_dimensions(self, change):
        index = self.wall_selected
        if index % 2:
            self.dimensions[index] += change[1]
        else:
            self.dimensions[index] += change[0]





if __name__ == "__main__":
    print("piss")
    run()
