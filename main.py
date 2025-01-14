# main.py

import pygame
import sys
import random
from random import randint
import atexit

from player import Player
from item import Item
from shapes import Circle, Sphere
from hunter import Hunter
from leaderboard import Leaderboard
from stopwatch import Stopwatch

# Dimensions of the window
WIDTH = 1200
HEIGHT = 600
Z_LAYERS = 200  # Currently this is inclusive [0,200]

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Maze Game")
clock = pygame.time.Clock()

DEBUG_MODE = False


@atexit.register
def cleanup_pygame():
    """Cleanup Pygame on exit."""
    pygame.quit()


class Obstacle(Sphere):
    def __init__(self, x, y, z, radius):
        super().__init__(x, y, z, radius)


class StartLocation(Circle):
    def __init__(self, x, y, z, radius):
        super().__init__(x, y, z, radius)
        self.surf = pygame.image.load(
            "graphics/maze/start_location.png"
        ).convert_alpha()

    # @override
    def display(self, screen, from_z, color=(0, 0, 255)) -> None:
        if self.z == from_z:
            start_rect = self.surf.get_rect(center=(self.x, self.y))
            screen.blit(self.surf, start_rect)


class EndLocation(Circle):
    def __init__(self, x, y, z, radius):
        super().__init__(x, y, z, radius)
        self.surf = pygame.image.load(
            "graphics/maze/end_location.png"
        ).convert_alpha()

    # @override
    def display(self, screen, from_z, color=(0, 0, 255)) -> None:
        if self.z == from_z:
            end_rect = self.surf.get_rect(center=(self.x, self.y))
            screen.blit(self.surf, end_rect)


class Maze:
    def __init__(self, difficulty):
        # start and end locations
        margin = 50
        self.start_location = StartLocation(margin, margin, 0, 25)
        self.end_location = EndLocation(WIDTH - margin, HEIGHT - margin, Z_LAYERS, 25)

        # generate objects inside the maze based on difficulty
        self.difficulty = difficulty
        self.obstacles: list[Obstacle] = []
        self.power_ups: list[Item] = []
        self.hunters: list[Hunter] = []

        if difficulty == "easy":
            self.generate_maze_obstacles(90, 50, 90)
            self.generate_maze_items(75)
        elif difficulty == "medium":
            self.generate_maze_obstacles(110, 50, 90)
            self.generate_maze_items(75)
            self.generate_maze_hunters(3)
        elif difficulty == "hard":
            self.generate_maze_obstacles(120, 50, 90)
            self.generate_maze_items(75)
            self.generate_maze_hunters(6)
        elif difficulty == "???":
            self.generate_maze_obstacles(0, 50, 90)
            self.generate_maze_items(100)
            self.generate_maze_hunters(200)

    def generate_maze_obstacles(self, num_obstacles, r_min, r_max) -> None:
        """Fill up `self.obstacles` with random obstacles with radius
        in the range [r_min, r_max], ensures the obstacles do not overlap with
        the start and end locations."""
        while len(self.obstacles) < num_obstacles:
            x = randint(0, WIDTH)
            y = randint(0, HEIGHT)
            z = randint(0, Z_LAYERS)
            radius = randint(r_min, r_max)
            obst = Obstacle(x, y, z, radius)
            if not obst.collides_with_circle(
                    self.start_location
            ) and not obst.collides_with_circle(self.end_location):
                self.obstacles.append(obst)
                print(f"Generated obstacle at ({x}, {y}, {z}) with radius {radius}")

    def generate_maze_items(self, num_items) -> None:
        """Fill up `self.power_ups` with random items."""
        item_types = [
            "speed_boost",
            "dash",
            "teleport",
        ]
        while len(self.power_ups) < num_items:
            x = randint(20, WIDTH - 20)
            y = randint(20, HEIGHT - 20)
            z = randint(-5, Z_LAYERS - 5)  # -5 so items spawn more often on z = 0
            radius = 11
            item_type = random.choice(item_types)
            item = Item(x, y, z, z + 15, radius, item_type)
            # ensure items do not overlap with start/end locations or obstacles
            if item.collides_with_circle(self.start_location):
                continue
            elif item.collides_with_circle(self.end_location):
                continue
            elif any(obst.collides_with_circle(item) for obst in self.obstacles):
                continue
            self.power_ups.append(item)
            print(f"Generated item: {item_type} at ({x}, {y}, {z})")

    def generate_maze_hunters(self, num_hunters) -> None:
        """Generate `num_hunters` hunters on the maze"""
        for _ in range(num_hunters):
            x = randint(20, WIDTH - 20)  # random location and speed
            y = randint(20, HEIGHT - 20)
            z = randint(21, Z_LAYERS)
            radius = randint(12, 18)
            speed = randint(50, 200) / 100
            hunter = Hunter(x, y, z, radius, speed)
            print(f"Generated hunter at ({x}, {y}, {z})")
            self.hunters.append(hunter)

    def display_obstacles(self, player_z) -> None:
        """Displays 3D obstacles as a 2D cross-section using the player’s
        z-coordinate."""
        for obst in self.obstacles:
            obst.display(screen, player_z)

    def display_items(self, player_z) -> None:
        """Displays items in the maze based on player's Z-layer."""
        for item in self.power_ups:
            item.display(screen, player_z)

    def display_hunters(self, player) -> None:
        """Displays hunters in the maze based on the player's Z-layer"""
        for hunter in self.hunters:
            hunter.display_hunter(screen, player)

    def display_start_end(self, from_z) -> None:
        """Display the start and end locations of the maze"""
        self.start_location.display(screen, from_z, (255, 255, 0))
        self.end_location.display(screen, from_z, (255, 255, 0))

    def collect_items(self, player) -> None:
        """Checks and collects items if the player collides with them."""
        for item in self.power_ups:
            if item.check_collision(player):
                item.apply_effect(player, maze=self)  # Pass maze instance

    def move_hunters(self, player) -> None:
        """Update the position of the hunters based on the player's position."""
        for hunter in self.hunters:
            hunter.handle_movement(player)

    def collide_hunters(self, player) -> bool:
        """Check if the player collides with any of the hunters."""
        for hunter in self.hunters:
            if hunter.check_collision(player):
                return True
        return False

    def is_move_allowed(self, character) -> bool:
        """Check if a given character can be at a certain position in the maze."""
        # check collisions with obstacles
        char_circle = Circle(*character.get_parameters())
        for obst in self.obstacles:
            if obst.collides_with_circle(char_circle):
                return False

        # Check collision with map boundaries
        cx, cy, cz, r = character.get_parameters()
        if (cx < r
                or cx > WIDTH - r
                or cy < r
                or cy > HEIGHT - r
                or cz < 0
                or cz > Z_LAYERS):
            return False

        return True

    def is_move_allowed_pos(self, x, y, z) -> bool:
        """
        Checks if a specific (x, y, z) position is free (no obstacles).

        :param x: X-coordinate
        :param y: Y-coordinate
        :param z: Z-coordinate
        :return: True if position is free, False otherwise
        """
        temp_circle = Circle(x, y, z, 10)  # assuming player radius is 10
        for obst in self.obstacles:
            if obst.collides_with_circle(temp_circle):
                return False

        # Check collision with map boundaries
        if (x < temp_circle.radius
                or x > WIDTH - temp_circle.radius
                or y < temp_circle.radius
                or y > HEIGHT - temp_circle.radius
                or z < 0
                or z > Z_LAYERS):
            return False

        return True

    def get_start_location(self):
        return self.start_location

    def get_end_location(self):
        return self.end_location


