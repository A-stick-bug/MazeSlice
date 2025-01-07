# item.py

import pygame
from shapes import Cylinder

class Item(Cylinder):
    """
    Represents an item within the maze that the player can collect.
    """

    def __init__(self, x, y, start_z, end_z, radius, item_type, color=(255, 215, 0)):
        """
        Initializes the Item with position, size, type, and color.

        :param x: X-coordinate
        :param y: Y-coordinate
        :param start_z: Starting Z-layer
        :param end_z: Ending Z-layer
        :param radius: Radius of the item
        :param item_type: Type of the item (e.g., 'speed_boost', 'dash', 'stealth')
        :param color: Color of the item for rendering
        """
        super().__init__(x, y, start_z, end_z, radius)
        self.type = item_type
        self.color = color
        self.collected = False  # Flag to check if the item has been collected

    @property
    def z(self):
        """
        Returns the midpoint Z-coordinate of the item.
        """
        return (self.start_z + self.end_z) / 2

    def get_type(self):
        """
        Returns the type of the item.
        """
        return self.type

    def display_item(self, screen, player_z):
        """
        Displays the item on the screen if it is within the visible Z-layer.
        Changes color if collected.
        """
        if not self.collected:
            z_distance = abs(self.z - player_z)
            circle_radius = self.get_cross_section_radius(self.radius, z_distance)
            if circle_radius > 0:
                pygame.draw.circle(
                    surface=screen,
                    color=self.color,
                    center=(self.x, self.y),
                    radius=int(circle_radius)
                )

    def check_collision(self, player):
        """
        Checks collision with the player. If collision occurs, mark as collected.

        :param player: Instance of the Player class
        """
        if self.collected:
            return False

        # Check if player is within the item's Z-layer
        if not (self.start_z <= player.z <= self.end_z):
            return False

        # Calculate planar distance
        planar_dist = pygame.math.Vector2(self.x - player.x, self.y - player.y).length()
        if planar_dist < (self.radius + player.radius):
            self.collected = True
            print(f"Item collected: {self.type} at ({self.x}, {self.y}, {self.z})")
            return True
        return False

    def apply_effect(self, player):
        """
        Applies the item's effect to the player based on its type.

        :param player: Instance of the Player class
        """
        if not self.collected:
            return

        if self.type == 'speed_boost':
            player.apply_speed_boost()
            # The Player class handles reverting the speed after a duration
        elif self.type == 'dash':
            player.dash_cooldown = max(0.5, player.dash_cooldown - 0.1)
            print("Dash cooldown reduced!")
            # Reduces the cooldown period for dashing
        elif self.type == 'stealth':
            player.stealth_cooldown = max(2.0, player.stealth_cooldown - 0.5)
            print("Stealth cooldown reduced!")
            # Reduces the cooldown period for stealth mode
        # Add more item types and their effects as needed
