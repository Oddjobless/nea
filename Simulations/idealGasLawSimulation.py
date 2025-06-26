from Simulations.SimulationFiles.baseClasses import *
import pygame


def run():
    pygame.init()
    screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Ideal Gas Law Simulation")

    container = Container(32, 18, (screen_width, screen_height))
    frame_rate = container.frame_rate
    clock = pygame.time.Clock()

    while True:
        screen.fill((78, 198, 140))

        # Draw layout
        container.draw_walls(screen)
        container.draw_widgets(screen, pygame.mouse.get_pos())

        # Update particles
        for index, particle in enumerate(container.particles):
            particle.update(screen, custom_dimensions=container.dimensions, vector_field=False)

        for particle in container.particles:
            particle.collision_event()
            pygame.draw.circle(screen, particle.colour, particle.position, particle.radius)

        # Handle collisions
        completed = set()
        for ball_i, ball_j in container.colliding_balls_pairs:
            completed.add(ball_i)
            if ball_j not in completed:
                ball_i.resolve_dynamic_collision(ball_j)
                if container.spark_button.text == "Collision Sparks Enabled":
                    pygame.draw.line(screen, (0, 255, 0), ball_i.position, ball_j.position, width=5)
        container.colliding_balls_pairs.clear()

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    return

            # Selecting container wall
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # RMB
                    if container.selected_wall_check(event.pos):
                        pygame.mouse.get_rel()
                        container.wall_selected = container.selected_wall_index(event.pos)

                elif event.button == 1:  # LMB
                    if container.reset_button.click_check(event.pos):  # Reset button
                        container.initialise_container()

                    if container.within_wall_check(event.pos):  # Add particles
                        container.add_particle(event.pos)
                        container.rms_velocity = container.calculate_rms_velocity()

                    for widget in container.widgets:  # General widget handler
                        if widget.click_check(event.pos):
                            widget.is_clicked = not widget.is_clicked
                            break

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3 and container.wall_selected is not None:
                    container.wall_selected = None  # Release container wall

                if event.button == 1:  # Release temperature slider
                    container.temp_slider.is_clicked = False

            if container.wall_selected is not None:  # Adjust wall dimensions if wall is selected
                container.change_wall_dimensions(pygame.mouse.get_rel())  # Move container wall

        pygame.display.update()
        clock.tick(frame_rate)


class GasParticle(Particle):
    def __init__(self, mass, particle_radius, container, velocity=None, position=None, colour=(123, 12, 255)):
        super().__init__(mass, particle_radius, container, velocity=velocity, position=position)
        self.colour = colour  # Distinguishes heavy and light particles
        self.damping = 1

    def update(self, screen, custom_dimensions=None, vector_field=False):
        super().update(screen, custom_dimensions=custom_dimensions, vector_field=vector_field)


