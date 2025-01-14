# hunter.py

from math import dist
from random import random
import pygame

from shapes import Circle
from player import Player


class Hunter(Circle):
    """represents a hunter which moves towards the player and kills them."""

    def __init__(self, x, y, z: int, radius, speed=0.0, color=(255, 119, 0)):
        super().__init__(x, y, z, radius)
        self.speed = speed
        self.color = color
        self.initial_location = (x, y, z)

    def z_distance_from_player(self, player: Player) -> int:
        return abs(self.z - player.z)

    def handle_movement(self, player: Player) -> None:
        """handles the movement of the hunter based on where the player is."""
        # maybe just let hunter move freely through obstacles
        if self.z_distance_from_player(player) <= 20:
            player_location = player.get_location()[:2]
            cur_location = (self.x, self.y)
            distance_from_player = dist(player_location, cur_location)
            movement_scalar = self.speed / distance_from_player
            self.x += (player.get_x() - self.x) * movement_scalar
            self.y += (player.get_y() - self.y) * movement_scalar
            if self.z > player.z:
                if random() > self.speed / 5:
                    self.z -= 1
            elif self.z < player.z:
                if random() > self.speed / 5:
                    self.z += 1
            # separate z movement from xy, and cheap non integral speed implementation

    def set_location(self, location) -> None:
        self.x, self.y, self.z = location

    def reset_location(self):
        self.set_location(self.initial_location)

    def display_hunter(self, screen, player: Player) -> None:
        """
        displays the hunter on the screen.
        """
        z_distance_from_player = self.z_distance_from_player(player)
        if z_distance_from_player == 0:
            pygame.draw.circle(
                screen,
                color=self.color,
                center=(int(self.x), int(self.y)),
                radius=self.radius
            )
        elif z_distance_from_player < 20:
            # surface for transparency
            alpha = 224 - 2 * z_distance_from_player
            transparent_surface = pygame.Surface(
                (self.radius * 2, self.radius * 2),
                pygame.SRCALPHA
            )
            # draw on transparent surface
            pygame.draw.circle(
                surface=transparent_surface,
                # Blue color with 50% transparency (alpha = 128)
                color=(*self.color, alpha),
                center=(self.radius, self.radius),
                radius=self.radius
            )

            # blit the transparent surface onto the main screen
            screen.blit(transparent_surface, (self.x -
                                              self.radius, self.y - self.radius))

    def check_collision(self, player: Player) -> bool:
        """
        Checks collision with the player. If collision occurs, the player is xooked. End the game.
        """
        if super().collides_with_circle(player):
            from main import DEBUG_MODE
            if DEBUG_MODE:
                print(
                    f"Player collided with hunter at ({self.x}, {self.y}, {self.z})")
            return True

        return False
