import pygame
import pygame.math as pm  # for vector math

import sys
import time
import random
from random import randint
import atexit

from shapes import Circle, Sphere, Cylinder

# dimensions of the window
WIDTH = 1200
HEIGHT = 600
Z_LAYERS = 200  # currently this is inclusive [0,200]

# initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('3D Maze Game')
clock = pygame.time.Clock()

DEBUG_MODE = True


@atexit.register
def cleanup_pygame():
    """todo: save leaderboard and stuff"""
    ...


class Player(Circle):
    def __init__(self, x, y, z, radius=10):
        super().__init__(x, y, z, radius)
        self.speed = 5
        self.z_speed = 1

    def handle_movement(self, maze):
        """todo: if we cant go x units in a direction, check the maximum we CAN go, slide along the walls"""
        keys = pygame.key.get_pressed()

        old_location = self.get_location()

        movement_vector = [0, 0, 0]
        if keys[pygame.K_UP]:
            movement_vector[1] -= self.speed
        if keys[pygame.K_DOWN]:
            movement_vector[1] += self.speed
        if keys[pygame.K_LEFT]:
            movement_vector[0] -= self.speed
        if keys[pygame.K_RIGHT]:
            movement_vector[0] += self.speed
        if keys[pygame.K_w]:
            movement_vector[2] += self.z_speed
        if keys[pygame.K_s]:
            movement_vector[2] -= self.z_speed

        # maintain speed when moving diagonally
        if movement_vector[0] != 0 and movement_vector[1] != 0:
            movement_vector[0] /= 1.414
            movement_vector[1] /= 1.414

        self.x += movement_vector[0]
        self.y += movement_vector[1]
        self.z += movement_vector[2]

        # can't move here, revert location
        if not maze.is_move_allowed(self):
            self.set_position(*old_location)

    def display_player(self):
        pygame.draw.circle(
            screen,
            color=(255, 255, 255),
            center=(self.x, self.y),
            radius=self.radius
        )

    def set_position(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


class GameController:
    def __init__(self):
        self.game_state = "playing"  # [menu, help_menu, playing, game_over, winner]
        self.maze = Maze("easy")
        self.player = Player(*self.maze.get_start_location().get_location())

    def play(self):
        while True:  # todo: remove infinite loop with proper logic
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
        """Performs frame actions for when the game is in the `menu` state"""
        raise NotImplementedError

    def perform_help_menu_frame_actions(self):
        """Performs frame actions for when the game is in the `help_menu` state"""
        raise NotImplementedError

    def perform_playing_frame_actions(self):
        """Performs frame actions for when the game is in the `playing` state"""
        screen.fill((0, 0, 0))  # wipe screen

        events = pygame.event.get()
        for event in events:  # check exit game
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if DEBUG_MODE:
            self.run_debug(events)

        # handles player movement with collisions
        self.player.handle_movement(self.maze)

        self.maze.display_obstacles(self.player.get_z())
        self.player.display_player()
        pygame.display.flip()

    def perform_game_over_frame_actions(self):
        raise NotImplementedError

    def perform_winner_frame_actions(self):
        raise NotImplementedError

    def run_debug(self, frame_events):
        """
        Create coordinate grid for easy drawing and check frame rate
        """
        # 1. Draw grid
        grid_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(0, WIDTH, 100):  # big vertical lines
            line = pygame.Rect(i, 0, 2, HEIGHT)
            pygame.draw.rect(grid_surface, "red", line)
        for i in range(0, HEIGHT, 100):  # big horizontal lines
            line = pygame.Rect(0, i, WIDTH, 2)
            pygame.draw.rect(grid_surface, "red", line)
        for i in range(0, WIDTH, 20):  # small vertical lines
            line = pygame.Rect(i, 0, 1, HEIGHT)
            pygame.draw.rect(grid_surface, "grey", line)
        for i in range(0, HEIGHT, 20):  # small horizontal lines
            line = pygame.Rect(0, i, WIDTH, 1)
            pygame.draw.rect(grid_surface, "grey", line)
        screen.blit(grid_surface, (0, 0))  # display all grid lines

        # # 2. Check FPS every 5 seconds
        # if frame % 300 == 0 and self.game_state == "playing":
        #     t = time.time() - start_time
        #     fps = frame / t
        #     print(f"Frame: {frame}, Time: {t:.2f} , FPS: {fps:.2f}")
        #     if fps < 55:
        #         print("LOW FPS WARNING", file=sys.stderr)

        # 3. right click to get coordinates
        for event in frame_events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                print(f"Mouse coordinates: {event.pos}")


class Obstacle(Sphere):
    def __init__(self, x, y, z, radius):
        super().__init__(x, y, z, radius)


class Maze:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.obstacles: list[Obstacle] = []
        self.power_ups = []

        margin = 50
        self.start_location = Circle(margin, margin, 0, 25)
        self.end_location = Circle(WIDTH - margin, HEIGHT - margin, Z_LAYERS, 25)
        self.generate_maze_obstacles(70, 50, 90)  # PLACEHOLDER

    def generate_maze_obstacles(self, num_obstacles, r_min, r_max):
        """fill up `self.obstacles` with random obstacles with radius
        in the range [r_min, r_max], ensures the obstacles do not overlap with
        the start and end locations"""
        while len(self.obstacles) < num_obstacles:
            x = randint(0, WIDTH)
            y = randint(0, HEIGHT)
            z = randint(0, Z_LAYERS)
            radius = randint(r_min, r_max)
            obst = Obstacle(x, y, z, radius)
            if (not obst.collides_with_circle(self.start_location) and
                    not obst.collides_with_circle(self.end_location)):
                self.obstacles.append(obst)

    def display_obstacles(self, player_z) -> None:
        """Displays 3D obstacles as a 2D cross-section using the player’s
        z-coordinate"""
        for obst in self.obstacles:
            obst.display(screen, player_z)

    def is_move_allowed(self, character):
        """Check if a given character can be at a certain position in the
        maze"""
        # check collisions with obstacles
        char_circle = Circle(*character.get_parameters())
        for obst in self.obstacles:
            if obst.collides_with_circle(char_circle):
                return False

        # check collision with map boundaries
        cx, cy, cz, r = character.get_parameters()
        if (cx < r or cx > WIDTH - r or cy < r or cy > HEIGHT - r
                or cz < 0 or cz > Z_LAYERS):
            return False

        return True

    def get_start_location(self):
        return self.start_location

    def get_end_location(self):
        return self.end_location


if __name__ == '__main__':
    game = GameController()
    game.play()
