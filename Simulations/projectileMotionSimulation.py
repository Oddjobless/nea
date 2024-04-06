import numpy as np
import pygame.draw
import time
from Simulations.SimulationFiles.baseClasses import *




def draw_mode(level_no):

    pygame.init()
    file_name = "lvlTest"
    screen_width, screen_height = 1920, 1080
    screen = pygame.display.set_mode((screen_width, screen_height))
    obstacles = []
    level_name = ""
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
                pygame.draw.circle(screen, (255,255,255), rect_origin, radius)

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
                    if obstacles: # checks if the user has added a goal
                        with open(("./Simulations/SimulationFiles/Assets/ProjectileLevels/lvl" + str(level_no)), "w") as file:
                            file.write(f"{obstacles[0].position[0]},{obstacles[0].position[1]},{obstacles[0].width},{obstacles[0].height}")
                            for obstacle in obstacles[1:]:
                                file.write(f"\n{obstacle.position[0]},{obstacle.position[1]},{obstacle.width},{obstacle.height},{int(obstacle.is_platform)}")
                        print("Level saved")
                    else: # target not drawn
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
                        obstacles[0].colour = (255,255,255)
                        min_width = min(obstacles[0].width, obstacles[0].height)
                        obstacles[0].width = min_width
                        obstacles[0].height = min_width

                    else:
                        obstacles.append(Obstacle(np.array([rect_x, rect_y]), abs(rect_params[0]), abs(rect_params[1])))
                        if event.button == 3:
                            obstacles[-1].is_platform = True
                            obstacles[-1].colour = (90, 255, 43)


                    rect_origin = None
                    rect_params = None
                    mouse_hold = False

            if mouse_hold:
                rect_params = np.array(pygame.mouse.get_pos()) - rect_origin

        pygame.display.update()
        clock.tick(frame_rate)












def run(level_no, air_resistance=False):

    pygame.init()
    screen_width, screen_height = 1920, 1080
    display_width, display_height = 1920, 1000
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Projectile Motion Simulation")
    background = pygame.image.load("./Simulations/SimulationFiles/Assets/images/background1.jpg")
    background = pygame.transform.scale(background, (screen_width, screen_height))
    rows, columns = 18, 32

    vector_field = Container(rows, columns, level_no, air_resistance)

    vector_field.particles.extend([ProjectileParticle(1, 15, vector_field, wall_damping, floor_damping=0.7) for _ in range(6)])  # eccentricity
    for particle in vector_field.particles:
        particle.position = np.array([randint(140,210), randint(780,980)])
    font = pygame.font.SysFont("comicsans", 20)
    font_30 = pygame.font.SysFont("comicsans", 30)

    clock = pygame.time.Clock()

    while True:
        screen.fill((70, 69, 5))
        screen.blit(background, (0, 0))

        # output score to screen
        text = font.render("Score: " + str(vector_field.score), True, (255, 255, 255))
        screen.blit(text, (10, 10))


        for index, particle in enumerate(vector_field.particles):

            particle.update(screen)

            if vector_field.air_resistance:
                particle.apply_air_resistance()

        # pygame.draw.circle(screen, (169, 130, 85), vector_field.goal.position, vector_field.goal.radius)
        vector_field.goal.draw(screen)

        for particle in vector_field.particles:
            if particle.collision_event_obstacles() and vector_field.moving_particle is particle:
                vector_field.initial_time = None

            particle.collision_event()
            particle.collision_event_goal(screen)
            particle.draw(screen)


            # pygame.draw.circle(screen, (123, 12, 90), collide_x, self.radius)


        for obstacle in vector_field.obstacles:
            obstacle.draw(screen)
        vector_field.draw_splatters(screen)
        
        # kinematic info
        vector_field.update_kinematic_info()
        vector_field.draw_kinematic_info(screen)
        # 
        completed = set()
        for ball_i, ball_j in vector_field.colliding_balls_pairs: # loop over all collision
            completed.add(ball_i)
            if ball_j not in completed: # ensure that the particle in question hasn't already been resolved
                ball_i.resolve_dynamic_collision(ball_j)
                pygame.draw.line(screen, (0, 255, 0), ball_i.position, ball_j.position)
        vector_field.colliding_balls_pairs.clear() # reset the list for the next time step

        if vector_field.draw_line_to_mouse and vector_field.selected_particle != None:
            particle = vector_field.particles[vector_field.selected_particle]
            pygame.draw.line(screen, (255, 0, 0), particle.position, pygame.mouse.get_pos())
            projected_velocity = (np.array(pygame.mouse.get_pos()) - particle.position) * vector_field.projected_particle_velocity_multiplier
            if vector_field.toggle_velocity_display:
                display_params = f"{int(projected_velocity[0])}i\u0302 + {int(-projected_velocity[1])}j\u0302"
            else:
                display_params = f"{vector_field.get_magnitude(projected_velocity).astype(int)} m/s | \u03B1 = {int(np.arctan2(projected_velocity[1], projected_velocity[0]) * -180 / np.pi)}\u00B0"
            text = font.render(display_params, True, (255, 255, 255))
            screen.blit(text, particle.get_position() - np.array([80, 80]))

        else:
            vector_field.draw_line_to_mouse = False

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
                    return vector_field.score
                elif event.key == pygame.K_v:
                    vector_field.toggle_velocity_display = not vector_field.toggle_velocity_display
                elif event.key == pygame.K_t:
                    vector_field.show_kinematic_info = not vector_field.show_kinematic_info

            if event.type == pygame.MOUSEBUTTONDOWN:
                particle_clicked = vector_field.selected_particle
                if event.button == 1:
                    vector_field.show_coordinates = not vector_field.show_coordinates
                    if particle_clicked == None:
                        vector_field.drag_particle(event.pos)

                elif event.button == 3 and particle_clicked == None:
                    vector_field.project_particle(event.pos)


            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and vector_field.selected_particle != None:
                    vector_field.drop_particle()

                elif event.button == 3 and vector_field.selected_particle != None:
                    particle = vector_field.particles[vector_field.selected_particle]
                    vector_field.release_projected_particle(event.pos)
                    vector_field.start_timer(particle)


            if vector_field.selected_particle != None and not vector_field.draw_line_to_mouse:
                vector_field.move_selected_particle(event.pos)



        pygame.display.update()

        clock.tick(frame_rate)


