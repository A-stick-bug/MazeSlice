# lightning.py

import pygame
import random
import math


class LightningSegment():
    """Individual segment of lightning."""

    def __init__(self, start: tuple[float, float], end: tuple[float, float], color: tuple[int, int, int]):
        self.start_position = start
        self.end_position = end
        self.color = color

    def display(self, surface: pygame.Surface):
        pygame.draw.line(surface, self.color,
                         self.start_position, self.end_position)


class Lightning():
    """Lightning to be displayed upon teleportation."""

    def __init__(self, start: tuple[float, float], end: tuple[float, float]):
        """"""
        self.start_position = start
        self.end_position = end
        self.time = 0

        # Generation of individual segments.
        self.lightning_segments = []
        curr_pos = start

        # Used for keeping track of when each segment should display.
        curr_time = 0
        duration = 120

        # Loop to generate each segment. Ends if finished.
        # As distance always decreases, this while loop eventually finishes.
        while True:
            distance = random.randint(15, 25)

            # Randomly generate potential segments.
            # There are always more than 1 / 3 chance of succeeding.
            while True:
                angle = random.random() * 2 * math.pi
                vec = (distance * math.cos(angle), distance * math.sin(angle))
                new_pos = curr_pos
                new_pos[0] += vec[0]
                new_pos[1] += vec[1]

                # Check if this segment shortens the distance.
                if math.dist(curr_pos, end) > math.dist(new_pos, end):
                    color = (
                        random.randint(255, 224),
                        random.randint(238, 206),
                        random.randint(48, 16)
                    )
                    new_lightning_segment = LightningSegment(
                        curr_pos, new_pos, color)
                    self.lightning_segments.append(
                        new_lightning_segment, (curr_time, curr_time + duration))

                    # Set current position to new position.
                    curr_pos = new_pos

                    # Breaks this while loop.
                    break

            # Increments current time.
            if random.random() > 0.5:
                curr_time += 1

            # If close enough to end position, make a segment connecting it directly.
            if math.dist(curr_pos, end) <= 25:
                color = (
                    random.randint(255, 224),
                    random.randint(238, 206),
                    random.randint(48, 16)
                )
            new_lightning_segment = LightningSegment(
                curr_pos, new_pos, color)
            self.lightning_segments.append(
                new_lightning_segment, (curr_time, curr_time + duration))

    def display(self, surface: pygame.Surface):
        for lightning_segment in self.lightning_segments:
            time_range = lightning_segment[1]

            # Displays only if in correct time range.
            if time_range[0] <= self.time <= time_range[1]:
                lightning_segment[0].display()

        # Increments time.
        # Only advances if called. This will be paused when the game is paused.
        self.time += 1

    def check_used(self) -> bool:
        if self.time > self.lightning_segments[-1][1][1]:
            return False
        return True
