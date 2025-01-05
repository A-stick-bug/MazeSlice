import pygame

from math import dist


class Sphere:
    """Represents a sphere in 3D space"""

    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

    def get_cross_section_radius(self, radius_3d, z_distance):
        """Calculates the apparent size of a sphere based on its distance in
        the Z dimension"""
        if z_distance >= radius_3d:  # too far to appear
            return 0
        return (radius_3d ** 2 - z_distance ** 2) ** 0.5

    def display(self, screen, from_z):
        """Display the sphere as a projection onto a cross-section, size
        is determined by the distance in the Z dimension"""
        z_distance = abs(self.z - from_z)
        circle_radius = self.get_cross_section_radius(self.radius, z_distance)
        pygame.draw.circle(
            surface=screen,
            color=(0, 0, 255),
            center=(self.x, self.y),
            radius=circle_radius,
        )

    def collides_with_circle(self, other):
        """Check if this sphere collides with a circle"""
        z_dist = abs(other.get_z() - self.z)
        proj_rad = self.get_cross_section_radius(self.radius, z_dist)
        if proj_rad == 0:  # does not appear in cross-section
            return False
        planar_dist = dist((other.get_x(), other.get_y()), (self.x, self.y))
        return planar_dist < proj_rad + other.get_radius()

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


class Circle(Sphere):
    """Represents a circle in 3D space, as a sphere with thickness of 1"""

    def __init__(self, x, y, z, radius):
        super().__init__(x, y, z, radius)

    # @override
    def display(self, screen, from_z):
        """Display circle only if it is on the same layer as what we are
        viewing from"""
        if self.get_z() == from_z:
            super().display(screen, from_z)


class Cylinder:
    """Represents a cylinder in 3D space using a stack of circles"""
    ...