#
class ProjectileParticle(Particle):
    def __init__(self, mass, particle_radius, vector_field, _wall_damping, floor_damping):
        super().__init__(mass, particle_radius, vector_field, _wall_damping)

        self.acceleration = np.array([0, self.vector_field.g])
        self.floor_damping = floor_damping
        self.colour = (168,132,35)
        self.hit_goal = False
    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, self.position, self.radius)

    def kinematics(self):
        pass
        # vel = [3,3]
        # so we move 12 pixels right every tick. f = 60, so 1 * 60 pixels per second = 180 px / sec
        # distance in pixels, lets say 720 pixels
        # acceleration downwards should be 9.8 m/s^2. so if i use 2 px/s^, it's a conversion to 9.8:

    def px_to_metres(self, pixel_val):
        return pixel_val / self.vector_field.px_to_metres_factor

    def get_real_acceleration(self):
        return self.px_to_metres(self.acceleration)

    def get_real_velocity(self):
        return self.px_to_metres(self.velocity)
    """
    centre login
    have all of it one page
    simulation in each corner
    """
    def get_real_distance(self, val):
        return self.px_to_metres(val)



    def collision_event_goal(self, screen):
        goal = self.vector_field.goal
        if self.entirely_in_obstacle_check2(goal.position, goal.width):
            self.vector_field.initial_time = None
            self.velocity = self.velocity * (1 - self.vector_field.penetration_factor)
            self.acceleration *= 0
            self.hit_goal = True
            self.colour = (25,125,195)
            if np.allclose(self.velocity, np.zeros_like(self.velocity), atol=2):
                self.vector_field.selected_particle = None
                try:
                    self.vector_field.calculate_points(self)
                    print(self.vector_field.score)
                    self.vector_field.particles.remove(self)
                    self.vector_field.splattered_particles.append(self)
                except:
                    return
        else:
            self.hit_goal = False
            self.acceleration = np.array([0, self.vector_field.g])

    def entirely_in_obstacle_check2(self, pos, radius): # circle
        square_distance = self.vector_field.get_square_magnitude(pos - self.position)
        if square_distance < radius ** 2:
            return True
        return False




    def update(self, screen):

        self.next_position = self.position + self.velocity * dt
        if self.next_position[0] > screen.get_width() - (self.radius) or self.next_position[
            0] < self.radius:  # or within blocked cell
            self.velocity[0] *= -1 * self.damping

        if self.next_position[1] > screen.get_height() - self.radius or self.next_position[1] < self.radius:
            self.velocity[1] *= -1 * self.floor_damping
            self.velocity[0] *= 0.99  # friction to slow if on ground

        self.next_position = np.clip(self.next_position, (self.radius, self.radius),
                                     (screen.get_width() - self.radius, screen.get_height() - self.radius))

        self.position = self.next_position


        # print(self.vector_field.grid)
        if self.vector_field.particles.index(self) != self.vector_field.selected_particle:
            self.velocity = self.velocity + self.acceleration












