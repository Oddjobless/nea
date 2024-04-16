# from Simulations.SimulationFiles.baseClasses import *
# # ported from projectile sim. could make a ideal gas sim, with adjustable volume and more particles and higher temperature
#
# import pymunk
# import pymunk.pygame_util
#
# class Object:
#     def __init__(self, space, radius, mass):
#         self.body = pymunk.Body()
#         self.body.position = (100, 100)
#         self.shape = pymunk.Circle(self.body, radius)
#         self.shape.mass = mass
#         self.shape.color = (123, 12, 90, 100)
#         self.shape.elasticity = 1
#         self.shape.friction = 0
#         space.add(self.body, self.shape)
#
#
# def calculate_distance(p1, p2):
#     return np.sqrt((p2[1] - p1[1]) ** 2 + (p2[0] - p1[0]) ** 2)
#
# def calculate_angle(p1, p2):
#     return np.arctan2(p2[1] - p1[1], p2[0] - p1[0])
#
# def run():
#     pygame.init()
#     clock = pygame.time.Clock()
#     screen_width, screen_height = 1920, 1080
#     screen = pygame.display.set_mode((screen_width, screen_height))
#     pygame.display.set_caption("Pygame Boilerplate")
#     rows, columns = 18, 32
#     box_width = screen_width // columns
#     container = Container(rows, columns)
#
#     container.particles.extend([ProjectileParticle(1, 30, container, container.wall_damping, floor_damping=1.00) for _ in range(100)])  # eccentricity
#     font = pygame.font.SysFont("comicsans", int(box_width // 2.6))
#     frame = 0
#     mouse_rel_refresh = frame_rate * 0.5##
#
#
#     space = pymunk.Space()
#     space.gravity = (0.0, 981)
#     draw_options = pymunk.pygame_util.DrawOptions(screen)
#
#     pressed_pos = None
#     ball = None
#
#     ball = Object(space, 40, 2)
#     width, height = 1920, 1080
#
#
#     rects = [
#         [(width / 2, height - 10), (width, 20)],
#         [(width / 2, 10), (width, 20)],
#         [(10, height/2), (20, height)],
#         [(width - 10, height / 2), (20, height)]
#     ]
#     for position, size in rects:
#         body = pymunk.Body(body_type=pymunk.Body.STATIC)
#         body.position = position
#         shape = pymunk.Poly.create_box(body, size)
#         space.add(body, shape)
#         shape.elasticity = 1
#         shape.friction = 0.5
#
#
#     while True:
#
#         screen.fill((70, 69, 5))
#
#         ### drawing vectorField
#
#         space.debug_draw(draw_options)
#
#         # logic goes here
#
#         """for index, particle in enumerate(container.particles):
#
#             particle.update(screen)
#             if container.air_resistance:
#                 particle.apply_air_resistance()
#
#         for particle in container.particles:
#             particle.collision_event()
#
#             pygame.draw.circle(screen, (123, 12, 90), particle.position, particle.radius)
#             # pygame.draw.circle(screen, (123, 12, 90), collide_x, self.radius)
#
#
#         completed = set()
#         for ball_i, ball_j in container.colliding_balls_pairs:
#             completed.add(ball_i)
#             if ball_j not in completed:
#                 print("Ball", ball_i, "collides with", ball_j)
#                 ball_i.resolve_dynamic_collision(ball_j)
#                 pygame.draw.line(screen, (0, 255, 0), ball_i.position, ball_j.position)
#         container.colliding_balls_pairs.clear()
#
#         if container.draw_line_to_mouse and container.selected_particle != None:
#             pygame.draw.line(screen, (255, 0, 0), container.particles[container.selected_particle].position, pygame.mouse.get_pos())
#         else:
#             container.draw_line_to_mouse = False"""
#
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 return
#
#             elif event.type == pygame.KEYUP:
#                 if event.key == pygame.K_q:
#                     pygame.quit()
#                     return
#
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 ball.body.apply_impulse_at_local_point((100,0), (0,0))
#
#
#             """if event.type == pygame.MOUSEBUTTONDOWN:
#                 if event.button == 1 and container.selected_particle == None:
#                     container.drag_particle(event.pos)
#                     print("adf")
#
#                 elif event.button == 3 and container.selected_particle == None:
#                     container.project_particle(event.pos)
#
#
#
#
#             elif event.type == pygame.MOUSEBUTTONUP:
#                 if event.button == 1 and container.selected_particle != None:
#                     container.drop_particle()
#
#                 elif event.button == 3 and container.selected_particle != None:
#                     container.release_projected_particle(event.pos)
#
#             if container.selected_particle != None and not container.draw_line_to_mouse:
#                 container.move_selected_particle(event.pos)"""
#
#
#
#         pygame.display.update()
#
#
#         space.step(dt)
#         clock.tick(frame_rate)
#
#
# #
# class ProjectileParticle(Particle):
#     def __init__(self, mass, particle_radius, container, _wall_damping, floor_damping):
#         super().__init__(mass, particle_radius, container, _wall_damping)
#         g = 0
#         self.acceleration = np.array([0, g])
#         self.floor_damping = floor_damping
#
#     def update(self, screen):
#
#         self.next_position = self.position + self.velocity * dt
#         if self.next_position[0] > screen.get_width() - (self.radius) or self.next_position[
#             0] < self.radius:  # or within blocked cell
#             self.velocity[0] *= -1 * self.damping
#         if self.next_position[1] > screen.get_height() - self.radius or self.next_position[1] < self.radius:
#             self.velocity[1] *= -1 * self.floor_damping
#
#         self.next_position = np.clip(self.next_position, (self.radius, self.radius),
#                                      (screen.get_width() - self.radius, screen.get_height() - self.radius))
#
#         self.position = self.next_position
#
#
#
#
#
#         # print(self.container.grid)
#         if self.container.particles.index(self) != self.container.selected_particle:
#             self.velocity = self.velocity + self.acceleration * self.mass
#
#
#
#
#
#
#
# class Container(SpatialMap):
#     def __init__(self, rows, columns):
#         super().__init__(rows, columns)
#         self.particles = []
#         self.selected_particle = None
#         self.projected_particle_velocity_multiplier = 80
#
#         self.draw_line_to_mouse = False
#         self.colliding_balls_pairs = []
#
#         self.air_resistance = True
#         self.drag_coefficient = 0.000000001
#
#
#
#
#
#
# if __name__ == "__main__":
#     print("piss")
#     run()
