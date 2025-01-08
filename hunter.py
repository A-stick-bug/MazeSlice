# hunter.py

from math import dist
from random import random
import pygame

from shapes import Circle
from Player import Player


class Hunter(Circle):
    """"""
    
    def __init__(self, x, y, z: int, radius, speed=0.0, color=(255, 119, 0)):
        super().__init__(x, y, z, radius)
        self.speed = speed
        self.color = color

    def z_distance_from_player(self, player: Player):
        return abs(self.z - player.get_z())

    def handle_movement(self, player: Player) -> None:
        """"""
        # maybe just let hunter move freely through obstacles
        if self.z_distance_from_player(player) <= 20:
            player_location = player.get_location()[:2]
            cur_location = (self.x, self.y)
            distance_from_player = dist(player_location, cur_location)
            movement_scalar = self.speed / distance_from_player
            self.x += (player.get_x() - self.x) * movement_scalar
            self.y += (player.get_y() - self.y) * movement_scalar
            if self.z > player.get_z():
                if random() > self.speed / 10:
                    self.z -= 1
            elif self.z < player.get_z():
                if random() > self.speed / 10:
                    self.z += 1
            # separate z movement from xy, and cheap non integral speed implementation

    def display_hunter(self, screen, player: Player):
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
                color=(*self.color, alpha),  # Blue color with 50% transparency (alpha = 128)
                center=(self.radius, self.radius),
                radius=self.radius
            )

            # blit the transparent surface onto the main screen
            screen.blit(transparent_surface, (self.x - self.radius, self.y - self.radius))
