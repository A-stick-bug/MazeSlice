import atexit
import random
from random import randint
import sys

import pygame

from hunter import Hunter
from item import Item
from leaderboard import Leaderboard
from player import Player
from shapes import Circle, Sphere
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


class StartLocation(Circle):
    """A starting location represented as a circular object.

    Attributes:
        surf: A pygame surface for the spawn point image
        angle: The current angle of rotation for the spawn point image
    """

    def __init__(self, x, y, z, radius):
        """Initializes the start location with its position and radius.

        Args:
            x: The x-coordinate of the spawn point
            y: The y-coordinate of the spawn point
            z: The z-coordinate for depth or layering
            radius: The radius of the circle representing the start location
        """
        super().__init__(x, y, z, radius)
        self.surf = pygame.image.load(
            "graphics/maze/start_location.png"
        ).convert_alpha()
        self.angle = 0

    def display(self, screen, from_z, color=(0, 0, 255)) -> None:
        """Displays the starting location on the screen

        Args:
            screen: The pygame screen where the start location should be drawn
            from_z: The z-coordinate to check if the start location should be displayed
            color: Color of spawn point. Defaults to blue (0, 0, 255)
        """
        if self.z == from_z:
            rotated_surf = pygame.transform.rotate(self.surf, self.angle)
            start_rect = rotated_surf.get_rect(center=(self.x, self.y))
            screen.blit(rotated_surf, start_rect)

    def rotate(self) -> None:
        """
        Rotates the spawn point image by a small increment
        """
        self.angle += 0.2


class EndLocation(Circle):
    """An end location represented as a circular object.

    Attributes:
        surf: A pygame surface for the end location image.
    """

    def __init__(self, x, y, z, radius):
        """Initializes the end location with its position and radius.

        Args:
            x: X-coordinate of the end location.
            y: Y-coordinate of the end location.
            z: Z-coordinate of the end location.
            radius: Radius of the end location.
        """
        super().__init__(x, y, z, radius)
        self.surf = pygame.image.load(
            "graphics/maze/end_location.png"
        ).convert_alpha()

    # @override
    def display(self, screen, from_z, color=(0, 0, 255)) -> None:
        """Displays the end location on the screen.

        Args:
            screen: The pygame screen to draw the end location on.
            from_z: The z-coordinate to check if the end location should be displayed
            color: Color of end location. Defaults to blue (0, 0, 255)
        """
        if self.z == from_z:
            end_rect = self.surf.get_rect(center=(self.x, self.y))
            screen.blit(self.surf, end_rect)


