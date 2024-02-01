import pygame
from baseClasses import *


pygame.init()


def run():
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Pygame Boilerplate")

    vector_field = SpatialMap()

    particles = [ProjectileParticle(1, 60, vector_field, wall_damping) for _ in range(2)]  # eccentricity
    font = pygame.font.SysFont("comicsans", int(box_width // 2.6))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            click_event = pygame.mouse.get_pressed()
            if any(click_event):
                if click_event[0]:  # LEFT CLICK
                    pass # drag ball around
                elif click_event[2]:  # RIGHT CLICK
                    pass # add particle?

        ### drawing vectorField
        screen.fill((70, 69, 5))


        # logic goes here

        for particle in particles:
            particle.update(screen)

            pygame.draw.circle(screen, (123, 12, 90), particle.get_position(), particle.radius)

        # print("Total density: ", total_density)

        # Update display

        pygame.display.update()

        clock.tick(frame_rate)


#
class ProjectileParticle(Particle):
    def __init__(self, mass, particle_radius, vector_field, damping):
        super().__init__(mass, particle_radius, vector_field, damping)
        self.acceleration = np.array([0,9.8])

    def update(self, screen):
        if self.next_position[0] > screen.get_width() - (self.radius) or self.next_position[
            0] < self.radius:  # or within blocked cell
            self.velocity[0] *= -1 * self.damping
        if self.next_position[1] > screen.get_height() - self.radius or self.next_position[1] < self.radius:

            self.velocity[1] *= -1 * self.damping

        self.next_position = np.clip(self.next_position, (self.radius, self.radius),(screen.get_width() - self.radius, screen.get_height() - self.radius))

        self.position = self.next_position


        self.velocity = self.velocity + self.acceleration / self.mass
        self.next_position = self.position + self.velocity * dt
        print(self.radius)

    def check_collision(self, next_particle):
        vector = self.vector_field.get_magnitude(next_particle.position - self.position)
        if 0 < vector <= self.radius + next_particle.radius:
            return (True, self.vector_field.normalise_vector(vector))
        return (False, None)

    def collision_event(self, particles_list):
        for particle in particles_list:
            is_collision, normal_vector = self.check_collision(particle)


    def calculate_final_speeds(self, other_particle, eccentricity):
        # m1u1 + m2u2 = m1v1 + m2v2
        # e(u1 - u2) = v2-v1
        m1 = self.mass # scalar
        m2 = other_particle.mass
        u1 = self.velocity # vector
        u2 = other_particle.velocity
        e = eccentricity

        v1 = (u1 * (m1 - e * m2) + (1 + e) * (m2 * u2)) / (m1 + m2)
        v2 = (u2 * (m2 - e * m1) + (1 + e) * (m1 * u1)) / (m1 + m2)
        return (v1, v2)




if __name__ == "__main__":
    print("piss")
    run()