class Widget:
    def __init__(self, position, size, colour, text=None, slider=False, parent=None, hover=True, alt_text=None, dynamic=False):
        self.position = np.array(position, dtype=float)  # Top left corner
        self.size = np.array(size)  # (width, height)
        self.colour = np.array(colour)
        self.default_colour = self.colour.copy()
        self.slider = slider
        self.parent = parent  # i.e. the container the widget is bound to
        self.text = text
        self.alt_text = alt_text
        self.font = pygame.font.SysFont("Arial", 30)
        self.hover = hover  # Should the widget respond the cursor hovering over it?
        self.dynamic = dynamic  # Does the widget move?
        self.is_clicked = False
        if slider:  # Currently only used for the temperature
            self.knob = self.position + self.size // 2
            self.knob_rest_pos = self.knob.copy()
            self.knob_value = 273

    def draw(self, screen, mouse_pos):  # Drawing the widget on the screen
        pygame.draw.rect(screen, self.colour, tuple(self.position) + tuple(self.size))

        if self.slider:
            pygame.draw.circle(screen, self.colour, (self.position[0], self.position[1] + self.size[1] // 2),
                               self.size[1] // 2)
            pygame.draw.circle(screen, self.colour,
                               (self.position[0] + self.size[0], self.position[1] + self.size[1] // 2),
                               self.size[1] // 2)
            pygame.draw.circle(screen, (180, 180, 230), self.knob, self.size[1])

        else:
            if self.hover and self.position[0] < mouse_pos[0] < self.position[0] + self.size[0] and self.position[1] < \
                    mouse_pos[1] < self.position[1] + self.size[1]:
                pygame.draw.rect(screen, self.colour * 0.9, (self.position[0], self.position[1], self.size[0], self.size[1]))
            text = self.font.render(self.text, True, (0, 0, 0))
            pos = self.position + self.size // 2
            screen.blit(text, (pos[0] - text.get_width() // 2, pos[1] - text.get_height() // 2))

    def update(self):  # Check for changes
        if self.is_clicked:
            if self.slider:
                self.knob[0] = max(min(pygame.mouse.get_pos()[0], self.knob_rest_pos[0] + 0.5 * self.size[0]),
                                   self.position[0])
                self.knob_value += 0.01 * (self.knob_rest_pos[0] - self.knob[0])
                self.knob_value = max(1, self.knob_value)
                self.parent.temperature_change(self.knob_value)

        elif self.slider:
            difference = self.knob_rest_pos - self.knob
            self.knob += difference * 0.2

        if self.dynamic and self.parent:
            dim = self.parent.dimensions
            pressure_sizes = 250, 100
            self.position = np.array(
                [(dim[0] + dim[2] - pressure_sizes[0]) // 2, dim[1] - pressure_sizes[1] - self.parent.wall_radius])

    def click_check(self, pos):  # Checks whether widget has been interacted with
        if self.slider:
            distance = np.sqrt((self.knob[0] - pos[0]) ** 2 + (self.knob[1] - pos[1]) ** 2)

            if distance < self.size[1]:
                return True

        else:
            if self.position[0] < pos[0] < self.position[0] + self.size[0] and self.position[1] < pos[1] < \
                    self.position[1] + self.size[1]:

                if self.alt_text:
                    self.text, self.alt_text = self.alt_text, self.text

                self.colour = self.default_colour
                return True
        return False


class Container(SpatialMap):
    def __init__(self, rows, columns, screen_size):
        # Initialising variables
        super().__init__(rows, columns, screen_size=screen_size)
        self.rms_velocity = None
        self.R = 8.3145  # Boltzmann's constant
        self.px_to_metres = 0.1
        self.dimensions = np.array([200, 200, 1000, 850])  # left, top, right, bottom: container wall positions
        self.font = pygame.font.SysFont("comicsans", int(self.box_width // 2.6))
        self.small_font = pygame.font.SysFont("comicsans", int(self.box_width // 4))
        self.colliding_balls_pairs = []  # Used for collision resolution
        self.wall_selected = None
        self.wall_radius = 20  # Wall width
        self.damping = 1  # No energy lost during collision - ideal gas law
        self.temperature = 293
        self.initial_temperature = 293  # Needed for resetting container

        # Creating widgets
        dim = self.dimensions
        pressure_sizes = 250, 100
        pressure_pos = ((dim[0] + dim[2] - pressure_sizes[0]) // 2, dim[1] - pressure_sizes[1] - self.wall_radius)
        self.pressure_display = Widget(pressure_pos, pressure_sizes, (255, 255, 200), parent=self, dynamic=True,
                                       hover=False)
        self.temp_slider = Widget((1480, 410), (400, 30), (81, 228, 81), slider=True, parent=self)
        self.particle_button = Widget((1560, 630), (250, 100), (166, 179, 215), text="Heavy Particles",
                                      alt_text="Light Particles")
        self.reset_button = Widget((1480, 900), (400, 100), (242, 125, 125), text="RESET")
        self.spark_button = Widget((1490, 770), (380, 75), (237, 234, 116), text="Collision Sparks Enabled",
                                   alt_text="Collision Sparks Disabled")
        self.widgets = [self.pressure_display, self.temp_slider, self.particle_button, self.reset_button,
                        self.spark_button]

        self.initialise_container()

    def initialise_container(self):  # Also used for resetting the container
        dim = self.dimensions
        base_v = 55  # Initial velocity of particles
        self.temp_slider.knob_value = self.initial_temperature
        self.temperature = self.initial_temperature

        self.particles.clear()  # Remove all particles to reset container
        self.particles.extend([GasParticle(0.1, 8, self, position=np.array(
            [randint(dim[0], dim[2]), randint(dim[1], dim[3])]), velocity=np.array(
            [randint(-base_v, base_v), randint(-base_v, base_v)], dtype=float)) for _ in range(50)])
        self.rms_velocity = self.calculate_rms_velocity()
        self.pressure_display.text = f"{self.calculate_pressure() * 1000:<.2f} mPa"

    def calculate_pressure(self):  # P = (nRT)/V
        width, height = (self.dimensions[2] - self.dimensions[0]) / self.px_to_metres, (
                self.dimensions[3] - self.dimensions[1]) / self.px_to_metres
        pressure = (len(self.particles) * self.R * self.temperature) / (width * height)
        return pressure

    def calculate_rms_velocity(self):
        total_square_vel = 0.0
        for particle in self.particles:
            squared_velocity_magnitude = np.sum((particle.velocity / self.px_to_metres) ** 2)
            total_square_vel += 0.5 * particle.mass * squared_velocity_magnitude

        rms = np.sqrt(total_square_vel / len(self.particles))
        return rms

    def add_particle(self, mouse_position):  # Add heavy or light particle at cursor
        if self.particle_button.is_clicked:
            obj = GasParticle(0.06, 5, self, position=np.array(mouse_position, dtype=float))
            obj.colour = np.array([255, 60, 60])
        else:
            obj = GasParticle(0.1, 8, self, position=np.array(mouse_position, dtype=float))

        self.particles.append(obj)
        self.pressure_display.text = f"{self.calculate_pressure() * 1000:<.2f} mPa"

    def temperature_change(self, new_temperature):  # i.e. when slider is changed
        change = new_temperature - self.temperature
        if abs(change) > 0.5:  # Only update if big enough interval
            old_temperature = self.temperature
            self.temperature = new_temperature
            temperature_ratio = new_temperature / old_temperature

            # Update simulation parameters
            self.rms_velocity = self.calculate_rms_velocity()
            self.pressure_display.text = f"{self.calculate_pressure() * 1000:<.2f} mPa"
            for index, particle in enumerate(self.particles):
                particle.velocity *= temperature_ratio

    def draw_widgets(self, screen, mouse_pos):  # Widget handler
        for widget in self.widgets:
            widget.draw(screen, mouse_pos)
            widget.update()

    def draw_walls(self, screen):  # draw container + text
        screen_width, screen_height = screen.get_width(), screen.get_height()
        dim = self.dimensions
        radius = self.wall_radius
        width = dim[2] - dim[0]
        height = dim[3] - dim[1]
        pygame.draw.rect(screen, (161, 221, 208), (0.75 * screen_width, 0, 0.25 * screen_width, screen_height))
        pygame.draw.rect(screen, (200, 200, 200), (
            dim[0] - radius, dim[1] - radius, width + 2 * radius,
            height + 2 * radius))
        pygame.draw.rect(screen, (255, 255, 255), (dim[0], dim[1], width, height))

        # Output the widget text
        text = self.small_font.render(f"Heat Up", True, (10, 10, 10))
        screen.blit(text, (0.79 * screen_width - 0.5 * text.get_width(), 450))
        text = self.small_font.render(f"Cool Down", True, (10, 10, 10))
        screen.blit(text, (0.96 * screen_width - 0.5 * text.get_width(), 450))
        text = self.font.render(f"{round(self.temp_slider.knob_value, 1)} \u00B0K", True, (10, 10, 10))
        screen.blit(text, (0.875 * screen_width - 0.5 * text.get_width(), 325))
        text = self.small_font.render("Root Mean Square Speed", True, (10, 10, 10))
        screen.blit(text, (0.875 * screen_width - 0.5 * text.get_width(), 100))
        text = self.small_font.render("AKA The Average Speed:", True, (10, 10, 10))
        screen.blit(text, (0.875 * screen_width - 0.5 * text.get_width(), 130))
        text = self.font.render(f"{round(self.rms_velocity, 1)} m/s", True, (10, 10, 10))
        screen.blit(text, (0.875 * screen_width - 0.5 * text.get_width(), 170))
        text = self.small_font.render("Spawn particles", True, (10, 10, 10))
        screen.blit(text, (0.875 * screen_width - 0.5 * text.get_width(), 550))
        text = self.small_font.render("with your left click!", True, (10, 10, 10))
        screen.blit(text, (0.875 * screen_width - 0.5 * text.get_width(), 580))

    def selected_wall_check(self, mouse_pos):  # checking if ANY wall has been selected
        dim = self.dimensions
        radius = self.wall_radius
        checks = np.array([
            dim[0] - radius < mouse_pos[0] < dim[2] + radius and not dim[0] < mouse_pos[0] < dim[2],
            dim[1] - radius < mouse_pos[1] < dim[3] + radius and not dim[1] < mouse_pos[1] < dim[3]
        ])
        if checks.any():
            return True
        return False

    def within_wall_check(self, mouse_pos):  # Checks if mouse is inside walls, not including walls themselves
        dim = self.dimensions
        if dim[0] < mouse_pos[0] < dim[2] and dim[1] < mouse_pos[1] < dim[3]:
            return True
        return False

    def selected_wall_index(self, mouse_pos):  # Returns index of the selected wall
        dim = self.dimensions
        radius = self.wall_radius
        if dim[0] - radius < mouse_pos[0] < dim[0]:  # left wall
            return 0

        elif dim[1] - radius < mouse_pos[1] < dim[1]:  # top wall
            return 1

        elif dim[2] < mouse_pos[0] < dim[2] + radius:  # right wall
            return 2

        elif dim[3] < mouse_pos[1] < dim[3] + radius:  # bottom wall
            return 3
        else:
            return None

    def change_wall_dimensions(self, change):  # Update container dimensions
        index = self.wall_selected
        dim = self.dimensions.copy()
        if index % 2:  # If the top or bottom wall is selected
            dim[index] += change[1]
        else:  # If left or right wall is selected
            dim[index] += change[0]

        # Container dimensions validation
        if not dim[2] + self.wall_radius < self.screen_width * 0.75:
            dim[2] = self.screen_width * 0.75 - self.wall_radius
        if 20 < dim[2] - dim[0] and dim[3] - dim[1] > 20:
            self.dimensions = dim
        self.pressure_display.text = f"{self.calculate_pressure() * 1000:<.2f} mPa"