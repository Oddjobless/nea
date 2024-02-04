import pygame
from baseClasses import *
# ported from projectile sim. could make a ideal gas sim, with adjustable volume and more particles and higher temperature
pygame.init()


def run():
    screen_width, screen_height = 1920, 1080
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = Container(rows, columns)

    vector_field.particles.extend([ProjectileParticle(1, 30, vector_field, wall_damping, floor_damping=1.00) for _ in range(200)])  # eccentricity
    font = pygame.font.SysFont("comicsans", int(box_width // 2.6))
    frame = 0
    mouse_rel_refresh = frame_rate * 0.5

    while True:



        ### drawing vectorField
        screen.fill((70, 69, 5))

        # logic goes here

        for index, particle in enumerate(vector_field.particles):

            particle.update(screen)
            if vector_field.air_resistance:
                particle.apply_air_resistance()

        for particle in vector_field.particles:
            particle.collision_event()

            pygame.draw.circle(screen, (123, 12, 90), particle.position, particle.radius)
            # pygame.draw.circle(screen, (123, 12, 90), collide_x, self.radius)


        completed = set()
        for ball_i, ball_j in vector_field.colliding_balls_pairs:
            completed.add(ball_i)
            if ball_j not in completed:
                print("Ball", ball_i, "collides with", ball_j)
                ball_i.resolve_dynamic_collision(ball_j)
                pygame.draw.line(screen, (0, 255, 0), ball_i.position, ball_j.position)
        # vector_field.colliding_balls_pairs.clear()

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
        g = 0
        self.acceleration = np.array([0, g])
        self.floor_damping = floor_damping

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


class Container(SpatialMap):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)
        self.particles = []
        self.selected_particle = None
        self.projected_particle_velocity_multiplier = 10

        self.draw_line_to_mouse = False
        self.colliding_balls_pairs = []

        self.air_resistance = False
        self.drag_coefficient = 0.000000001

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
