# shapes.py

import pygame
from math import dist


class Circle:
    """
    Represents a circle in 3D space.

    Attributes:
        x (float): The x-coordinate of the circle's center.
        y (float): The y-coordinate of the circle's center.
        z (int): The z-coordinate (layer) of the circle.
        radius (int): The radius of the circle.
    """

    def __init__(self, x, y, z, radius):
        """
        Initializes the Circle instance with position and radius.

        Args:
            x (float): The x-coordinate of the circle's center.
            y (float): The y-coordinate of the circle's center.
            z (int): The z-coordinate (layer) of the circle.
            radius (int): The radius of the circle.
        """
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

    def collides_with_circle(self, other) -> bool:
        """
        Determines whether this circle collides with another circle.

        Collision is based on overlapping planar distances on the same z-layer.

        Args:
            other (Circle): Another circle to check collision against.

        Returns:
            bool: True if the circles collide, False otherwise.
        """
        if other.get_z() - self.z != 0:
            return False
        planar_dist = dist((other.get_x(), other.get_y()), (self.x, self.y))
        return planar_dist < self.radius + other.radius

    def display(self, screen, from_z, color=(0, 0, 255)) -> None:
        """
        Renders the circle on the given Pygame screen if it's on the same z-layer.

        Args:
            screen (pygame.Surface): The Pygame surface to draw the circle on.
            from_z (int): The current viewing z-layer.
            color (tuple, optional): RGB color of the circle. Defaults to blue (0, 0, 255).
        """
        if self.get_z() == from_z:
            pygame.draw.circle(
                surface=screen,
                color=color,
                center=(self.x, self.y),
                radius=self.radius,
            )

    def get_parameters(self) -> tuple[float, float, int, int]:
        """
        Retrieves the circle's parameters.

        Returns:
            tuple: A tuple containing (x, y, z, radius).
        """
        return self.x, self.y, self.z, self.radius

    def get_location(self) -> tuple[float, float, int]:
        """
        Retrieves the circle's current location.

        Returns:
            tuple: A tuple containing (x, y, z).
        """
        return self.x, self.y, self.z

    def get_x(self) -> float:
        """
        Retrieves the x-coordinate of the circle's center.

        Returns:
            float: The x-coordinate.
        """
        return self.x

    def get_y(self) -> float:
        """
        Retrieves the y-coordinate of the circle's center.

        Returns:
            float: The y-coordinate.
        """
        return self.y

    def get_z(self) -> int:
        """
        Retrieves the z-coordinate (layer) of the circle.

        Returns:
            int: The z-coordinate.
        """
        return self.z

    def get_radius(self) -> int:
        """
        Retrieves the radius of the circle.

        Returns:
            int: The radius.
        """
        return self.radius

    def __iter__(self):
        """
        Allows iteration over the circle's parameters.

        Yields:
            float/int: The x, y, z, and radius of the circle in order.
        """
        return iter(self.get_parameters())