class Maze:
    def __init__(self, difficulty: str):
        """A maze with a specific difficulty.

        Args:
            difficulty: The difficulty of the maze

        Attributes:
            start_location: The spawn point of the player
            end_location: The end point of the maze
            obstacles: A list of obstacles in the maze
            power_ups: A list of power-up items in the maze
            hunters: A list of hunters in the maze
            difficulty: The difficulty of the maze
        """
        margin = 50
        self.start_location = StartLocation(margin, margin, 0, 25)
        self.end_location = EndLocation(
            WIDTH - margin, HEIGHT - margin, Z_LAYERS, 25)

        # generate objects inside the maze based on difficulty
        self.difficulty = difficulty
        self.obstacles: list[Sphere] = []
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

    def generate_maze_obstacles(self, num_obstacles: int, r_min: int,
                                r_max: int) -> None:
        """
        Fill up `self.obstacles` with randomized obstacles.

        Args:
            num_obstacles: Number of obstacles to generate
            r_min: Minimum radius of obstacles
            r_max: Maximum radius of obstacles
        """
        while len(self.obstacles) < num_obstacles:
            x = randint(0, WIDTH)
            y = randint(0, HEIGHT)
            z = randint(0, Z_LAYERS)
            radius = randint(r_min, r_max)
            obst = Sphere(x, y, z, radius)
            if not obst.collides_with_circle(
                    self.start_location
            ) and not obst.collides_with_circle(self.end_location):
                self.obstacles.append(obst)
                if DEBUG_MODE:
                    print(
                        f"Generated obstacle at ({x}, {y}, {z}) with radius {radius}")

    def generate_maze_items(self, num_items: int) -> None:
        """Fill up `self.power_ups` with randomized items.

        Args:
            num_items: Number of items to generate
        """
        item_types = [
            "speed_boost",
            "dash",
            "teleport",
        ]
        while len(self.power_ups) < num_items:
            x = randint(20, WIDTH - 20)
            y = randint(20, HEIGHT - 20)

            # -5 so items spawn more often on z = 0
            z = randint(-5, Z_LAYERS - 5)
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
            if DEBUG_MODE:
                print(f"Generated item: {item_type} at ({x}, {y}, {z})")

    def generate_maze_hunters(self, num_hunters: int) -> None:
        """Generate randomized hunters on the maze.

        Args:
            num_hunters: Number of hunters to generate
        """
        for _ in range(num_hunters):
            x = randint(20, WIDTH - 20)  # random location and speed
            y = randint(20, HEIGHT - 20)
            z = randint(21, Z_LAYERS)
            radius = randint(12, 18)
            speed = randint(50, 200) / 100
            hunter = Hunter(x, y, z, radius, speed)
            if DEBUG_MODE:
                print(f"Generated hunter at ({x}, {y}, {z})")
            self.hunters.append(hunter)

    def display_obstacles(self, player_z: int) -> None:
        """Displays 3D obstacles as a 2D cross-section.

        Args:
            player_z: The z-coordinate of the player to determine which
                      obstacles are visible
        """
        for obst in self.obstacles:
            obst.display(screen, player_z)

    def display_items(self, player_z: int) -> None:
        """Displays items in the maze based on player's Z-layer.

        Args:
            player_z: The z-coordinate of the player to determine which
                      items are visible
        """
        for item in self.power_ups:
            item.display(screen, player_z)

    def display_hunters(self, player: Player) -> None:
        """Displays hunters in the maze based on the player's Z-layer

        Args:
            player: Player object used to determine the visibility of hunters
        """
        for hunter in self.hunters:
            hunter.display_hunter(screen, player)

    def display_start_end(self, from_z: int) -> None:
        """Display the start and end locations of the maze

        Args:
            from_z: The z-coordinate to determine which locations are visible
        """
        self.start_location.display(screen, from_z, (255, 255, 0))
        self.end_location.display(screen, from_z, (255, 255, 0))

    def collect_items(self, player: Player) -> None:
        """Collect items that the player collides with.

        Args:
            player: The player object to check collisions and apply item effects
        """
        for item in self.power_ups:
            if item.check_collision(player):
                item.apply_effect(player, maze=self)  # Pass maze instance

    def move_hunters(self, player: Player) -> None:
        """Update the position of the hunters based on the player's position.

        Args:
            player: The player object used to update hunter movements
        """
        for hunter in self.hunters:
            hunter.handle_movement(player)

    def collide_hunters(self, player: Player) -> bool:
        """Check if the player collides with any of the hunters.

        Args:
            player: The player object to check for collisions with hunters

        Returns:
            True if the player collides with any hunter, otherwise False
        """
        for hunter in self.hunters:
            if hunter.check_collision(player):
                return True
        return False

    def is_move_allowed(self, player: Player) -> bool:
        """Check if a player can be at a certain position in the maze.

        Args:
            player: The player object to check for collisions with obstacles

        Returns:
            True if the move is allowed, otherwise False
        """
        # check collisions with obstacles
        char_circle = Circle(*player.get_parameters())
        for obst in self.obstacles:
            if obst.collides_with_circle(char_circle):
                return False

        # Check collision with map boundaries
        cx, cy, cz, r = player.get_parameters()
        if (cx < r
                or cx > WIDTH - r
                or cy < r
                or cy > HEIGHT - r
                or cz < 0
                or cz > Z_LAYERS):
            return False

        return True

    def get_start_location(self) -> StartLocation:
        """Returns the start location of the maze

        Returns:
            StartLocation: The start location of the maze
        """
        return self.start_location

    def get_end_location(self) -> EndLocation:
        """Returns the end location of the maze

        Returns:
            EndLocation: The end location of the maze
        """
        return self.end_location

    def get_power_ups(self) -> list[Item]:
        """Return a list of all power ups in the maze

        Returns:
            list[Item]: A list of power up items in the maze
        """
        return self.power_ups

    def get_hunters(self) -> list[Hunter]:
        """Return a list of all hunters in the maze

        Returns:
            list[Hunter]: A list of hunter objects in the maze
        """
        return self.hunters


