from Simulations.SimulationFiles.baseClasses import *
# ported from projectile sim. could make a ideal gas sim, with adjustable volume and more particles and higher temperature



def run():
    pygame.init()

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = Container(32, 18)
    frame_rate = 30




    clock = pygame.time.Clock()
    while True:




        screen.fill((70, 69, 5))
        vector_field.draw_walls(screen)
        vector_field.draw_slider(screen, pygame.mouse.get_pos())
        # draw gas container walls




        for index, particle in enumerate(vector_field.particles):
            particle.update(screen, custom_dimensions=vector_field.dimensions, vector_field=False)
            if vector_field.air_resistance:
                particle.apply_air_resistance()

        for particle in vector_field.particles:
            particle.collision_event()
            pygame.draw.circle(screen, particle.colour, particle.position, particle.radius)



        completed = set()
        for ball_i, ball_j in vector_field.colliding_balls_pairs:
            completed.add(ball_i)
            if ball_j not in completed:
                ball_i.resolve_dynamic_collision(ball_j)
                vector_field.collision_count += 1
                if vector_field.collision_spark:
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
                if event.button == 3 :
                    if vector_field.selected_wall_check(event.pos):
                        pygame.mouse.get_rel()
                        vector_field.wall_selected = vector_field.selected_wall_index(event.pos)
                    elif vector_field.selected_particle == None:
                        vector_field.project_particle(event.pos)


                elif event.button == 1:
                    if vector_field.reset_button.click_check(event.pos):
                        vector_field.initialise_container()


                    if vector_field.within_wall_check(event.pos):
                        vector_field.add_particle(event.pos)

                    elif vector_field.selected_particle == None:
                        vector_field.drag_particle(event.pos)

                    for widget in vector_field.widgets:
                        if widget.click_check(event.pos):
                            widget.is_clicked = not widget.is_clicked
                            print(widget.text, widget.is_clicked)
                            break



            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3 and vector_field.wall_selected != None:
                    vector_field.wall_selected = None


                if event.button == 1:
                    vector_field.temp_slider.is_clicked = False
                    if vector_field.selected_particle != None:
                        vector_field.drop_particle()

                elif event.button == 3 and vector_field.selected_particle != None:
                    vector_field.release_projected_particle(event.pos)

            if vector_field.wall_selected != None:
                vector_field.change_wall_dimensions(pygame.mouse.get_rel())


            elif vector_field.selected_particle != None and not vector_field.draw_line_to_mouse:
                vector_field.move_selected_particle(event.pos)




        pygame.display.update()

        clock.tick(frame_rate)


#

class GasParticle(Particle):
    def __init__(self, mass, particle_radius, vector_field, _wall_damping, velocity=None, position=None, colour=(123, 12, 255)):
        super().__init__(mass, particle_radius, vector_field, _wall_damping, velocity=velocity, position=position)
        self.colour = colour
    def update(self, screen, custom_dimensions=None, vector_field=False):
        super().update(screen, custom_dimensions=custom_dimensions, vector_field=vector_field)


