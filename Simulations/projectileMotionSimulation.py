import pygame
import time
from Simulations.SimulationFiles.baseClasses import *


def draw_mode(level_no, penetration_factor=0.15):
    pygame.init()
    frame_rate = 30
    screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pygame.display.set_mode((screen_width, screen_height))
    obstacles = []
    goal_background_image = pygame.image.load("./Simulations/SimulationFiles/Assets/images/images.jpg")
    goal_background_image.convert_alpha()

    # wall_image = pygame.image.load("./Simulations/SimulationFiles/Assets/images/wall.png")
    print("Wall loaded")

    pygame.display.set_caption("Create Level")
    background = pygame.image.load("./Simulations/SimulationFiles/Assets/images/background1.jpg")
    background = pygame.transform.scale(background, (screen_width, screen_height))

    rect_origin = None
    rect_params = None
    mouse_hold = False

    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Helvetica", 35)
    while True:
        screen.fill((169, 130, 40))
        screen.blit(background, (0, 0))

        if rect_origin is not None and rect_params is not None:
            rect_x = rect_origin[0] - abs(rect_params[0]) if rect_params[0] < 0 else rect_origin[0]
            rect_y = rect_origin[1] - abs(rect_params[1]) if rect_params[1] < 0 else rect_origin[1]
            if obstacles:

                pygame.draw.rect(screen, (255, 0, 0), (rect_x, rect_y, abs(rect_params[0]), abs(rect_params[1])))
            else:
                radius = int(np.sqrt(rect_params[0] ** 2 + rect_params[1] ** 2))
                pygame.draw.circle(screen, (255, 255, 255), rect_origin, radius)

        for obstacle in obstacles:
            obstacle.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    return

                elif event.key == pygame.K_s:
                    if obstacles:  # checks if the user has added a goal
                        with open(("./Simulations/SimulationFiles/Assets/ProjectileLevels/lvl" + str(level_no)),
                                  "w") as file:
                            file.write(f"{penetration_factor}\n")
                            goal = obstacles[0]
                            file.write(
                                f"{goal.position[0]},{goal.position[1]},{goal.width},{goal.height}")
                            for obstacle in obstacles[1:]:
                                file.write(
                                    f"\n{obstacle.position[0]},{obstacle.position[1]},{obstacle.width},{obstacle.height},{int(obstacle.is_platform)}")
                        print("Level saved")
                    else:  # target not drawn
                        print("Add a goal to save the level")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 or event.button == 3:
                    rect_origin = np.array(pygame.mouse.get_pos())
                    mouse_hold = True


            elif event.type == pygame.MOUSEBUTTONUP:
                if rect_origin is not None:
                    rect_params = np.array(pygame.mouse.get_pos()) - rect_origin

                    if not obstacles:
                        obstacles.append(Obstacle(rect_origin, radius, radius, goal=True))
                        obstacles[0].colour = (255, 255, 255)
                        min_width = min(obstacles[0].width, obstacles[0].height)
                        obstacles[0].width = min_width
                        obstacles[0].height = min_width

                    else:
                        platform = True if event.button == 3 else False

                        obstacles.append(Obstacle(np.array([rect_x, rect_y]), abs(rect_params[0]), abs(rect_params[1]),
                                                  is_platform=platform))

                    rect_origin = None
                    rect_params = None
                    mouse_hold = False

            if mouse_hold:
                rect_params = np.array(pygame.mouse.get_pos()) - rect_origin
        text = font.render("Level Designer", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        pygame.display.update()
        clock.tick(frame_rate)


def run(level_no, air_resistance=False):
    pygame.init()
    screen_width, screen_height = pygame.display.Info().current_w, pygame.display.Info().current_h
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Projectile Motion Simulation")
    background = pygame.image.load("./Simulations/SimulationFiles/Assets/images/background1.jpg")
    background = pygame.transform.scale(background, (screen_width, screen_height))
    rows, columns = 18, 32

    container = Container(rows, columns, level_no, air_resistance)
    frame_rate = container.frame_rate

    container.particles.extend([ProjectileParticle(1, 15, container) for _ in range(6)])  # eccentricity
    for particle in container.particles:
        particle.position = np.array([randint(140, 210), randint(780, 980)])
    font = pygame.font.SysFont("comicsans", 20)
    font_30 = pygame.font.SysFont("comicsans", 30)

    clock = pygame.time.Clock()

    while True:
        screen.fill((70, 69, 5))
        screen.blit(background, (0, 0))

        # output score to screen
        text = font.render("Score: " + str(container.score), True, (255, 255, 255))
        screen.blit(text, (10, 10))

        for index, particle in enumerate(container.particles):

            particle.update(screen)

            if container.air_resistance:
                particle.apply_air_resistance()

        # pygame.draw.circle(screen, (169, 130, 85), container.goal.position, container.goal.radius)
        container.goal.draw(screen)

        for particle in container.particles:
            if particle.collision_event_obstacles() and container.moving_particle is particle:
                container.initial_time = None

            particle.collision_event()
            particle.collision_event_goal()
            particle.draw(screen)

            # pygame.draw.circle(screen, (123, 12, 90), collide_x, self.radius)

        for obstacle in container.obstacles:
            obstacle.draw(screen)
        container.draw_splatters(screen)

        # kinematic info
        container.update_kinematic_info()
        container.draw_kinematic_info(screen)
        #
        completed = set()
        for ball_i, ball_j in container.colliding_balls_pairs:  # loop over all collision
            completed.add(ball_i)
            if ball_j not in completed:  # ensure that the particle in question hasn't already been resolved
                ball_i.resolve_dynamic_collision(ball_j)
        container.colliding_balls_pairs.clear()  # reset the list for the next time step

        if container.draw_line_to_mouse and container.selected_particle is not None:
            particle = container.particles[container.selected_particle]
            pygame.draw.line(screen, (255, 0, 0), particle.position, pygame.mouse.get_pos(), width=4)
            pygame.mouse.set_cursor(pygame.cursors.broken_x)
            projected_velocity = (np.array(
                pygame.mouse.get_pos()) - particle.position) * container.projected_particle_velocity_multiplier
            if container.toggle_velocity_display:
                display_params = f"{int(projected_velocity[0])}i\u0302 + {int(-projected_velocity[1])}j\u0302"
            else:
                display_params = f"{container.get_magnitude(projected_velocity).astype(int)} m/s | \u03B1 = {int(np.arctan2(projected_velocity[1], projected_velocity[0]) * -180 / np.pi)}\u00B0"
            text = font.render(display_params, True, (255, 255, 255))
            screen.blit(text, particle.get_position() - np.array([80, 80]))

        else:
            container.draw_line_to_mouse = False

        mouse_pos = pygame.mouse.get_pos()
        coordinates = np.array([mouse_pos[0], screen_height - mouse_pos[1]])
        text = font_30.render(f"({int(coordinates[0])}, {int(coordinates[1])})", True, (255, 255, 255))
        screen.blit(text, (screen_width - 180, 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    pygame.quit()
                    return container.score
                elif event.key == pygame.K_v:
                    container.toggle_velocity_display = not container.toggle_velocity_display
                elif event.key == pygame.K_t:
                    container.show_kinematic_info = not container.show_kinematic_info

            if event.type == pygame.MOUSEBUTTONDOWN:
                particle_clicked = container.selected_particle
                if event.button == 1:
                    container.show_coordinates = not container.show_coordinates
                    if particle_clicked is None:
                        container.drag_particle(event.pos)

                elif event.button == 3 and particle_clicked is None:
                    container.project_particle(event.pos)


            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and container.selected_particle is not None:
                    container.drop_particle()
                    pygame.mouse.set_cursor(pygame.cursors.Cursor())

                elif event.button == 3 and container.selected_particle is not None:
                    particle = container.particles[container.selected_particle]
                    container.release_projected_particle(event.pos)
                    pygame.mouse.set_cursor(pygame.cursors.Cursor())
                    container.start_timer(particle)

            if container.selected_particle is not None and not container.draw_line_to_mouse:
                container.move_selected_particle(event.pos)

        pygame.display.update()

        clock.tick(frame_rate)


#
class ProjectileParticle(Particle):
    def __init__(self, mass, particle_radius, container):
        super().__init__(mass, particle_radius, container)

        self.acceleration = np.array([0, self.container.g])
        self.colour = (184, 146, 255)
        self.hit_goal = False
        self.damping = 0.8

    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, self.position, self.radius)

    def px_to_metres(self, pixel_val):
        return pixel_val / self.container.px_to_metres_factor

    def get_real_acceleration(self):
        return self.px_to_metres(self.acceleration)

    def get_real_velocity(self):
        return self.px_to_metres(self.velocity)

    def get_real_distance(self, val):
        return self.px_to_metres(val)

    def collision_event_goal(self):
        goal = self.container.goal
        if self.entirely_in_obstacle_check2(goal.position, goal.width):
            self.container.initial_time = None
            self.velocity = self.velocity * (1 - self.container.penetration_factor)
            self.acceleration *= 0
            self.hit_goal = True
            if np.allclose(self.velocity, np.zeros_like(self.velocity), atol=2):
                self.container.selected_particle = None

                self.container.calculate_points(self)
                print(self.container.score)
                self.container.particles.remove(self)
                self.container.splattered_particles.append(self)

        else:
            self.hit_goal = False
            self.acceleration = np.array([0, self.container.g])

    def entirely_in_obstacle_check2(self, pos, radius):  # circle
        square_distance = self.container.get_square_magnitude(pos - self.position)
        if square_distance < radius ** 2:
            return True
        return False

    def update(self, screen):

        self.next_position = self.position + self.velocity * self.container.dt
        if self.next_position[0] > screen.get_width() - self.radius or self.next_position[
            0] < self.radius:  # or within blocked cell
            self.velocity[0] *= -1 * self.container.damping

        if self.next_position[1] > screen.get_height() - self.radius or self.next_position[1] < self.radius:
            self.velocity[1] *= -1 * self.container.damping
            self.velocity[0] *= 0.99  # want to add a bit of energy loss. pretty much the coefficient of restitution

        self.next_position = np.clip(self.next_position, (self.radius, self.radius),
                                     (screen.get_width() - self.radius, screen.get_height() - self.radius))

        self.position = self.next_position

        # print(self.container.grid)
        if self.container.particles.index(self) != self.container.selected_particle:
            self.velocity = self.velocity + self.acceleration


class Container(SpatialMap):
    def __init__(self, rows, columns, level_no, air_resistance):
        screen_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        super().__init__(rows, columns, screen_size=screen_size)
        self.projected_particle_velocity_multiplier = 5
        self.damping = 0.75

        self.draw_line_to_mouse = False
        self.colliding_balls_pairs = []

        self.drag_coefficient = 0.000000001

        self.air_resistance = air_resistance
        self.px_to_metres_factor = 2
        self.penetration_factor = 0.15
        self.toggle_velocity_display = False
        self.show_coordinates = False

        self.score = 0
        self.goal = None

        self.obstacles = []

        self.g = 9.8
        self.moving_particle = None
        self.current_time = 0
        self.initial_time = None
        self.initial_velocity = 0
        self.initial_angle = 0
        self.final_velocity = 0
        self.final_angle = 0
        self.initial_position = np.zeros(2)
        self.current_position = np.zeros(2)
        self.show_kinematic_info = True

        if not self.initialise_level("./Simulations/SimulationFiles/Assets/ProjectileLevels/lvl" + str(level_no)):
            self.obstacles = []
            self.initialise_level("./Simulations/SimulationFiles/Assets/ProjectileLevels/lvl1")  # load level one
        else:
            print("Level loaded successfully")

    def start_timer(self, particle):
        self.stop_timer()
        self.initial_time = time.time()
        self.moving_particle = particle
        self.initial_position = particle.position
        self.initial_velocity = self.get_magnitude(particle.velocity)
        self.initial_angle = np.arctan2(particle.velocity[1], particle.velocity[0]) * -180 / np.pi
        self.current_position = particle.position

    def stop_timer(self):
        self.initial_time = None

    def update_kinematic_info(self):
        if self.initial_time is not None:
            self.current_time = time.time() - self.initial_time
            self.final_velocity = self.get_magnitude(self.moving_particle.velocity)
            self.final_angle = np.arctan2(self.moving_particle.velocity[1],
                                          self.moving_particle.velocity[0]) * -180 / np.pi
            self.current_position = self.moving_particle.position

    def draw_kinematic_info(self, screen):
        if self.show_kinematic_info:
            pygame.draw.rect(screen, (230, 230, 230, 127), (1620, 65, 300, 330))
            font = pygame.font.SysFont("Arial", 25)
            labels = ["Initial Speed",
                      "Vertical Displacement",
                      "Horizontal Displacement",
                      "Current Speed",
                      "Time"]
            values = [
                f"{round(self.initial_velocity):>8} m/s at {round(self.initial_angle):>3}\u00B0",
                f"{round(self.initial_position[1] - self.current_position[1]):>8} m",
                f"{round(self.current_position[0] - self.initial_position[0]):>8} m",
                f"{round(self.final_velocity):>8} m/s at {round(self.final_angle):>3}\u00B0",
                f"{self.current_time:>10.2f} seconds"]
            for index, text in enumerate(zip(labels, values)):
                screen.blit(font.render(text[0], True, (50, 50, 50)), (1640, 20 + 60 * (index + 1)))
                screen.blit(font.render(text[1], True, (50, 50, 50)), (1640, 45 + 60 * (index + 1)))

    def add_points(self, points):
        self.score += points

    def calculate_points(self, particle):
        multiplier = abs((self.get_magnitude(self.goal.position - particle.position) / self.goal.width))
        points = int(100 * (1 - multiplier ** 2))
        self.add_points(points)

    def draw_splatters(self, screen):
        length = len(self.collision_splatters)
        for index, particle in enumerate(self.splattered_particles):
            splat = self.collision_splatters[index % length]
            screen.blit(splat, particle.position - (splat.get_width() // 2, splat.get_height() // 2))

    def initialise_level(self, file_name):
        goal_background_image = pygame.image.load("./Simulations/SimulationFiles/Assets/images/images.jpg")
        ball_box_image = None
        goal_background_image.convert_alpha()

        # creating ball box
        box_dimensions = [
            ((100, 1055), 150, 25),
            ((100, 970), 25, 110),
            ((225, 970), 25, 110)]
        for row in box_dimensions:
            plank = Obstacle(*row, ball_box_image)
            plank.is_platform = True
            plank.colour = (248, 94, 0)
            self.obstacles.append(plank)

        splatters = ["splat1.png", "splat2.png", "splat3.png"]
        splat_width = 100
        self.collision_splatters = []
        self.splattered_particles = []
        for splat in splatters:
            img = pygame.image.load("./Simulations/SimulationFiles/Assets/images/" + splat)
            img.convert_alpha()
            img = pygame.transform.scale(img, (splat_width, splat_width * img.get_height() // img.get_width()))
            self.collision_splatters.append(img)

        bounce_image = pygame.image.load("./Simulations/SimulationFiles/Assets/images/wall.jpg")
        wall_image = pygame.image.load("./Simulations/SimulationFiles/Assets/images/bouncy_wall.jpg")
        try:  # parsing level
            with open(file_name, "r") as file:
                self.penetration_factor = float(file.readline())
                goal = file.readline()
                self.initialise_goal(goal.split(","))  # handling goal separately
                for line in file:
                    line = line.split(",")
                    image = bounce_image if int(line[4]) else wall_image
                    new_obstacle = Obstacle((int(line[0]), int(line[1])), int(line[2]), int(line[3]), image,
                                            is_platform=int(line[4]))
                    self.obstacles.append(new_obstacle)

            return True

        except FileNotFoundError:
            print("File not found")
            print(file_name)
            return False  # and run level 1

        except Exception as e:
            print(e)
            return False

    def initialise_goal(self, goal):
        image = pygame.image.load("./Simulations/SimulationFiles/Assets/images/target.png")
        print(goal)
        image = pygame.transform.scale(image, (2 * int(goal[2]), 2 * int(goal[2])))
        self.goal = Obstacle((int(goal[0]), int(goal[1])), int(goal[2]), int(goal[2]), image, goal=True)
        # self.goal.position = np.array([int(goal[1]), int(goal[2])])
        self.goal.colour = (255, 105, 180)  # pink color

    def real_velocity(self):

        pass


class Obstacle:
    def __init__(self, position, width, height, image=None, goal=False, is_platform=False):
        self.position = np.array(position)
        self.width, self.height = width, height
        self.colour = (255, 0, 0) if not is_platform else (90, 255, 43)
        self.goal = goal
        self.is_platform = is_platform
        self.image = image
        if image is not None and not goal:
            self.image = image.subsurface(pygame.Rect(0, 0, self.width, self.height))

    def draw(self, screen):

        if self.image:
            if self.goal:
                screen.blit(self.image, self.position - self.width)
            else:
                screen.blit(self.image, self.position)
        elif self.goal:
            pygame.draw.circle(screen, self.colour, self.position, self.width)
        else:
            pygame.draw.rect(screen, self.colour, (self.position[0], self.position[1], self.width, self.height))


if __name__ == "__main__":
    run(2)
