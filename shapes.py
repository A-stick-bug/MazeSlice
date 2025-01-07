# shapes.py

import pygame
from math import dist


class Circle:
    """Represents a circle in 3D space"""

    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

    def collides_with_circle(self, other):
        """Check if this sphere collides with a circle."""
        if other.get_z() - self.z != 0:
            return False
        planar_dist = dist((other.get_x(), other.get_y()), (self.x, self.y))
        return planar_dist < self.radius + other.radius

    def display(self, screen, from_z):
        """Display circle only if it is on the same layer as what we are viewing from."""
        if self.get_z() == from_z:
            pygame.draw.circle(
                surface=screen,
                color=(0, 0, 255),  # Blue color for obstacles
                center=(self.x, self.y),
                radius=self.radius,
            )

    def get_parameters(self):
        return self.x, self.y, self.z, self.radius

    def get_location(self):
        return self.x, self.y, self.z

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_z(self):
        return self.z

    def get_radius(self):
        return self.radius

    def __iter__(self):
        return iter(self.get_parameters())


class Sphere(Circle):
    """Represents a sphere in 3D space"""

    def __init__(self, x, y, z, radius):
        super().__init__(x, y, z, radius)

    def get_cross_section_radius(self, radius_3d, z_distance):
        """Calculates the apparent size of a sphere based on its distance in the Z dimension."""
        if z_distance >= radius_3d:  # Too far to appear
            return 0
        return (radius_3d ** 2 - z_distance ** 2) ** 0.5

    def display(self, screen, from_z):
        """Display the sphere as a projection onto a cross-section, size is determined by the distance in the Z dimension."""
        z_distance = abs(self.z - from_z)
        circle_radius = self.get_cross_section_radius(self.radius, z_distance)
        if circle_radius > 0:  # visible obstacle
            pygame.draw.circle(
                surface=screen,
                color=(0, 0, 255),  # Blue color for obstacles
                center=(self.x, self.y),
                radius=int(circle_radius),
            )
        # draw shadow of obstacle
        shadow_z_distance = max(0, abs(self.z - from_z) - 10)
        shadow_circle_radius = self.get_cross_section_radius(self.radius, shadow_z_distance)
        if shadow_circle_radius > 0:
            # surface for transparency
            transparent_surface = pygame.Surface(
                (self.radius * 2, self.radius * 2),
                pygame.SRCALPHA
            )
            # draw on transparent surface
            pygame.draw.circle(
                surface=transparent_surface,
                color=(0, 0, 255, 128),  # Blue color with 50% transparency (alpha = 128)
                center=(self.radius, self.radius),
                radius=shadow_circle_radius
            )

            # blit the transparent surface onto the main screen
            screen.blit(transparent_surface, (self.x - self.radius, self.y - self.radius))

    def collides_with_circle(self, other):
        """Check if this sphere collides with a circle."""
        z_dist = abs(other.z - self.z)
        proj_rad = self.get_cross_section_radius(self.radius, z_dist)
        if proj_rad == 0:  # Does not appear in cross-section
            return False
        planar_dist = dist((other.x, other.y), (self.x, self.y))
        return planar_dist < proj_rad + other.radius


class Cylinder:
    """Represents a cylinder in 3D space using a stack of circles."""

    def __init__(self, x, y, start_z, end_z, radius):
        """Creates a cylinder ranging from start_z to end_z inclusive."""
        self.x = x
        self.y = y
        self.start_z = start_z
        self.end_z = end_z
        self.radius = radius

    def get_cross_section_radius(self, radius_3d, z_distance):
        """Calculates the apparent size of a cylinder's cross-section based on distance in Z."""
        if z_distance >= radius_3d:  # Too far to appear
            return 0
        return (radius_3d ** 2 - z_distance ** 2) ** 0.5

    def display(self, screen, from_z):
        """Display the cylinder if the player is within its Z range."""
        if self.start_z <= from_z <= self.end_z:
            pygame.draw.circle(
                surface=screen,
                color=(255, 215, 0),  # Gold color for items
                center=(self.x, self.y),
                radius=int(self.radius),
            )

    def collides_with_circle(self, other):
        """Check if this cylinder collides with a circle."""
        # Check if the other circle's z is within the cylinder's range
        if not (self.start_z <= other.get_z() <= self.end_z):
            return False
        planar_dist = dist((other.get_x(), other.get_y()), (self.x, self.y))
        return planar_dist < self.radius + other.radius

    def get_parameters(self):
        return self.x, self.y, self.start_z, self.end_z, self.radius

    def get_location(self):
        return self.x, self.y, self.start_z, self.end_z

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_start_z(self):
        return self.start_z

    def get_end_z(self):
        return self.end_z

    def get_radius(self):
        return self.radius

    def __iter__(self):
        return iter(self.get_parameters())
