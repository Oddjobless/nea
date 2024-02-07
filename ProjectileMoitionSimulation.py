import pygame
from baseClasses import *

pygame.init()


def draw_mode():
    screen = pygame.display.set_mode((1920,1080))
    obstacles = []
    level_name = ""
    while True:
        screen.fill((169, 130, 40))

        for obstacle in obstacles:
            obstacle.draw(screen)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return


            if event.type == pygame.MOUSEBUTTONDOWN:
                pass


            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    pass

                elif event.button == 3:
                    pass



def run():
    screen_width, screen_height = 1920, 1080
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = Container(rows, columns)

    vector_field.particles.extend([ProjectileParticle(1, 15, vector_field, wall_damping, floor_damping=0.7) for _ in range(6)])  # eccentricity
    font = pygame.font.SysFont("comicsans", 20)
    frame = 0
    mouse_rel_refresh = frame_rate * 0.5

# force
    while True:



        ### drawing vectorField
        screen.fill((70, 69, 5))

        # logic goes here

        for index, particle in enumerate(vector_field.particles):

            particle.update(screen)

            if vector_field.air_resistance:
                particle.apply_air_resistance()

        # pygame.draw.circle(screen, (169, 130, 85), vector_field.goal.position, vector_field.goal.radius)
        vector_field.goal.draw(screen)

        for particle in vector_field.particles:
            particle.collision_event_obstacles()
            particle.collision_event()
            particle.collision_event_goal()


            particle.draw(screen)
            # pygame.draw.circle(screen, (123, 12, 90), collide_x, self.radius)
            text = font.render(f"{particle.get_real_velocity()[1]:1f}, {(particle.get_position()[0] * vector_field.g_multiplier):1f}", True, (255, 255, 255))
            screen.blit(text, particle.get_position() - np.array([0, 80]))

        for obstacle in vector_field.obstacles:
            obstacle.draw(screen)

        completed = set()
        for ball_i, ball_j in vector_field.colliding_balls_pairs:
            completed.add(ball_i)
            if ball_j not in completed:
                # print("Ball", ball_i, "collides with", ball_j)
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


            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and vector_field.selected_particle == None:
                    vector_field.drag_particle(event.pos)
                    print("adf")

                elif event.button == 3 and vector_field.selected_particle == None:
                    vector_field.project_particle(event.pos)




            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and vector_field.selected_particle != None:
                    vector_field.drop_particle()

                elif event.button == 3 and vector_field.selected_particle != None:
                    vector_field.release_projected_particle(event.pos)

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
        self.colour = (43,132,154)
    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, self.position, self.radius)

    def kinematics(self):
        pass
        # vel = [3,3]
        # so we move 12 pixels right every tick. f = 60, so 1 * 60 pixels per second = 180 px / sec
        # distance in pixels, lets say 720 pixels
        # acceleration downwards should be 9.8 m/s^2. so if i use 2 px/s^, it's a conversion to 9.8:

    def px_to_metres(self, pixel_val):
        return self.vector_field.g_multiplier * pixel_val

    def get_real_acceleration(self):
        return self.px_to_metres(self.acceleration)

    def get_real_velocity(self, ):
        return self.px_to_metres(self.velocity)

    def get_real_distance(self, val):
        return self.px_to_metres(val)

    def collision_event_obstacles(self):
        for obstacle in self.vector_field.obstacles:
            if self.check_obstacle_collision(obstacle):

                return self.resolve_obstacle_collision(obstacle)

    def resolve_obstacle_collision(self, obstacle):
        # Calculate the displacement vector from the rectangle to the circle
        displacement = self.next_position - np.array([max(obstacle.position[0], min(self.next_position[0], obstacle.position[0] + obstacle.width)),
                                                      max(obstacle.position[1], min(self.next_position[1], obstacle.position[1] + obstacle.height))])

        # Calculate the penetration depth for both x and y directions
        penetration_x = max(0, self.radius - abs(displacement[0]))
        penetration_y = max(0, self.radius - abs(displacement[1]))

        # Determine the direction of displacement
        direction_x = 1 if displacement[0] > 0 else -1
        direction_y = 1 if displacement[1] > 0 else -1


        if obstacle.is_platform:
            damping = 0.1
        else:
            damping = self.damping


        if penetration_x < penetration_y:
            # Collided in x-direction
            self.next_position[0] += penetration_x * direction_x
            self.velocity[0] *= -1 * damping
            if obstacle.is_platform:
                self.velocity[1] *= -1 * damping
        else:
            # Collided in y-direction
            self.next_position[1] += penetration_y * direction_y
            self.velocity[1] *= -1 * damping
            if obstacle.is_platform:
                self.velocity[0] *= -1 * damping

    def check_obstacle_collision(self, obstacle, custom_radius=None):
        # Calculate the closest point on the rectangle to the circle
        closest_x = max(obstacle.position[0], min(self.next_position[0], obstacle.position[0] + obstacle.width))
        closest_y = max(obstacle.position[1], min(self.next_position[1], obstacle.position[1] + obstacle.height))

        # Calculate the distance between the circle's center and the closest point on the rectangle
        distance = np.sqrt((self.next_position[0] - closest_x) ** 2 + (self.next_position[1] - closest_y) ** 2)

        # Check if the distance is less than the circle's radius
        if not custom_radius:
            return distance < self.radius
        print(distance, self.radius)
        return distance < custom_radius

    def collision_event_goal(self):
        goal = self.vector_field.goal
        if self.check_obstacle_collision(goal, custom_radius=0.01):
            self.velocity *= 0
            self.colour = (255,255,255)
            # self.acceleration *= 0


    def update(self, screen):

        self.next_position = self.position + self.velocity * dt
        if self.next_position[0] > screen.get_width() - (self.radius) or self.next_position[
            0] < self.radius:  # or within blocked cell
            self.velocity[0] *= -1 * self.damping
        if self.next_position[1] > screen.get_height() - self.radius or self.next_position[1] < self.radius:
            self.velocity[1] *= -1 * self.floor_damping

        self.next_position = np.clip(self.next_position, (self.radius, self.radius),
                                     (screen.get_width() - self.radius, screen.get_height() - self.radius))

        self.position = self.next_position





        # print(self.vector_field.grid)
        if self.vector_field.particles.index(self) != self.vector_field.selected_particle:
            self.velocity = self.velocity + self.acceleration * self.mass



    def is_collision(self, next_particle):
        distance = self.vector_field.get_square_magnitude(next_particle.next_position - self.next_position)
        if self != next_particle:
            if 0 < distance <= (self.radius + next_particle.radius)**2:
                self.vector_field.colliding_balls_pairs.append((self, next_particle))
                return True
        return False

    def resolve_static_collision(self, next_particle):
        distance = self.vector_field.get_magnitude(next_particle.next_position - self.next_position)

        overlap = 0.5 * (distance - (self.radius + next_particle.radius))
        self.next_position -= overlap * (self.next_position - next_particle.next_position) / distance

        next_particle.next_position += overlap * (self.next_position - next_particle.next_position) / distance

    def collision_event(self):
        for particle in self.vector_field.particles:
            if self.is_collision(particle):
                self.resolve_static_collision(particle)

    def apply_air_resistance(self):
        vel = self.vector_field.get_magnitude(self.velocity)
        vel_normalised = self.vector_field.normalise_vector(self.velocity)
        drag_force = -self.vector_field.drag_coefficient * np.pi * self.radius ** 2 * vel ** 2
        self.velocity += (drag_force * vel_normalised) / self.mass

    def resolve_dynamic_collision(self, next_particle):
        distance = self.vector_field.get_magnitude(next_particle.next_position - self.next_position)
        normal = self.vector_field.normalise_vector(next_particle.next_position - self.next_position)
        tangent = np.array([-normal[1], normal[0]])

        tangential_vel_i = tangent * np.dot(self.velocity, tangent)
        tangential_vel_j = tangent * np.dot(next_particle.velocity, tangent)

        normal_vel_i = normal * ((np.dot(self.velocity, normal) * (self.mass - next_particle.mass) + 2 * next_particle.mass * np.dot(next_particle.velocity, normal)) / (self.mass + next_particle.mass))
        normal_vel_j = normal * ((np.dot(next_particle.velocity, normal) * (next_particle.mass - self.mass) + 2 * self.mass * np.dot(self.velocity, normal)) / (self.mass + next_particle.mass))

        self.velocity = tangential_vel_i + normal_vel_i
        next_particle.velocity = tangential_vel_j + normal_vel_j



