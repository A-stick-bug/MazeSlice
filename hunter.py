# hunter.py

from math import dist
from random import random
import pygame

from shapes import Circle
from player import Player


class Hunter(Circle):
    """Represents a hunter which moves towards the player and kills them.

    Attributes:
        initial_location (tuple[float, float, int]): Initial location of the hunter.
    """

    def __init__(
        self, x: float, y: float, z: int, radius: int, speed=0.0, color=(255, 119, 0)
    ):
        """Initializes a hunter with its position, radius, speed and color.

        Args:
            x: X-coordinate of the hunter.
            y: Y-coordinate of the hunter.
            z: Z-coordinate of the hunter.
            radius: Radius of the hunter.
            speed: Speed of the hunter.
            color: Color of the hunter, default is #FF7700.
        """
        super().__init__(x, y, z, radius)
        self.speed = speed
        self.color = color
        self.initial_location = (x, y, z)

    def z_distance_from_player(self, player: Player) -> int:
        """Returns the difference between the hunter and the player's
        respective Z-coordinates."""
        return abs(self.z - player.z)

    def handle_movement(self, player: Player) -> None:
        """Handles the movement of the hunter based on where the player is."""
        # Hunter moves only if they are displayed on the screen.
        if self.z_distance_from_player(player) <= 20:
            player_location = player.get_location()[:2]
            cur_location = (self.x, self.y)
            distance_from_player = dist(player_location, cur_location)
            movement_scalar = self.speed / distance_from_player
            self.x += (player.get_x() - self.x) * movement_scalar
            self.y += (player.get_y() - self.y) * movement_scalar

            # Separate z movement from xy, and cheap non integral speed implementation.
            if self.z > player.z:
                if random() > self.speed / 5:
                    self.z -= 1
            elif self.z < player.z:
                if random() > self.speed / 5:
                    self.z += 1

    def set_location(self, location: tuple[float, float, int]) -> None:
        """Sets the hunter's location."""
        self.x, self.y, self.z = location

    def reset_location(self) -> None:
        """Resets the location of the hunter."""
        self.set_location(self.initial_location)

    def display_hunter(self, screen: pygame.Surface, player: Player) -> None:
        """Displays the hunter on the screen.

        Args:
            screen: The pygame screen where the hunter should be drawn
            player: The player.
        """
        # Checks for difference of Z-coordinate from the player.
        z_distance_from_player = self.z_distance_from_player(player)
        if z_distance_from_player == 0:
            pygame.draw.circle(
                screen,
                color=self.color,
                center=(int(self.x), int(self.y)),
                radius=self.radius,
            )

        # Fades out if not on the same Z-level as player.
        elif z_distance_from_player < 20:
            # Surface for transparency
            alpha = 224 - 2 * z_distance_from_player
            transparent_surface = pygame.Surface(
                (self.radius * 2, self.radius * 2), pygame.SRCALPHA
            )

            # Draw on transparent surface
            pygame.draw.circle(
                surface=transparent_surface,
                # Blue color with 50% transparency (alpha = 128)
                color=(*self.color, alpha),
                center=(self.radius, self.radius),
                radius=self.radius,
            )

            # Blit the transparent surface onto the main screen
            screen.blit(
                transparent_surface, (self.x - self.radius, self.y - self.radius)
            )

    def check_collision(self, player: Player) -> bool:
        """Checks collision with the player. If collision occurs, end the game.
        
        Returns True if collides with player and False otherwise.
        """
        if super().collides_with_circle(player):
            from main import DEBUG_MODE

            if DEBUG_MODE:
                print(f"Player collided with hunter at ({self.x}, {self.y}, {self.z})")
            return True

        return False
