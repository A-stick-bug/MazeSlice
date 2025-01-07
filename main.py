# main.py

import pygame
import sys
import random
from random import randint
import atexit

from Player import Player
from item import Item
from shapes import Circle, Sphere, Cylinder

# Dimensions of the window
WIDTH = 1200
HEIGHT = 600
Z_LAYERS = 200  # Currently this is inclusive [0,200]

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('3D Maze Game')
clock = pygame.time.Clock()

DEBUG_MODE = True


@atexit.register
def cleanup_pygame():
    """Cleanup Pygame on exit."""
    pygame.quit()


class Obstacle(Sphere):
    def __init__(self, x, y, z, radius):
        super().__init__(x, y, z, radius)


class Maze:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.obstacles: list[Obstacle] = []
        self.power_ups: list[Item] = []
        self.Z_LAYERS = Z_LAYERS  # Expose Z_LAYERS as an instance attribute

        margin = 50
        self.start_location = Circle(margin, margin, 0, 25)
        self.end_location = Circle(WIDTH - margin, HEIGHT - margin, Z_LAYERS, 25)
        self.generate_maze_obstacles(70, 50, 90)  # Adjust numbers as needed
        self.generate_maze_items(20)  # Generate 20 items

    def generate_maze_obstacles(self, num_obstacles, r_min, r_max):
        """Fill up `self.obstacles` with random obstacles with radius
        in the range [r_min, r_max], ensures the obstacles do not overlap with
        the start and end locations."""
        while len(self.obstacles) < num_obstacles:
            x = randint(self.start_location.radius, WIDTH - self.start_location.radius)
            y = randint(self.start_location.radius, HEIGHT - self.start_location.radius)
            z = randint(0, self.Z_LAYERS)
            radius = randint(r_min, r_max)
            obst = Obstacle(x, y, z, radius)
            if (not obst.collides_with_circle(self.start_location) and
                    not obst.collides_with_circle(self.end_location)):
                self.obstacles.append(obst)
                print(f"Generated obstacle at ({x}, {y}, {z}) with radius {radius}")

    def generate_maze_items(self, num_items):
        """Fill up `self.power_ups` with random items."""
        item_types = ['speed_boost', 'dash', 'teleport']  # Replaced 'stealth' with 'teleport'
        while len(self.power_ups) < num_items:
            x = randint(20, WIDTH - 20)
            y = randint(20, HEIGHT - 20)
            z = 0  # Fix items to ground level
            radius = 10
            item_type = random.choice(item_types)
            color = self.get_color_by_type(item_type)
            item = Item(x, y, z, z + 10, radius, item_type, color)
            # Ensure items do not overlap with start/end locations or obstacles
            if (not item.collides_with_circle(self.start_location) and
                not item.collides_with_circle(self.end_location) and
                all(not obst.collides_with_circle(item) for obst in self.obstacles)):
                self.power_ups.append(item)
                print(f"Generated item: {item_type} at ({x}, {y}, {z})")

    def get_color_by_type(self, item_type):
        """Returns color based on item type."""
        colors = {
            'speed_boost': (255, 0, 0),      # Red
            'dash': (0, 255, 0),             # Green
            'teleport': (128, 0, 128),       # Purple
        }
        return colors.get(item_type, (255, 255, 255))  # Default white

    def display_obstacles(self, player_z) -> None:
        """Displays 3D obstacles as a 2D cross-section using the player’s z-coordinate."""
        for obst in self.obstacles:
            obst.display(screen, player_z)

    def display_items(self, player_z) -> None:
        """Displays items in the maze based on player's Z-layer."""
        for item in self.power_ups:
            item.display(screen, player_z)

    def collect_items(self, player):
        """Checks and collects items if the player collides with them."""
        for item in self.power_ups:
            if item.check_collision(player):
                item.apply_effect(player, maze=self)  # Pass maze instance

    def is_move_allowed(self, character):
        """Check if a given character can be at a certain position in the maze."""
        # Check collisions with obstacles
        char_circle = Circle(*character.get_parameters())
        for obst in self.obstacles:
            if obst.collides_with_circle(char_circle):
                return False

        # Check collision with map boundaries
        cx, cy, cz, r = character.get_parameters()
        if (cx < r or cx > WIDTH - r or cy < r or cy > HEIGHT - r
                or cz < 0 or cz > self.Z_LAYERS):
            return False

        return True

    def is_move_allowed_pos(self, x, y, z):
        """
        Checks if a specific (x, y, z) position is free (no obstacles).

        :param x: X-coordinate
        :param y: Y-coordinate
        :param z: Z-coordinate
        :return: True if position is free, False otherwise
        """
        temp_circle = Circle(x, y, z, 10)  # Assuming player radius is 10
        for obst in self.obstacles:
            if obst.collides_with_circle(temp_circle):
                return False

        # Check collision with map boundaries
        if (x < temp_circle.radius or x > WIDTH - temp_circle.radius or
            y < temp_circle.radius or y > HEIGHT - temp_circle.radius or
            z < 0 or z > self.Z_LAYERS):
            return False

        return True

    def get_start_location(self):
        return self.start_location

    def get_end_location(self):
        return self.end_location


