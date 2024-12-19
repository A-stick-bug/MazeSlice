import pygame
import time
from random import randint

from collisions import collides

# dimensions of the window
WIDTH = 800
HEIGHT = 400
Z_LAYERS = 200

# initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('3D Maze Game')
clock = pygame.time.Clock()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, z):
        super().__init__()
        self.x = x
        self.y = y
        self.z = z
        self.radius = 10
        self.speed = 10
        self.z_speed = 1

    def handle_movement(self):
        """todo, when moving diagonally, lower speed by 1/sqrt2"""
        keys = pygame.key.get_pressed()
        # Handle movement

        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_w]:
            self.z -= self.z_speed
        if keys[pygame.K_s]:
            self.z += self.z_speed

    def display_player(self):
        pygame.draw.circle(
            screen,
            color=(255, 255, 255),
            center=(self.x, self.y),
            radius=self.radius
        )

    def get_position(self):
        return self.x, self.y, self.z

    def get_z(self):
        return self.z


class GameController:
    def __init__(self):
        self.maze = Maze("easy")
        self.player = Player(*self.maze.get_start_location())

    def play(self):
        while True:  # todo: remove infinite loop with proper logic
            self.perform_frame_actions()
            clock.tick(60)  # 60 fps


    def perform_frame_actions(self):
        screen.fill((0, 0, 0))  # wipe screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        self.player.handle_movement()
        self.maze.display_obstacles(self.player.get_z())
        self.player.display_player()
        pygame.display.flip()


class Obstacle:
    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

    def get_circle(self):
        return self.x, self.y, self.z, self.radius

    def __iter__(self):  # allows for unpacking values
        return iter(self.get_circle())


class Maze:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.obstacles = []
        self.power_ups = []

        margin = 50
        self.start_location = (margin, margin, 0)
        self.end_location = (WIDTH - margin, HEIGHT - margin, 0)
        self.generate_maze_obstacles(70, 50, 90)  # PLACEHOLDER

    def generate_maze_obstacles(self, num_obstacles, r_min, r_max):
        for _ in range(num_obstacles):
            x = randint(0, WIDTH)
            y = randint(0, HEIGHT)
            z = randint(0, Z_LAYERS)
            radius = randint(r_min, r_max)
            self.obstacles.append(Obstacle(x, y, z, radius))

    def display_obstacles(self, player_z) -> None:
        """Displays 3D obstacles as a 2D cross-section using the player’s
        z-coordinate"""
        for x, y, z, radius in self.obstacles:
            z_distance = abs(z - player_z)
            circle_radius = self._get_cross_section_radius(radius, z_distance)
            pygame.draw.circle(
                surface=screen,
                color=(0, 0, 255),
                center=(x, y),
                radius=circle_radius,
            )

    def _get_cross_section_radius(self, radius_3d, z_distance):
        """Calculates the apparent size of a sphere based on its Z distance
        from the player."""
        if z_distance >= radius_3d:  # too far to appear
            return 0
        return (radius_3d ** 2 - z_distance ** 2) ** 0.5

    def move_allowed(self, player):
        raise NotImplementedError

    def get_start_location(self):
        return self.start_location

    def get_end_location(self):
        return self.end_location


if __name__ == '__main__':
    game = GameController()
    game.play()