class Widget:
    def __init__(self, position, size, colour, text=None, slider=False, parent=None, hover=True, alt_text=None, dynamic=False):
        self.position = np.array(position, dtype=float)
        self.size = np.array(size)
        self.colour = np.array(colour)
        self.default_colour = self.colour.copy()
        self.slider = slider
        self.parent = parent
        self.text = text
        self.alt_text = alt_text
        self.font = pygame.font.SysFont("Arial", 30)
        self.hover = hover
        self.dynamic = dynamic
        if slider:
            self.knob = self.position + self.size // 2
            self.knob_rest_pos = self.knob.copy()
            self.knob_value = 273


        self.is_clicked = False

    def draw(self, screen, mouse_pos):

        pygame.draw.rect(screen, self.colour, tuple(self.position) + tuple(self.size))

        if self.slider:

            pygame.draw.circle(screen, self.colour, (self.position[0], self.position[1] + self.size[1] // 2),
                               self.size[1] // 2)
            pygame.draw.circle(screen, self.colour, (self.position[0] + self.size[0], self.position[1] + self.size[1] // 2) ,
                               self.size[1] // 2)
            pygame.draw.circle(screen, (180, 180, 230), self.knob, self.size[1])
        else:
            if self.hover and self.position[0] < mouse_pos[0] < self.position[0] + self.size[0] and self.position[1] < mouse_pos[1] < self.position[1] + self.size[1]:
                pygame.draw.rect(screen, self.colour * 0.9, (self.position[0], self.position[1], self.size[0], self.size[1]))
            text = self.font.render(self.text, True, (0, 0, 0))
            pos = self.position + self.size // 2
            screen.blit(text, (pos[0] - text.get_width() // 2, pos[1] - text.get_height() // 2))


    def update(self):
        if self.is_clicked:
            if self.slider:
                self.knob[0] = max(min(pygame.mouse.get_pos()[0], self.knob_rest_pos[0] + 0.5 * self.size[0]), self.position[0])
                self.knob_value += 0.005 * (self.knob_rest_pos[0] - self.knob[0])
                self.knob_value = max(1, self.knob_value)
                self.parent.temperature_change(self.knob_value)



        elif self.slider:
            difference = self.knob_rest_pos - self.knob
            self.knob += difference * 0.2

        if self.dynamic and self.parent:
            dim = self.parent.dimensions
            pressure_sizes = 200, 100
            self.position = np.array([(dim[0] + dim[2] - pressure_sizes[0]) // 2, dim[1] - pressure_sizes[1] - self.parent.wall_radius])

    def click_check(self, pos):
        if self.slider:
            distance = np.sqrt((self.knob[0] - pos[0])**2 + (self.knob[1] - pos[1])**2)
            if distance < self.size[1]:
                return True
        else:
            if self.position[0] < pos[0] < self.position[0] + self.size[0] and self.position[1] < pos[1] < self.position[1] + self.size[1]:
                print(self.alt_text)
                if self.alt_text:
                    print("Switch")
                    self.text, self.alt_text = self.alt_text, self.text
                self.colour = self.default_colour
                return True
        return False
class Container(SpatialMap):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)
        self.particles = []
        self.selected_particle = None
        self.projected_particle_velocity_multiplier = 80
        self.dimensions = np.array([200,200,900,600]) # left, top, right, bottom
        self.font = pygame.font.SysFont("comicsans", int(self.box_width // 2.6))
        self.collision_count = 0
        self.collision_spark = True
        self.draw_line_to_mouse = False
        self.colliding_balls_pairs = []
        self.wall_selected = None
        self.wall_radius = 20

        dim = self.dimensions

        pressure_sizes = 200, 100
        pressure_pos = ((dim[0] + dim[2] - pressure_sizes[0]) // 2, dim[1] - pressure_sizes[1] - self.wall_radius)
        self.pressure_display = Widget(pressure_pos, pressure_sizes, (255, 255, 200), parent=self, dynamic=True)
        self.temp_slider = Widget((1480,900), (400,30), (140,140,140), slider=True, parent=self)
        self.particle_button = Widget((1560,400), (250,100), (140,140,140), text="Heavy Particles", alt_text="Light Particles")
        self.collision_counter = Widget((1480,500), (400,100), (140,140,140), text="Collision Count")
        self.reset_button = Widget((1480,700), (400,100), (140,140,140), text="Reset")
        self.stopwatch_button = Widget((1480,50), (300,150), (140,140,140), hover=False)
        self.pause_button = Widget((1480, 70), (150, 100), (200,80,30), text="Pause", alt_text="Start")
        self.widgets = [self.pressure_display, self.temp_slider, self.particle_button,self.pause_button, self.collision_counter, self.reset_button, self.stopwatch_button ]
        self.temperature = 293
        self.initial_temperature = 293


        self.initialise_container()

    # def calculate_volume(self):
    #     width, height = self.dimensions[2] - self.dimensions[0], self.dimensions[3] - self.dimensions[1]
    #     return 0.00001 * width * height

    def calculate_pressure(self):
        total_mass = 0
        for particle in self.particles:
            total_mass += particle.mass
        width, height = self.dimensions[2] - self.dimensions[0], self.dimensions[3] - self.dimensions[1]
        pressure = (total_mass * self.temperature) / (0.00001*width*height)
        return pressure

    def initialise_container(self):
        dim = self.dimensions
        base_v = 200
        self.temp_slider.knob_value = self.initial_temperature
        self.temperature = self.initial_temperature

        self.particles.clear()
        self.particles.extend([GasParticle(1, 8, self, 1.00, position=np.array(
            [randint(dim[0], dim[2]), randint(dim[1], dim[3])]), velocity=np.array(
            [randint(-base_v, base_v), randint(-base_v, base_v)], dtype=float)) for _ in range(50)])  # eccentricity
        self.rms_velocity = self.calculate_rms_velocity()
        self.pressure_display.text = f"{round(self.calculate_pressure())} Pa"



    def add_particle(self, mouse_position):
        if self.particle_button.is_clicked:
            obj = GasParticle(0.75, 6, self, 1.0, position=np.array(mouse_position, dtype=float))
            obj.colour = np.array([255, 60, 60])
            print(obj.colour)
        else:
            obj = GasParticle(1, 8, self, 1.0, position=np.array(mouse_position, dtype=float))

        self.particles.append(obj)
        self.calculate_rms_velocity()
        self.pressure_display.text = f"{round(self.calculate_pressure())} Pa"
    def temperature_change(self, new_temperature):
        change = new_temperature - self.temperature
        if abs(change) > 0.5:
            old_temperature = self.temperature
            self.temperature = new_temperature
            temperature_ratio = new_temperature / old_temperature
            self.rms_velocity = self.calculate_rms_velocity()
            self.pressure_display.text = f"{round(self.calculate_pressure())} Pa"
            for index, particle in enumerate(self.particles):
                particle.velocity *= temperature_ratio

    def calculate_rms_velocity(self):
        total_squared_velocity = sum(np.sum(particle.velocity ** 2) * 0.5 * particle.mass for particle in self.particles)
        rms_velocity = np.sqrt(total_squared_velocity / len(self.particles))
        return rms_velocity

    def draw_slider(self, screen, mouse_pos):

        for widget in self.widgets:
            widget.draw(screen, mouse_pos)
            widget.update()

    def stopwatch(self):
        pass

    def draw_walls(self, screen):
        dim = self.dimensions
        radius = self.wall_radius
        width = dim[2] - dim[0]
        height = dim[3] - dim[1]
        pygame.draw.rect(screen, (150,80,150), (0.75 * screen_width, 0, 0.25 * screen_width, screen_height))
        pygame.draw.rect(screen, (200,200,200), (
            dim[0] - radius, dim[1] - radius, width + 2 * radius,
            height + 2*radius))
        pygame.draw.rect(screen, (255,255,255), (dim[0], dim[1], width, height))


        # text = self.font.render(f"Temperature", True, (10,10,10))
        # screen.blit(text, (0.875 * screen_width - 0.5 * text.get_width(), 0.2 * screen_height))
        text = self.font.render(f"{round(self.temp_slider.knob_value,1)} K", True, (10,10,10))
        screen.blit(text, (0.875 * screen_width - 0.5 * text.get_width(), 0.25 * screen_height))
        text = self.font.render(f"{round(self.rms_velocity,1)} m/s", True, (10,10,10))
        screen.blit(text, (0.875 * screen_width - 0.5 * text.get_width(), 0.3 * screen_height))




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

    def within_wall_check(self, mouse_pos):
        dim = self.dimensions
        if dim[0] < mouse_pos[0] < dim[2] and dim[1] < mouse_pos[1] < dim[3]:
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
        dim = self.dimensions.copy()
        if index % 2:
            dim[index] += change[1]
        else:
            dim[index] += change[0]
        if not dim[2] + self.wall_radius < screen_width * 0.75:
            dim[2] = screen_width * 0.75 - self.wall_radius
        if 20 < dim[2] - dim[0] and dim[3] - dim[1] > 20:
            self.dimensions = dim
        self.pressure_display.text = f"{round(self.calculate_pressure())} Pa"





if __name__ == "__main__":
    run()