class Obstacle:
    def __init__(self, position, width, height, image=None, goal=False):
        self.position = np.array(position)
        self.width, self.height = width, height
        self.colour = (255, 0, 0)
        self.is_platform = False
        self.image = pygame.transform.scale(image, (width, height)) if image and not goal else None
        # self.image = image.subsurface(pygame.Rect(0, 0, self.width, self.height)) if image else None
        self.goal = goal

    def draw(self, screen):

        if self.image:
            if self.goal:
                pygame.draw.circle(screen, self.colour, self.position, self.width)
                screen.blit(self.image, self.position - self.width // 2)

            else:
                screen.blit(self.image, self.position)
        elif self.goal:
            pygame.draw.circle(screen, self.colour, self.position, self.width)
        else:
            pygame.draw.rect(screen, self.colour, (self.position[0], self.position[1], self.width, self.height))


class Container(SpatialMap):
    def __init__(self, rows, columns, level_no, air_resistance):
        super().__init__(rows, columns)
        self.particles = []
        self.selected_particle = None
        self.projected_particle_velocity_multiplier = 4

        self.draw_line_to_mouse = False
        self.colliding_balls_pairs = []


        self.drag_coefficient = 0.000000001

        
        self.air_resistance = air_resistance
        self.px_to_metres_factor = 2
        self.penetration_factor = 0.1
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
            self.initialise_level("./Simulations/SimulationFiles/Assets/ProjectileLevels/lvl1") #load level one
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
            self.final_angle = np.arctan2(self.moving_particle.velocity[1], self.moving_particle.velocity[0]) * -180 / np.pi
            self.current_position = self.moving_particle.position
        
        
        
    def draw_kinematic_info(self, screen):
        if self.show_kinematic_info:
            pygame.draw.rect(screen, (230,230,230,127), (1620, 65, 300, 330))
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
                screen.blit(font.render(text[0], True, (50,50,50)), (1640, 20 + 60 * (index + 1)))
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
            ((100,1055),150,25),
            ((100,970),25,110),
            ((225,970),25,110)]
        for row in box_dimensions:
            plank = Obstacle(*row, ball_box_image)
            plank.is_platform = True
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

        wall_image = pygame.image.load("./Simulations/SimulationFiles/Assets/images/wall.png")
        try: # parsing level
            with open(file_name, "r") as file:
                goal = file.readline()
                self.initialise_goal(goal.split(",")) # handling goal separately
                for line in file:
                    line = line.split(",")
                    object = Obstacle((int(line[0]), int(line[1])), int(line[2]), int(line[3]), wall_image)
                    self.obstacles.append(object)
                    if int(line[4]):
                        object.is_platform = True
                        object.colour = (37,41,74) # temporary
            return True

        except FileNotFoundError:
            print("File not found")
            print(file_name)
            return False # and run level 1

        except Exception as e:
            print(e)
            return False

    def initialise_goal(self, goal):
        image = pygame.image.load("./Simulations/SimulationFiles/Assets/images/target.png")
        print(goal)
        image = pygame.transform.scale(image, (2 * int(goal[2]), 2 * int(goal[2])))
        self.goal = Obstacle((int(goal[0]), int(goal[1])),int(goal[2]), int(goal[2]), image, goal=True)
        # self.goal.position = np.array([int(goal[1]), int(goal[2])])
        self.goal.colour = (255,105,180) # pink color







    def real_velocity(self):

        pass




if __name__ == "__main__":
    run(2)