class Obstacle:
    def __init__(self, position, width, height):
        self.position = np.array(position)
        self.width, self.height = width, height
        self.colour = (255, 0, 0)
        self.is_platform = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.colour, (self.position[0], self.position[1], self.width, self.height))


class Container(SpatialMap):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)
        self.particles = []
        self.selected_particle = None
        self.projected_particle_velocity_multiplier = 3

        self.draw_line_to_mouse = False
        self.colliding_balls_pairs = []

        self.air_resistance = False
        self.drag_coefficient = 0.000000001

        self.g = 9.8
        self.g_multiplier = 9.8 / self.g

        self.px_to_metres_factor = 4

        self.obstacles = []
        self.initialise_level("ProjectileMotionLevels/lvl2")





    def initialise_level(self, file_name):
        with open(file_name, "r") as file:
            goal = file.readline()
            self.initialise_goal(goal.split(","))
            for line in file:
                line = line.split(",")
                object = Obstacle((int(line[0]), int(line[1])), int(line[2]), int(line[3]))
                self.obstacles.append(object)
                if int(line[4]):
                    object.is_platform = True
                    object.colour = (37,41,74)

    def initialise_goal(self, goal):
        # self.goal = Particle(0, int(goal[0]), self, 0)
        self.goal = Obstacle((int(goal[0]), int(goal[1])),int(goal[2]), int(goal[3]))
        # self.goal.position = np.array([int(goal[1]), int(goal[2])])
        self.goal.colour = (255,105,180) # hot pink color




    def drag_particle(self, mouse_pos):
        for index, particle in enumerate(self.particles):
            if not particle.radius < mouse_pos[0] < screen_width - particle.radius and particle.radius < mouse_pos[1] < screen_height - particle.radius:
                continue
            distance = particle.vector_field.get_magnitude(np.array(mouse_pos) - particle.position)
            if distance < particle.radius:
                particle.velocity = particle.velocity * 0
                self.selected_particle = index
                return
    def drop_particle(self):
        self.particles[self.selected_particle].velocity *= 0
        self.selected_particle = None

    def move_selected_particle(self, mouse_position):
        self.particles[self.selected_particle].position = mouse_position

    def project_particle(self, mouse_pos):
        for index, particle in enumerate(self.particles):
            if not particle.radius < mouse_pos[0] < screen_width - particle.radius and particle.radius < mouse_pos[1] < screen_height - particle.radius:
                continue
            distance = particle.vector_field.get_magnitude(np.array(mouse_pos) - particle.position)
            if distance < particle.radius:
                particle.velocity = particle.velocity * 0
                self.draw_line_to_mouse = True
                self.selected_particle = index
                return

    def release_projected_particle(self, mouse_pos):
        particle = self.particles[self.selected_particle]
        particle.velocity = (particle.position - np.array(mouse_pos)) * self.projected_particle_velocity_multiplier
        self.draw_line_to_mouse = False
        self.selected_particle = None

    def apply_air_resistance(self):
        for particle in self.particles:
            particle.apply_resistance()


if __name__ == "__main__":
    print("piss")
    run()
