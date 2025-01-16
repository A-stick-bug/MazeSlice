# player.py

import random
import pygame
import math

from shapes import Circle

EXPERIMENTAL_SLIDING = True


class Player(Circle):
    """
    Represents the player, handling movement, actions, and temporary effects.
    Inherits from the `Circle` class.
    """

    def __init__(self, x, y, z, radius=18):
        """
        Initialize player with position, movement, and action cooldowns.

        Args:
            x (float): Player's x-coordinate.
            y (float): Player's y-coordinate.
            z (float): Player's z-coordinate.
            radius (int, optional): Player's radius. Defaults to 18.
        """
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
        self.teleport_end_time = 0  # Initialize teleport end time

        # Temporary effect timers
        self.speed_boost_active = False
        self.speed_boost_end_time = 0

        # Load and scale the player images
        try:
            # Default sprite
            self.original_surf = pygame.image.load("graphics/player/linty.png").convert_alpha()
            self.original_surf = pygame.transform.scale(self.original_surf, (self.radius * 2, self.radius * 2))

            # Dash sprite
            self.dash_surf = pygame.image.load("graphics/player/lintydash.png").convert_alpha()
            self.dash_surf = pygame.transform.scale(self.dash_surf, (self.radius * 2, self.radius * 2))

            # Teleport sprite
            self.teleport_surf = pygame.image.load("graphics/player/lintyteleport.png").convert_alpha()
            self.teleport_surf = pygame.transform.scale(self.teleport_surf, (self.radius * 2, self.radius * 2))

            # Set the current sprite to the default
            self.current_surf = self.original_surf
        except pygame.error as e:
            from main import DEBUG_MODE
            if DEBUG_MODE:
                print(f"Failed to load player images: {e}")
            self.current_surf = None  # Fallback if image loading fails

    def handle_movement(self, maze):
        """
        Manage player movement, collisions, dashing, and teleporting.

        Args:
            maze (Maze): Maze object for collision checks.
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

        # Clamp velocity to max speed
        self.velocity.x = max(-self.max_speed, min(self.velocity.x, self.max_speed))
        self.velocity.y = max(-self.max_speed, min(self.velocity.y, self.max_speed))

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
                from main import DEBUG_MODE
                if DEBUG_MODE:
                    print("Dash activated!")

        # Handle dash duration
        if self.is_dashing:
            if (current_time - self.dash_start_time) >= self.dash_duration:
                self.is_dashing = False
                # Reset velocity after dash
                if self.velocity.length() > 0:
                    self.velocity = self.velocity.normalize() * self.max_speed
                from main import DEBUG_MODE
                if DEBUG_MODE:
                    print("Dash ended.")

        # Removed gravity application
        # self.velocity.z += self.gravity  # Removed

        old_location = self.get_location()

        if not EXPERIMENTAL_SLIDING:
            # Simple collision handling without sliding
            # Attempt to move along the X-axis
            self.x += self.velocity.x
            if not maze.is_move_allowed(self):
                self.x = old_location[0]

            # Attempt to move along the Y-axis
            self.y += self.velocity.y
            if not maze.is_move_allowed(self):
                self.y = old_location[1]

        else:
            # Experimental sliding collision handling
            self.x += self.velocity.x
            self.y += self.velocity.y
            if not maze.is_move_allowed(self):
                # If movement is blocked, revert to old location
                self.x, self.y = old_location[:2]
                max_angle = 60  # Maximum angle to attempt sliding

                # Attempt to slide by rotating the velocity vector incrementally
                for angle in range(1, max_angle + 1):
                    rad = angle / 180 * math.pi  # Convert angle to radians

                    # Rotate velocity vector clockwise by 'angle' degrees
                    self.x += math.cos(rad) * self.velocity.x - math.sin(rad) * self.velocity.y
                    self.y += math.sin(rad) * self.velocity.x + math.cos(rad) * self.velocity.y
                    if not maze.is_move_allowed(self):
                        # If still blocked, revert to old position
                        self.x, self.y = old_location[:2]
                    else:
                        # Successful slide exit loop
                        break

                    # Rotate velocity vector counter-clockwise by 'angle' degrees
                    rad = -rad
                    self.x += math.cos(rad) * self.velocity.x - math.sin(rad) * self.velocity.y
                    self.y += math.sin(rad) * self.velocity.x + math.cos(rad) * self.velocity.y
                    if not maze.is_move_allowed(self):
                        # If still blocked, revert to old position
                        self.x, self.y = old_location[:2]
                    else:
                        # Successful slide exit loop
                        break

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
        Render the player sprite on the screen based on current state.
        """
        from main import screen  # Importing here to avoid circular imports
        if self.current_surf is None:
            from main import DEBUG_MODE
            if DEBUG_MODE:
                print("Player image not loaded. Cannot display player.")
            return

        # Blit the current sprite onto the screen at the player's position
        # Adjust position to center the image
        screen.blit(self.current_surf, (int(self.x - self.radius), int(self.y - self.radius)))

    def set_position(self, x, y, z):
        """
        Update player's position.

        Args:
            x (float): New x-coordinate.
            y (float): New y-coordinate.
            z (float): New z-coordinate.
        """
        self.x = x
        self.y = y
        self.z = z

    def get_location(self):
        """
        Get current player location.

        Returns:
            tuple: (x, y, z) coordinates.
        """
        return self.x, self.y, self.z

    def get_parameters(self):
        """
        Get parameters for collision detection.

        Returns:
            tuple: (x, y, z, radius).
        """
        return self.x, self.y, self.z, self.radius

    def teleport(self, maze):
        """
        Teleport player to a random valid position.

        Args:
            maze (Maze): Maze object for valid position checks.
        """
        from main import WIDTH, HEIGHT
        has_found = False

        attempts = 0
        max_attempts = 100  # Prevent infinite loop

        while not has_found and attempts < max_attempts:
            temp_x = random.randint(self.radius, WIDTH - self.radius)
            temp_y = random.randint(self.radius, HEIGHT - self.radius)
            temp_z = self.z  # Teleport to the same z_level

            if maze.is_move_allowed(Player(temp_x, temp_y, temp_z)):
                has_found = True
                self.set_position(temp_x, temp_y, temp_z)
                from main import DEBUG_MODE
                if DEBUG_MODE:
                    print(f"Player teleported to ({temp_x}, {temp_y}, {temp_z})")
            attempts += 1

        if has_found:
            # Switch to Teleport sprite
            self.current_surf = self.teleport_surf
            # Set a timer to revert to default sprite after a short duration
            self.teleport_end_time = pygame.time.get_ticks() / 1000 + 0.5  # 0.5 seconds duration
            self.is_teleporting = True
        else:
            from main import DEBUG_MODE
            if DEBUG_MODE:
                print("Teleport failed: No free position found.")

    def handle_timers(self):
        """
        Manage timers for temporary effects like speed boosts and teleporting.
        """
        current_time = pygame.time.get_ticks() / 1000
        # Handle speed boost timer
        if self.speed_boost_active and current_time >= self.speed_boost_end_time:
            self.max_speed -= 2  # Revert max_speed
            self.speed_boost_active = False
            # Only revert sprite if not teleporting
            if not self.is_teleporting:
                self.current_surf = self.original_surf
            from main import DEBUG_MODE
            if DEBUG_MODE:
                print("Speed boost ended.")

        # Handle teleport timer
        if self.is_teleporting and current_time >= self.teleport_end_time:
            self.is_teleporting = False
            # Only revert sprite if speed boost is not active
            if not self.speed_boost_active:
                self.current_surf = self.original_surf
            from main import DEBUG_MODE
            if DEBUG_MODE:
                print("Teleport effect ended.")

        # Ensure sprite reflects current state priority
        if self.is_teleporting:
            self.current_surf = self.teleport_surf
        elif self.speed_boost_active:
            self.current_surf = self.dash_surf
        else:
            self.current_surf = self.original_surf

    def apply_speed_boost(self, duration=5.0):
        """
        Apply a speed boost for a set duration.

        Args:
            duration (float, optional): Boost duration in seconds. Defaults to 5.0.
        """
        if not self.speed_boost_active:
            self.max_speed += 2  # Increase max_speed
            self.speed_boost_active = True
            self.speed_boost_end_time = pygame.time.get_ticks() / 1000 + duration
            self.current_surf = self.dash_surf  # Switch to Dash sprite
            from main import DEBUG_MODE
            if DEBUG_MODE:
                print("Speed boost activated!")
        else:
            from main import DEBUG_MODE
            if DEBUG_MODE:
                print("Speed boost is already active. Cannot stack boosts.")

    def reduce_dash_cooldown(self):
        """
        Decrease the dash cooldown, not going below 0.5 seconds.
        """
        self.dash_cooldown = max(0.5, self.dash_cooldown - 0.1)
        from main import DEBUG_MODE
        if DEBUG_MODE:
            print(f"Dash cooldown reduced to {self.dash_cooldown} seconds.")

    def reduce_teleport_cooldown(self):
        """
        Decrease the teleport cooldown, not going below 2.0 seconds.
        """
        self.teleport_cooldown = max(2.0, self.teleport_cooldown - 0.5)
        from main import DEBUG_MODE
        if DEBUG_MODE:
            print(f"Teleport cooldown reduced to {self.teleport_cooldown} seconds.")
