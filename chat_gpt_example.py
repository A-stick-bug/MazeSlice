import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Maze Navigation")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Player attributes
player_pos = [100, 100, 0]  # Starting position (x, y, z)
player_speed = 10

# Maze dimensions
maze_depth = 200  # Total number of Z-layers

# Sphere obstacles
NUM_OBSTACLES = 75
obstacles = []

for _ in range(NUM_OBSTACLES):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    z = random.randint(0, maze_depth - 1)
    radius = random.randint(50, 90)
    obstacles.append({"x": x, "y": y, "z": z, "radius": radius})


# Helper functions
def calculate_projected_radius(original_radius, z_distance):
    """Calculates the apparent size of a sphere based on its Z distance from the player."""
    if z_distance == 0:  # Avoid division by zero
        return original_radius
    return (original_radius ** 2 - z_distance ** 2) ** 0.5


def render_cross_section(screen, player_z):
    """Renders the current 2D cross-section based on the player's Z-coordinate."""
    screen.fill(BLACK)

    # Draw obstacles on the current Z-layer
    for obstacle in obstacles:
        z_distance = abs(obstacle["z"] - player_z)
        if z_distance <= obstacle["radius"]:  # Only render obstacles near the player's Z-layer
            projected_radius = calculate_projected_radius(obstacle["radius"], z_distance)
            pygame.draw.circle(
                screen,
                BLUE,
                (obstacle["x"], obstacle["y"]),
                projected_radius,
            )

    # Draw the player
    pygame.draw.circle(screen, WHITE, (player_pos[0], player_pos[1]), 10)


def move_player(direction):
    """Moves the player in the specified direction if within bounds."""
    if direction == "UP" and player_pos[1] > 10:
        player_pos[1] -= player_speed
    elif direction == "DOWN" and player_pos[1] < HEIGHT - 10:
        player_pos[1] += player_speed
    elif direction == "LEFT" and player_pos[0] > 10:
        player_pos[0] -= player_speed
    elif direction == "RIGHT" and player_pos[0] < WIDTH - 10:
        player_pos[0] += player_speed
    elif direction == "FORWARD" and player_pos[2] < maze_depth - 1:
        player_pos[2] += 1
    elif direction == "BACKWARD" and player_pos[2] > 0:
        player_pos[2] -= 1


# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle key presses
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        move_player("UP")
    if keys[pygame.K_DOWN]:
        move_player("DOWN")
    if keys[pygame.K_LEFT]:
        move_player("LEFT")
    if keys[pygame.K_RIGHT]:
        move_player("RIGHT")
    if keys[pygame.K_w]:
        move_player("FORWARD")  # Move "up" a Z-layer
    if keys[pygame.K_s]:
        move_player("BACKWARD")  # Move "down" a Z-layer

    # Render the current 2D cross-section
    render_cross_section(screen, player_pos[2])

    # Update the display
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
