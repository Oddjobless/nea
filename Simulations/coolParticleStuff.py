import pygame
from baseClasses import *
# ported from projectile sim. could make a ideal gas sim, with adjustable volume and more particles and higher temperature



def run():
    pygame.init()

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = Container(rows, columns)

    vector_field.particles.extend([ProjectileParticle(1, 20, vector_field, _wall_damping=1.00, floor_damping=1.00) for _ in range(100)])  # eccentricity
    font = pygame.font.SysFont("comicsans", int(box_width // 2.6))
    temp_slider = pygame
    frame = 0
    mouse_rel_refresh = frame_rate * 0.5


    clock = pygame.time.Clock()
    while True:




        screen.fill((70, 69, 5))


        # draw gas container walls
        vector_field.draw_walls(screen)

        for index, particle in enumerate(vector_field.particles):
            particle.update(screen, custom_dimensions=vector_field.dimensions, vector_field=False)
            if vector_field.air_resistance:
                print("oh no")
                particle.apply_air_resistance()

        for particle in vector_field.particles:
            particle.collision_event()

            pygame.draw.circle(screen, (123, 12, 90), particle.position, particle.radius)
            # pygame.draw.circle(screen, (123, 12, 90), collide_x, self.radius)


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
                elif event.button == 1 and vector_field.selected_particle == None:
                    vector_field.drag_particle(event.pos)

                elif event.button == 3 and vector_field.selected_particle == None:
                    vector_field.project_particle(event.pos)




            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3 and vector_field.wall_selected != None:
                    vector_field.wall_selected = None


                if event.button == 1 and vector_field.selected_particle != None:
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
class ProjectileParticle(Particle):
    def __init__(self, mass, particle_radius, vector_field, _wall_damping, floor_damping):
        super().__init__(mass, particle_radius, vector_field, _wall_damping)
        g = 0
        self.acceleration = np.array([0, g])
        self.floor_damping = floor_damping
        self.T_slider = [1000,1000, 400, 20, 100]

    def draw_slider(self):


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
        self.projected_particle_velocity_multiplier = 80
        self.dimensions = np.array([200,200,900,600]) # left, top, right, bottom

        self.draw_line_to_mouse = False
        self.colliding_balls_pairs = []
        self.wall_selected = None
        self.wall_radius = 20

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
