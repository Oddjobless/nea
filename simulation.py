import pygame
import sys
pygame.init()

def run():
    screen = pygame.display.set_mode((800, 600))
    screen.fill((255,69,180))
    pygame.display.set_caption("Pygame Boilerplate")


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # logic goes here

        # Drawing code goes here

        # Update display
        pygame.display.flip()

if __name__ == "__main__":
    run()