class GameController:
    def __init__(self):
        # [menu, help_menu, playing, game_over, winner]
        # game related variables
        self.game_state = "menu"
        self.maze = None
        self.player = None
        self.game_events = pygame.event.get()
        self.leaderboard = Leaderboard()
        self.stopwatch = Stopwatch(precision=2)

        # surfaces for display
        self.main_menu_surf = pygame.image.load("graphics/main_menu.png").convert_alpha()
        self.pause_menu_surf = pygame.image.load("graphics/pause_menu.png").convert_alpha()

    def play(self) -> None:
        """Main loop of the game"""
        while True:
            self.game_events = pygame.event.get()

            # check if player wants to exit game
            for event in self.game_events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.game_state == "menu":
                self.perform_menu_frame_actions()
            elif self.game_state == "help_menu":
                self.perform_help_menu_frame_actions()
            elif self.game_state == "leaderboard":
                self.perform_leaderboard_frame_actions()
            elif self.game_state == "playing":
                self.perform_playing_frame_actions()
            elif self.game_state == "paused":
                self.perform_paused_frame_actions()
            elif self.game_state == "game_over":
                self.perform_game_over_frame_actions()
            elif self.game_state == "winner":
                self.perform_winner_frame_actions()
            elif self.game_state == "loser":
                self.perform_loser_frame_actions()

            pygame.display.flip()
            clock.tick(60)  # 60 fps

    def start_game(self, difficulty: str) -> None:
        """Start a game with the selected difficulty"""
        self.maze = Maze(difficulty)
        self.player = Player(*self.maze.get_start_location().get_location())
        self.game_state = "playing"
        self.stopwatch.start()

    def pause_game(self) -> None:
        """Pause the current game"""
        self.stopwatch.pause()
        self.game_state = "paused"

    def resume_game(self) -> None:
        """Resume the currently paused game"""
        self.stopwatch.start()
        self.game_state = "playing"

    def perform_menu_frame_actions(self) -> None:
        """Performs frame actions for when the game is in the `menu` state."""
        screen.fill((0, 0, 0))
        screen.blit(self.main_menu_surf, (0, 0))  # display menu

        # check for interactions with menu
        for event in self.game_events:
            # check if the player wants to start a game in one of the
            # available difficulties
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()

                # handle difficulty selection
                if 770 <= x <= 1132:
                    if 204 <= y <= 274:
                        self.start_game("easy")
                    elif 295 <= y <= 365:
                        self.start_game("medium")
                    elif 387 <= y <= 458:
                        self.start_game("hard")
                    elif 479 <= y <= 549:
                        self.start_game("???")

                # handle leaderboard button
                elif 120 <= x <= 360 and 514 <= y <= 556:
                    self.game_state = "leaderboard"

                # handle help menu button
                elif 380 <= x <= 618 and 514 <= y <= 556:
                    self.game_state = "help_menu"

    def perform_help_menu_frame_actions(self) -> None:
        """Performs frame actions for when the game is in the `help_menu` state."""
        # todo: implement this
        screen.fill((0, 0, 0))
        self.display_text("Help Menu - Press M to Return", WIDTH // 2, HEIGHT // 2)

        for event in self.game_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    self.game_state = "menu"

    def perform_leaderboard_frame_actions(self):
        """Performs game actions for when the player is viewing the leaderboard"""
        # display leaderboard
        screen.fill((0, 0, 0))
        self.leaderboard.display(screen)

        # check if the player wants to exit leaderboard
        for event in self.game_events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if 1124 <= x <= 1180 and 19 <= y <= 69:
                    self.game_state = "menu"  # return to menu
                    break

    def perform_playing_frame_actions(self) -> None:
        """Performs frame actions for when the player is in a game"""
        screen.fill((0, 0, 0))

        for event in self.game_events:
            # check if player wants to exit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.game_state = "help_menu"
                if event.key == pygame.K_p:
                    self.pause_game()

        if DEBUG_MODE:
            self.run_debug()

        # handle player movement with collisions
        self.player.handle_movement(self.maze)
        self.maze.collect_items(self.player)
        self.maze.move_hunters(self.player)

        # display objects and effects
        self.maze.display_obstacles(self.player.get_z())
        self.maze.display_items(self.player.get_z())
        self.maze.display_hunters(self.player)
        self.maze.display_start_end(self.player.get_z())
        self.player.display_player()
        self.stopwatch.display(screen)
        self.display_active_effects()

        # check if we won/lost the game
        if self.check_win_condition():
            self.game_state = "winner"
            self.leaderboard.add_score(
                self.maze.difficulty, self.stopwatch.get_elapsed_time()
            )
        if self.check_lose_condition():
            self.game_state = "loser"

    def perform_paused_frame_actions(self):
        """Performs frame actions for when the game is paused"""
        screen.blit(self.pause_menu_surf, (0, 0))  # display menu

        # check if any of the buttons are pressed
        for event in self.game_events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if 416 <= x <= 735:
                    if 177 <= y <= 248:  # resume
                        self.resume_game()
                    elif 258 <= y <= 331:
                        ...  # help menu
                    elif 341 <= y <= 414:
                        ...  # restart
                    elif 423 <= y <= 496:  # quit to menu
                        self.reset_game()

    def perform_game_over_frame_actions(self):
        """Performs frame actions for when the player just lost a game."""
        # Placeholder for game over actions
        screen.fill((0, 0, 0))
        self.display_text("Game Over - Press R to Restart", WIDTH // 2, HEIGHT // 2)

        for event in self.game_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()

    def perform_winner_frame_actions(self):
        """Performs frame actions for when the game is in the `winner` state."""
        # Placeholder for winner actions
        screen.fill((0, 0, 0))
        self.display_text("You Won! - Press Q to Quit", WIDTH // 2, HEIGHT // 2)

        for event in self.game_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()

    def perform_loser_frame_actions(self):
        """Performs frame actions for when the game is in the `lost` state."""
        # Placeholder for loser(?!) actions
        screen.fill((0, 0, 0))
        self.display_text(
            "You Lost the Game! - Press Q to Quit", WIDTH // 2, HEIGHT // 2
        )

        for event in self.game_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()

    def run_debug(self):
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
        for event in self.game_events:
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
            remaining = int(
                self.player.speed_boost_end_time - pygame.time.get_ticks() / 1000
            )
            self.display_text(
                f"Speed Boost Active! ({remaining}s)", 100, 50, 24, (255, 0, 0)
            )

    def check_win_condition(self):
        """Check if the player has reached the end location."""
        if self.player.collides_with_circle(self.maze.get_end_location()):
            print("Win condition met!")
            return True
        return False

    def check_lose_condition(self):
        """Check if the player lost the game."""
        if self.maze.collide_hunters(self.player):
            print("Lost condition met!")
            return True
        return False

    def reset_game(self):
        """Reset the game to initial state."""
        self.__init__()


if __name__ == "__main__":
    game = GameController()
    game.play()