class GameController:
    def __init__(self):
        self.game_state = "menu"  # [menu, help_menu, playing, game_over, winner]
        self.maze = Maze("easy")
        self.player = Player(*self.maze.get_start_location().get_location())

    def play(self):
        while True:
            if self.game_state == "menu":
                self.perform_menu_frame_actions()
            elif self.game_state == "help_menu":
                self.perform_help_menu_frame_actions()
            elif self.game_state == "playing":
                self.perform_playing_frame_actions()
            elif self.game_state == "game_over":
                self.perform_game_over_frame_actions()
            elif self.game_state == "winner":
                self.perform_winner_frame_actions()
            clock.tick(60)  # 60 fps

    def perform_menu_frame_actions(self):
        """Performs frame actions for when the game is in the `menu` state."""
        # Placeholder for menu actions
        screen.fill((0, 0, 0))
        self.display_text("Menu - Press Enter to Play", WIDTH // 2, HEIGHT // 2)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.game_state = "playing"

    def perform_help_menu_frame_actions(self):
        """Performs frame actions for when the game is in the `help_menu` state."""
        # Placeholder for help menu actions
        screen.fill((0, 0, 0))
        self.display_text("Help Menu - Press M to Return", WIDTH // 2, HEIGHT // 2)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.game_state = "menu"

    def perform_playing_frame_actions(self):
        """Performs frame actions for when the game is in the `playing` state."""
        screen.fill((0, 0, 0))  # Wipe screen

        events = pygame.event.get()
        for event in events:  # Check exit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.game_state = "help_menu"

        if DEBUG_MODE:
            self.run_debug(events)

        # Handle player movement with collisions
        self.player.handle_movement(self.maze)

        # Display obstacles and items
        self.maze.display_obstacles(self.player.get_z())
        self.maze.display_items(self.player.get_z())

        # Collect items if any
        self.maze.collect_items(self.player)

        # Display player
        self.player.display_player()

        # Display active effects
        self.display_active_effects()

        # Check for win condition
        if self.check_win_condition():
            self.game_state = "winner"

        pygame.display.flip()

    def perform_game_over_frame_actions(self):
        """Performs frame actions for when the game is in the `game_over` state."""
        # Placeholder for game over actions
        screen.fill((0, 0, 0))
        self.display_text("Game Over - Press R to Restart", WIDTH // 2, HEIGHT // 2)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()

    def perform_winner_frame_actions(self):
        """Performs frame actions for when the game is in the `winner` state."""
        # Placeholder for winner actions
        screen.fill((0, 0, 0))
        self.display_text("You Won! - Press Q to Quit", WIDTH // 2, HEIGHT // 2)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

    def run_debug(self, frame_events):
        """
        Create coordinate grid for easy drawing and check frame rate.
        """
        # 1. Draw grid
        grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(0, WIDTH, 100):  # Big vertical lines
            line = pygame.Rect(i, 0, 2, HEIGHT)
            pygame.draw.rect(grid_surface, "red", line)
        for i in range(0, HEIGHT, 100):  # Big horizontal lines
            line = pygame.Rect(0, i, WIDTH, 2)
            pygame.draw.rect(grid_surface, "red", line)
        for i in range(0, WIDTH, 20):  # Small vertical lines
            line = pygame.Rect(i, 0, 1, HEIGHT)
            pygame.draw.rect(grid_surface, "grey", line)
        for i in range(0, HEIGHT, 20):  # Small horizontal lines
            line = pygame.Rect(0, i, WIDTH, 1)
            pygame.draw.rect(grid_surface, "grey", line)
        screen.blit(grid_surface, (0, 0))  # Display all grid lines

        # 2. Right click to get coordinates
        for event in frame_events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                print(f"Mouse coordinates: {event.pos}")

    def display_text(self, text, x, y, font_size=36, color=(255, 255, 255)):
        """Utility method to display text on the screen."""
        font = pygame.font.SysFont(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    def display_active_effects(self):
        """Displays active effects on the screen."""
        if self.player.speed_boost_active:
            remaining = int(self.player.speed_boost_end_time - pygame.time.get_ticks() / 1000)
            self.display_text(f"Speed Boost Active! ({remaining}s)", 100, 50, 24, (255, 0, 0))
        # Add more active effects here if needed

    def check_win_condition(self):
        """Check if the player has reached the end location."""
        if self.player.collides_with_circle(self.maze.get_end_location()):
            print("Win condition met!")
            return True
        return False

    def reset_game(self):
        """Reset the game to initial state."""
        self.maze = Maze("easy")
        self.player = Player(*self.maze.get_start_location().get_location())
        self.game_state = "playing"


if __name__ == '__main__':
    game = GameController()
    game.play()
