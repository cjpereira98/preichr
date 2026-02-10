import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Rocket")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 128, 255)
DARK_BLUE = (0, 100, 200)

# Fonts
title_font = pygame.font.Font(None, 74)
button_font = pygame.font.Font(None, 50)

# Text
title_text = title_font.render("Rocket", True, BLACK)
title_rect = title_text.get_rect(center=(width // 2, height // 4))

# Button
button_text = button_font.render("Start", True, WHITE)
button_rect = button_text.get_rect(center=(width // 2, height // 2))
button_color = BLUE

# Game loop
running = True
while running:
    screen.fill(WHITE)

    # Draw title
    screen.blit(title_text, title_rect)

    # Draw button
    pygame.draw.rect(screen, button_color, button_rect.inflate(20, 20))
    screen.blit(button_text, button_rect)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                print("Start button clicked!")

    # Change button color on hover
    if button_rect.collidepoint(pygame.mouse.get_pos()):
        button_color = DARK_BLUE
    else:
        button_color = BLUE

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
