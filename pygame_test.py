import pygame
import sys

# Initialize Pygame
pygame.init()

# Set the dimensions of the window
screen = pygame.display.set_mode((1800, 1000))

# Load the background image
backgroundImage = pygame.image.load('./materials/background/summer_sunset.jpg')

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Blit the image onto the screen as the background
    screen.blit(backgroundImage, (0, -100))

    # Update the display
    pygame.display.flip()

pygame.quit()
sys.exit()