class GameController:
    """Management system for the game.

    Attributes:
        temp_state: Temporary variable to track previous state
        game_state: Current state of the game
        maze: The current maze instance in the game.
        player: The current player instance in the game.
        game_events: Events in the current frame.
        leaderboard: Current leaderboard
        stopwatch: Stopwatch for the current game
        main_menu_surf: pygame surface for the main menu display
        pause_menu_surf: pygame surface for the pause menu display
    """

    def __init__(self):
        """Initializes the GameController to start a game.

        Initializes all game variables except `player` and `maze` which
        will be initialized when the difficulty is selected.
        """
        self.temp_state = "menu"  # temporary variable for exiting help menu
        self.game_state = "menu"
        self.maze = None
        self.player = None
        self.game_events = pygame.event.get()
        self.leaderboard = Leaderboard()
        self.stopwatch = Stopwatch(precision=2)

        # surfaces for display
        self.main_menu_surf = pygame.image.load(
            "graphics/main_menu.png").convert_alpha()
        self.pause_menu_surf = pygame.image.load(
            "graphics/pause_menu.png").convert_alpha()

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

    def display_playing_objects(self) -> None:
        """Display all objects on the map for when the player is in a game"""
        if self.game_state != "paused":
            self.maze.start_location.rotate()
        self.maze.display_start_end(self.player.get_z())
        self.maze.display_obstacles(self.player.get_z())
        self.maze.display_items(self.player.get_z())
        self.maze.display_hunters(self.player)
        self.player.display_player()
        self.stopwatch.display(screen)

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
                    self.temp_state = self.game_state
                    self.game_state = "help_menu"

    def perform_help_menu_frame_actions(self) -> None:
        """Performs frame actions for when the game is in the `help_menu` state."""
        # todo: implement this
        screen.fill((0, 0, 0))
        self.display_text("Help Menu - Press M to Return",
                          WIDTH // 2, HEIGHT // 2)

        for event in self.game_events:
            if event.type == pygame.KEYDOWN:
                # exit help menu, revert to previous state
                if event.key == pygame.K_m:
                    self.game_state = self.temp_state

    def perform_leaderboard_frame_actions(self) -> None:
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

    def perform_playing_frame_actions(self) -> None:
        """Performs frame actions for when the player is in a game"""
        screen.fill((0, 0, 0))

        # check player actions for pausing
        for event in self.game_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # pause game
                    self.pause_game()

        if DEBUG_MODE:
            self.run_debug()

        # handle player movement with collisions
        self.player.handle_movement(self.maze)
        self.maze.collect_items(self.player)
        self.maze.move_hunters(self.player)

        # display objects and effects
        self.display_playing_objects()
        self.display_active_effects()

        # check if we won/lost the game
        if self.check_win_condition():
            self.game_state = "winner"
            self.leaderboard.add_score(
                self.maze.difficulty, self.stopwatch.get_elapsed_time()
            )
        if self.check_lose_condition():
            self.game_state = "loser"

    def perform_paused_frame_actions(self) -> None:
        """Performs frame actions for when the game is paused"""

        # display the map as a background
        self.display_playing_objects()

        # display pause menu on top of a shaded background
        overlay_surf = pygame.Surface((screen.get_width(), screen.get_height()),
                                      pygame.SRCALPHA)
        # black with 128 alpha for background
        overlay_surf.fill((0, 0, 0, 128))
        screen.blit(overlay_surf, (0, 0))
        screen.blit(self.pause_menu_surf, (0, 0))

        # check if any of the buttons are pressed
        for event in self.game_events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if DEBUG_MODE:
                    print(x, y)
                if 416 <= x <= 735:
                    if 177 <= y <= 248:  # resume
                        self.resume_game()
                    elif 258 <= y <= 331:  # help menu
                        self.temp_state = self.game_state
                        self.game_state = "help_menu"
                    elif 341 <= y <= 414:  # restart level
                        self.restart_game()
                    elif 423 <= y <= 496:  # quit to menu
                        self.reset_game()
                if not (390 <= x <= 760 and 105 <= y <= 524):
                    self.resume_game()

    def perform_game_over_frame_actions(self) -> None:
        """Performs frame actions for when the player just lost a game."""
        screen.fill((0, 0, 0))
        self.display_text("Game Over - Press R to Restart",
                          WIDTH // 2, HEIGHT // 2)

        for event in self.game_events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()

    def perform_winner_frame_actions(self) -> None:
        """Performs frame actions for when the game is in the `winner` state."""
        screen.fill((0, 0, 0))
        self.display_text("You Won! - Click to return to Main Menu",
                          WIDTH // 2, HEIGHT // 2)

        for event in self.game_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.reset_game()

    def perform_loser_frame_actions(self) -> None:
        """Performs frame actions for when the game is in the `lost` state."""
        screen.fill((0, 0, 0))
        self.display_text(
            "You Lost the Game! - Click to return to Main Menu", WIDTH // 2, HEIGHT // 2
        )

        for event in self.game_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.reset_game()

    def run_debug(self) -> None:
        """Run debug features

        1. Create coordinate grid for easy drawing
        2. Allows for right-clicking to get mouse location
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

    def display_text(self, text, x, y, font_size=36, color=(255, 255, 255)) -> None:
        """Utility method to display text on the screen.

        Args:
            text: String to display
            x: X-coordinate of text
            y: Y-coordinate of text
            font_size: Font size of text
            color: Color of text
        """
        font = pygame.font.SysFont(None, font_size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    def display_active_effects(self) -> None:
        """Displays active effects on the screen."""
        if self.player.speed_boost_active:
            remaining = int(
                self.player.speed_boost_end_time - pygame.time.get_ticks() / 1000
            )
            self.display_text(
                f"Speed Boost Active! ({remaining}s)", 100, 50, 24, (255, 0, 0)
            )

    def check_win_condition(self) -> bool:
        """Check if the player reached the end

        Returns:
            True if the player reached the end, otherwise False
        """
        if self.player.collides_with_circle(self.maze.get_end_location()):
            print("Win condition met!")
            return True
        return False

    def check_lose_condition(self) -> bool:
        """Check if the player lost the game.

        Returns:
            True if the player lost the game by touching a hunter,
            otherwise False
        """
        if self.maze.collide_hunters(self.player):
            print("Lost condition met!")
            return True
        return False

    def restart_game(self) -> None:
        """Restart the current level"""
        self.player = Player(*self.maze.get_start_location().get_location())
        self.game_state = "playing"
        self.stopwatch.reset()
        self.stopwatch.start()
        for item in self.maze.get_power_ups():
            item.set_collected(False)
        for hunter in self.maze.get_hunters():
            hunter.reset_location()

    def reset_game(self) -> None:
        """Reset the game to initial `menu` state"""
        self.__init__()


if __name__ == "__main__":
    game = GameController()
    game.play()
