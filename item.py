# item.py

import pygame
from shapes import Cylinder


class Item(Cylinder):
    """
    Represents an item within the maze that the player can collect.
    """

    def __init__(self, x, y, start_z, end_z, radius, type: str):
        """
        Initializes the Item with position, size, type, and color.

        :param x: X-coordinate
        :param y: Y-coordinate
        :param start_z: Starting Z-layer
        :param end_z: Ending Z-layer
        :param radius: Radius of the item
        :param type: Type of the item (e.g., 'speed_boost', 'dash', 'teleport')
        :param color: Color of the item for rendering
        """
        super().__init__(x, y, start_z, end_z, radius)
        self.type = type
        self.color = self.get_color_by_type()
        self.collected = False  # Flag to check if the item has been collected

    @property
    def z(self):
        """
        Returns the midpoint Z-coordinate of the item.
        """
        return (self.start_z + self.end_z) / 2

    def get_type(self) -> str:
        """
        Returns the type of the item.
        """
        return self.type

    def get_color(self):
        """
        Returns the color of the item.
        """
        return self.color

    def get_color_by_type(self):
        """Returns color based on item type."""
        colors = {
            "speed_boost": (255, 0, 0),  # Red
            "dash": (0, 255, 0),  # Green
            "teleport": (128, 0, 128),  # Purple
        }
        return colors.get(self.type, (255, 255, 255))  # Default white

    def display(self, screen, player_z) -> None:
        """
        Displays the item on the screen if it is within the visible Z-layer.
        Changes color if collected.
        """
        if not self.collected and self.start_z <= player_z <= self.end_z:
            pygame.draw.circle(
                surface=screen,
                color=self.color,
                center=(self.x, self.y),
                radius=int(self.radius),
            )

    def check_collision(self, player) -> bool:
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
            from main import DEBUG_MODE

            if DEBUG_MODE:
                print(f"Item collected: {self.type} at ({self.x}, {self.y}, {self.z})")
            return True
        return False

    def apply_effect(self, player, maze) -> None:
        """
        Applies the item's effect to the player based on its type.

        :param player: Instance of the Player class
        :param maze: Instance of the Maze class
        """
        if not self.collected:
            return

        DEBUG = __import__("main").DEBUG_MODE
        if self.type == "speed_boost":
            player.apply_speed_boost()
            if DEBUG:
                print("Speed boost applied!")
            # The Player class handles reverting the speed after a duration
        elif self.type == "dash":
            player.reduce_dash_cooldown()
            if DEBUG:
                print("Dash cooldown reduced!")
            # Reduces the cooldown period for dashing
        elif self.type == "teleport":
            player.teleport(maze)
            if DEBUG:
                print("Teleport activated!")
            # Teleports the player to a random free spot
        # Add more item types and their effects as needed

    def set_collected(self, val) -> None:
        self.collected = val
