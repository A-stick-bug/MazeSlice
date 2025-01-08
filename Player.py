# Player.py

import random
import pygame
from shapes import Circle


class Player(Circle):
    def __init__(self, x, y, z, radius=10):
        super().__init__(x, y, z, radius)
        # Movement attributes
        self.z_speed = 1  # If you intend to keep vertical movement without gravity
        self.velocity = pygame.math.Vector3(0, 0, 0)
        self.acceleration = 0.5
        self.friction = 0.1
        self.max_speed = 5

        # Dash attributes
        self.is_dashing = False
        self.dash_speed = 15
        self.dash_duration = 0.2  # in seconds
        self.dash_cooldown = 1.0  # in seconds
        self.last_dash_time = -self.dash_cooldown

        # Teleport attributes
        self.is_teleporting = False
        self.teleport_cooldown = 5.0  # in seconds
        self.last_teleport_time = -self.teleport_cooldown

        # Temporary effect timers
        self.speed_boost_active = False
        self.speed_boost_end_time = 0

    def handle_movement(self, maze):
        """
        Handles player movement with collision detection, momentum, wall grabbing,
        dash, and teleport mechanics.
        """
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks() / 1000  # Current time in seconds

        # Reset acceleration
        accel = pygame.math.Vector3(0, 0, 0)

        # Movement input
        if keys[pygame.K_UP]:
            accel.y -= self.acceleration
        if keys[pygame.K_DOWN]:
            accel.y += self.acceleration
        if keys[pygame.K_LEFT]:
            accel.x -= self.acceleration
        if keys[pygame.K_RIGHT]:
            accel.x += self.acceleration

        # Apply acceleration
        self.velocity += accel

        # Apply friction
        if not accel.x:
            self.velocity.x *= (1 - self.friction)
        if not accel.y:
            self.velocity.y *= (1 - self.friction)
        if not accel.z:
            self.velocity.z *= (1 - self.friction)

        # Clamp velocity
        self.velocity.x = max(-self.max_speed,
                              min(self.velocity.x, self.max_speed))
        self.velocity.y = max(-self.max_speed,
                              min(self.velocity.y, self.max_speed))

        # Dash input
        if keys[pygame.K_SPACE]:
            if not self.is_dashing and (current_time - self.last_dash_time) >= self.dash_cooldown:
                self.is_dashing = True
                self.dash_start_time = current_time
                self.last_dash_time = current_time
                # Increase velocity for dash
                dash_vector = pygame.math.Vector3(
                    self.velocity.x, self.velocity.y, self.velocity.z)
                if dash_vector.length() != 0:
                    dash_vector = dash_vector.normalize() * self.dash_speed
                self.velocity += dash_vector
                print("Dash activated!")

        # Handle dash duration
        if self.is_dashing:
            if (current_time - self.dash_start_time) >= self.dash_duration:
                self.is_dashing = False
                # Reset velocity after dash
                if self.velocity.length() > 0:
                    self.velocity = self.velocity.normalize() * self.max_speed
                print("Dash ended.")

        # Removed gravity application
        # self.velocity.z += self.gravity  # Removed

        old_location = self.get_location()

        # Attempt to move along the X-axis
        self.x += self.velocity.x
        if not maze.is_move_allowed(self):
            self.x = old_location[0]

        # Attempt to move along the Y-axis
        self.y += self.velocity.y
        if not maze.is_move_allowed(self):
            self.y = old_location[1]

        # Attempt to move along the Z-axis (if vertical movement is desired)
        if keys[pygame.K_w]:
            self.z += self.z_speed
        if keys[pygame.K_s]:
            self.z -= self.z_speed
        if not maze.is_move_allowed(self):
            self.z = old_location[2]
            self.velocity.z = 0

        # Handle temporary effects
        self.handle_timers()

        # print("Player Position:", self.x, self.y, self.z)

    def display_player(self):
        """
        Renders the player as a circle on the screen.
        """
        from main import screen  # Importing here to avoid circular imports
        if self.is_teleporting:
            color = (255, 255, 0)  # Yellow color when teleporting
        elif self.speed_boost_active:
            color = (255, 0, 0)  # Red color when speed boost is active
        else:
            color = (255, 255, 255)  # Default white color
        pygame.draw.circle(
            screen,
            color=color,
            center=(int(self.x), int(self.y)),
            radius=self.radius
        )

    def set_position(self, x, y, z):
        """
        Updates the player's position.
        """
        self.x = x
        self.y = y
        self.z = z

    def get_location(self):
        """
        Returns the current location of the player as a tuple (x, y, z).
        """
        return self.x, self.y, self.z

    def get_parameters(self):
        """
        Returns the player's parameters needed for collision detection.
        """
        return self.x, self.y, self.z, self.radius

    def teleport(self, maze):
        '''
        Teleports player to a random position that is uncovered.
        '''
        from main import WIDTH, HEIGHT
        has_found = False

        attempts = 0
        max_attempts = 100  # Prevent infinite loop

        while not has_found and attempts < max_attempts:
            temp_x = random.randint(self.radius, WIDTH - self.radius)
            temp_y = random.randint(self.radius, HEIGHT - self.radius)
            temp_z = self.z  # Teleport to the same z_level

            if maze.is_move_allowed_pos(temp_x, temp_y, temp_z):
                has_found = True
                self.set_position(temp_x, temp_y, temp_z)
                print(f"Player teleported to ({temp_x}, {temp_y}, {temp_z})")
            attempts += 1

        if not has_found:
            print("Teleport failed: No free position found.")

    def handle_timers(self):
        """
        Handle timers for temporary effects like speed boost.
        """
        current_time = pygame.time.get_ticks() / 1000
        if self.speed_boost_active and current_time >= self.speed_boost_end_time:
            self.max_speed -= 2  # Revert max_speed
            self.speed_boost_active = False
            print("Speed boost ended.")

    def apply_speed_boost(self, duration=5.0):
        """
        Applies a speed boost to the player for a specified duration.
        """
        self.max_speed += 2  # Increase max_speed
        self.speed_boost_active = True
        self.speed_boost_end_time = pygame.time.get_ticks() / 1000 + duration
        print("Speed boost activated!")

    def reduce_dash_cooldown(self):
        """
        Reduces the dash cooldown period.
        """
        self.dash_cooldown = max(0.5, self.dash_cooldown - 0.1)
        print(f"Dash cooldown reduced to {self.dash_cooldown} seconds.")

    def reduce_teleport_cooldown(self):
        """
        Reduces the teleport cooldown period.
        """
        self.teleport_cooldown = max(2.0, self.teleport_cooldown - 0.5)
        print(
            f"Teleport cooldown reduced to {self.teleport_cooldown} seconds.")
