# Player.py

import random
import pygame
from shapes import Circle

class Player(Circle):
    def __init__(self, x, y, z, radius=10):
        super().__init__(x, y, z, radius)
        # Movement attributes
        self.speed = 5
        self.z_speed = 1
        self.velocity = pygame.math.Vector3(0, 0, 0)
        self.acceleration = 0.5
        self.friction = 0.1
        self.max_speed = 5
        self.max_z_speed = 3
        self.gravity = -0.5
        self.is_jumping = False
        self.is_on_wall = False

        # Dash attributes
        self.is_dashing = False
        self.dash_speed = 15
        self.dash_duration = 0.2  # in seconds
        self.dash_cooldown = 1.0  # in seconds
        self.last_dash_time = -self.dash_cooldown

        # Stealth attributes
        self.is_stealth = False
        self.stealth_speed_multiplier = 0.5
        self.stealth_duration = 3.0  # in seconds
        self.stealth_cooldown = 5.0  # in seconds
        self.last_stealth_time = -self.stealth_cooldown

        # Temporary effect timers
        self.speed_boost_active = False
        self.speed_boost_end_time = 0

    def handle_movement(self, maze):
        """
        Handles player movement with collision detection, momentum, wall grabbing,
        dash, and stealth mechanics.
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
        if keys[pygame.K_w]:
            accel.z += self.acceleration
        if keys[pygame.K_s]:
            accel.z -= self.acceleration

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
        self.velocity.x = max(-self.max_speed, min(self.velocity.x, self.max_speed))
        self.velocity.y = max(-self.max_speed, min(self.velocity.y, self.max_speed))
        self.velocity.z = max(-self.max_z_speed, min(self.velocity.z, self.max_z_speed))

        # Dash input
        if keys[pygame.K_SPACE]:
            if not self.is_dashing and (current_time - self.last_dash_time) >= self.dash_cooldown:
                self.is_dashing = True
                self.dash_start_time = current_time
                self.last_dash_time = current_time
                # Increase velocity for dash
                dash_vector = pygame.math.Vector3(self.velocity.x, self.velocity.y, self.velocity.z)
                if dash_vector.length() != 0:
                    dash_vector = dash_vector.normalize() * self.dash_speed
                self.velocity += dash_vector
                print("Dash activated!")

        # Stealth input
        if keys[pygame.K_LSHIFT]:
            if not self.is_stealth and (current_time - self.last_stealth_time) >= self.stealth_cooldown:
                self.is_stealth = True
                self.stealth_start_time = current_time
                self.last_stealth_time = current_time
                # Reduce speed
                self.max_speed *= self.stealth_speed_multiplier
                self.velocity *= self.stealth_speed_multiplier
                print("Stealth mode activated!")

        # Handle dash duration
        if self.is_dashing:
            if (current_time - self.dash_start_time) >= self.dash_duration:
                self.is_dashing = False
                # Reset velocity after dash
                if self.velocity.length() > 0:
                    self.velocity = self.velocity.normalize() * self.max_speed
                print("Dash ended.")

        # Handle stealth duration
        if self.is_stealth:
            if (current_time - self.stealth_start_time) >= self.stealth_duration:
                self.is_stealth = False
                # Restore velocity after stealth
                if self.velocity.length() > 0:
                    self.velocity = self.velocity.normalize() / self.stealth_speed_multiplier
                    self.velocity *= self.max_speed
                print("Stealth mode ended.")

        # Apply gravity
        self.velocity.z += self.gravity
        if self.velocity.z < -self.max_z_speed:
            self.velocity.z = -self.max_z_speed

        old_location = self.get_location()

        # Attempt to move along the X-axis
        self.x += self.velocity.x
        if not maze.is_move_allowed(self):
            self.x = old_location[0]
            self.is_on_wall = True
        else:
            self.is_on_wall = False

        # Attempt to move along the Y-axis
        self.y += self.velocity.y
        if not maze.is_move_allowed(self):
            self.y = old_location[1]
            self.is_on_wall = True
        else:
            self.is_on_wall = False

        # Attempt to move along the Z-axis
        self.z += self.velocity.z
        if not maze.is_move_allowed(self):
            self.z = old_location[2]
            self.velocity.z = 0
            self.is_jumping = False
        else:
            self.is_jumping = True

        # Wall grabbing (allow sliding along walls if on_wall)
        if self.is_on_wall:
            # Reduce horizontal velocity when on wall
            self.velocity.x *= 0.5
            self.velocity.y *= 0.5

        # Ensure Z-layer boundaries
        if self.z < 0:
            self.z = 0
            self.velocity.z = 0
            self.is_jumping = False
        elif self.z > maze.Z_LAYERS:
            self.z = maze.Z_LAYERS
            self.velocity.z = 0
            self.is_jumping = False

        # Handle temporary effects
        self.handle_timers()

       # print("Player Position:", self.x, self.y, self.z)

    def display_player(self):
        """
        Renders the player as a circle on the screen.
        """
        from main import screen  # Importing here to avoid circular imports
        if self.is_stealth:
            color = (0, 255, 0)  # Green color when in stealth
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

    def check_teleport(self, location, maze):
        '''
        Attempts a teleport of the Player to a random spot (location) that is not covered.
        '''
        if location[2] != self.z:
            return False

        temp_pos = self.get_location()

        self.set_position(*location)
        is_possible = maze.is_move_allowed(self)
        self.set_position(*temp_pos)
        return is_possible

    def teleport(self, maze):
        '''
        Teleports player to random position that is uncovered.
        '''
        from main import WIDTH, HEIGHT
        has_found = False

        while not has_found:
            temp_x = random.randint(self.radius, WIDTH - self.radius)
            temp_y = random.randint(self.radius, HEIGHT - self.radius)
            if self.check_teleport((temp_x, temp_y, self.z), maze):
                has_found = True
                self.set_position(temp_x, temp_y, self.z)

    def handle_timers(self):
        """
        Handle timers for temporary effects like speed boost.
        """
        current_time = pygame.time.get_ticks() / 1000
        if self.speed_boost_active and current_time >= self.speed_boost_end_time:
            self.max_speed -= 2  # Revert max_speed
            self.speed_boost_active = False
            print("Speed boost ended.")
