import pygame
from baseClasses import *

pygame.init()


def run():
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = Container(rows, columns)

    vector_field.particles.extend([ProjectileParticle(1, 60, vector_field, wall_damping, floor_damping=0.75) for _ in range(2)])  # eccentricity
    font = pygame.font.SysFont("comicsans", int(box_width // 2.6))
    frame = 0
    mouse_rel_refresh = frame_rate * 0.5

    while True:



        ### drawing vectorField
        screen.fill((70, 69, 5))

        # logic goes here

        for index, particle in enumerate(vector_field.particles):
            if index != vector_field.selected_particle:
                particle.update(screen)

        for particle in vector_field.particles:
            pygame.draw.circle(screen, (123, 12, 90), particle.position, particle.radius)
            # pygame.draw.circle(screen, (123, 12, 90), collide_x, self.radius)

        if vector_field.draw_line_to_mouse:
            pygame.draw.line(screen, (255, 0, 0), vector_field.particles[vector_field.selected_particle].position, pygame.mouse.get_pos())

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

                if event.button == 3 and vector_field.selected_particle != None:
                    vector_field.release_projected_particle(event.pos)

            if vector_field.selected_particle != None and not vector_field.draw_line_to_mouse:
                vector_field.move_selected_particle(event.pos)



        pygame.display.update()

        clock.tick(frame_rate)


#
class ProjectileParticle(Particle):
    def __init__(self, mass, particle_radius, vector_field, _wall_damping, floor_damping):
        super().__init__(mass, particle_radius, vector_field, _wall_damping)
        self.acceleration = np.array([0, 9.8])
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
        self.velocity = self.velocity + self.acceleration * self.mass


    def is_collision(self, next_particle):
        distance = self.vector_field.get_square_magnitude(next_particle.next_position - self.next_position)
        if self != next_particle:
            if 0 < distance <= (self.radius + next_particle.radius)**2:
                return True
        return False

    def resolve_static_collision(self, next_particle):
        distance = self.vector_field.get_magnitude(next_particle.next_position - self.next_position)
        overlap = 0.5 * (distance - self.radius + next_particle.radius)

        self.next_position -= overlap * (self.next_position - next_particle.next_position) / distance

        next_particle.next_position += overlap * (self.next_position - next_particle.next_position) / distance


class Container(SpatialMap):
    def __init__(self, rows, columns):
        super().__init__(rows, columns)
        self.particles = []
        self.selected_particle = None
        self.projected_particle_velocity_vector = 4

        self.draw_line_to_mouse = False

    def drag_particle(self, mouse_pos):
        for index, particle in enumerate(self.particles):
            if not particle.radius < mouse_pos[0] < screen_width - particle.radius and particle.radius < mouse_pos[1] < screen_height - particle.radius:
                continue
            distance = particle.vector_field.get_magnitude(np.array(mouse_pos) - particle.position)
            if distance < particle.radius:
                particle.velocity = particle.velocity * 0
                self.selected_particle = index
                print(index)
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
        particle.velocity = (particle.position - mouse_pos) * self.projected_particle_velocity_vector
        self.draw_line_to_mouse = False
        self.selected_particle = None

if __name__ == "__main__":
    print("piss")
    run()