class Sphere(Circle):
    """
    Represents a sphere in 3D space, extending the Circle class with 3D-specific behaviors.

    Attributes:
        Inherits all attributes from the Circle class.
    """

    def __init__(self, x, y, z, radius):
        """
        Initializes the Sphere instance with position and radius.

        Args:
            x (float): The x-coordinate of the sphere's center.
            y (float): The y-coordinate of the sphere's center.
            z (int): The z-coordinate (layer) of the sphere.
            radius (int): The radius of the sphere.
        """
        super().__init__(x, y, z, radius)

    def get_cross_section_radius(self, radius_3d, z_distance) -> float:
        """
        Calculates the apparent radius of the sphere's cross-section based on its z-distance.

        Args:
            radius_3d (int): The actual radius of the sphere.
            z_distance (float): The absolute distance in the z-axis from the viewing layer.

        Returns:
            float: The radius of the visible cross-section. Returns 0 if the sphere is too far.
        """
        if z_distance >= radius_3d:  # Too far to appear
            return 0
        return (radius_3d ** 2 - z_distance ** 2) ** 0.5

    def display(self, screen, from_z, color=(0, 0, 255)) -> None:
        """
        Renders the sphere as a projected circle on the given Pygame screen based on z-distance.

        Additionally draws a semi-transparent shadow to represent depth.

        Args:
            screen (pygame.Surface): The Pygame surface to draw the sphere on.
            from_z (int): The current viewing z-layer.
            color (tuple, optional): RGB color of the sphere. Defaults to blue (0, 0, 255).
        """
        z_distance = abs(self.z - from_z)
        circle_radius = self.get_cross_section_radius(self.radius, z_distance)
        if circle_radius > 0:  # visible obstacle
            pygame.draw.circle(
                surface=screen,
                color=color,
                center=(self.x, self.y),
                radius=int(circle_radius),
            )
        # Draw shadow of obstacle
        shadow_z_distance = max(0, abs(self.z - from_z) - 10)
        shadow_circle_radius = self.get_cross_section_radius(self.radius, shadow_z_distance)
        if shadow_circle_radius > 0:
            # Surface for transparency
            transparent_surface = pygame.Surface(
                (self.radius * 2, self.radius * 2),
                pygame.SRCALPHA
            )
            # Draw on transparent surface
            pygame.draw.circle(
                surface=transparent_surface,
                color=(0, 0, 255, 128),  # Blue color with 50% transparency (alpha = 128)
                center=(self.radius, self.radius),
                radius=shadow_circle_radius
            )

            # Blit the transparent surface onto the main screen
            screen.blit(transparent_surface, (self.x - self.radius, self.y - self.radius))

    def collides_with_circle(self, other) -> bool:
        """
        Determines whether this sphere collides with another circle, considering 3D distance.

        Args:
            other (Circle or Item): Another circle to check collision against.

        Returns:
            bool: True if the sphere collides with the circle, False otherwise.
        """
        z_dist = abs(other.z - self.z)
        proj_rad = self.get_cross_section_radius(self.radius, z_dist)
        if proj_rad == 0:  # Does not appear in cross-section
            return False
        planar_dist = dist((other.x, other.y), (self.x, self.y))
        return planar_dist < proj_rad + other.radius


class Cylinder:
    """Represents a cylinder in 3D space using a stack of circles."""

    def __init__(self, x: float, y: float, start_z: int, end_z: int, radius: int):
        """Initializes the Cylinder instance with position, z-range, and radius.

        Args:
            x: The x-coordinate of the cylinder's center.
            y: The y-coordinate of the cylinder's center.
            start_z: The starting z-coordinate (layer) of the cylinder.
            end_z: The ending z-coordinate (layer) of the cylinder.
            radius: The radius of the cylinder.
        """
        self.x = x
        self.y = y
        self.start_z = start_z
        self.end_z = end_z
        self.radius = radius

    def display(self, screen, from_z) -> None:
        """Renders the cylinder on the given Pygame screen if the viewing layer is within its z-range.

        Args:
            screen (pygame.Surface): The Pygame surface to draw the cylinder on.
            from_z (int): The current viewing z-layer.
        """
        if self.start_z <= from_z <= self.end_z:
            pygame.draw.circle(
                surface=screen,
                color=(255, 215, 0),  # Gold color for items
                center=(self.x, self.y),
                radius=int(self.radius),
            )

    def collides_with_circle(self, other: Circle) -> bool:
        """Determines whether this cylinder collides with another circle.

        Collision is based on the circle being within the cylinder's z-range and overlapping planar distances.

        Args:
            other: A circle to check collision against.

        Returns True if the cylinder collides with the circle, False otherwise.
        """
        # Check if the other circle's z is within the cylinder's range
        if not (self.start_z <= other.get_z() <= self.end_z):
            return False
        planar_dist = dist((other.get_x(), other.get_y()), (self.x, self.y))
        return planar_dist < self.radius + other.radius

    def get_parameters(self) -> tuple[float, float, int, int, int]:
        """Retrieves the cylinder's parameters.

        Returns a tuple containing (x, y, start_z, end_z, radius).
        """
        return self.x, self.y, self.start_z, self.end_z, self.radius

    def get_location(self) -> tuple[float, float, int, int]:
        """Retrieves the cylinder's current location and z-range.

        Returns a tuple containing (x, y, start_z, end_z).
        """
        return self.get_parameters()[4:]
