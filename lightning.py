# lightning.py

import math
import pygame
import random


def dist(a, b):
    """Distance helper function to optimize time, just for this program."""
    return math.isqrt(int(a[0] - b[0]) ** 2 + int(a[1] - b[1]) ** 2)


class LightningSegment:
    """Represents an individual segment of lightning."""

    def __init__(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        color: tuple[int, int, int],
    ):
        """Initializes a lightning segment with its start position, end
        position and color.

        Args:
            start: The start location of the segment.
            end: The end location of the segment.
            color: The color of the segment used for displaying purposes.
        """
        self.start_position = start
        self.end_position = end
        self.color = color

    def display(self, surface: pygame.Surface):
        """Display the lightning segment as a line on the given pygame surface.."""
        pygame.draw.line(surface, self.color, self.start_position, self.end_position, 3)


class Lightning:
    """Lightning to be displayed in the maze upon teleportation.

    Attributes:
        time: The number of frames since the lightning has been generated.
        lightning_segments: The individual segments of the lightning
        collected in a list.
    """

    def __init__(self, start: list[float, float], end: list[float, float]):
        """Initializes the lightning.

        Args:
            start: The starting position of the lightning.
            end: The ending position of the lightning.
        """
        self.start_position = start
        self.end_position = end
        self.time = 0

        # Generation of individual segments.
        self.lightning_segments = []
        curr_pos = list(start)
        # print(curr_pos)

        # Used for keeping track of when each segment should display.
        curr_time = 0
        duration = 120

        # Loop to generate each segment. Ends if finished.
        # As distance always decreases, this while loop eventually finishes.
        # But this is also laggy so the max amount of segments is capped.
        total_cnt = 0
        while True:
            total_cnt += 1

            # If close enough to end position, or there are too many segments
            # make a segment connecting it directly.
            if dist(curr_pos, end) <= 50 or total_cnt > 20:
                color = (
                    random.randint(224, 255),
                    random.randint(206, 238),
                    random.randint(16, 48),
                )
                new_lightning_segment = LightningSegment(curr_pos, end, color)
                self.lightning_segments.append(
                    (new_lightning_segment, (curr_time, curr_time + duration))
                )
                break

            distance = random.randint(35, 60)

            # Randomly generate potential segments.
            # There are always more than 1 / 3 chance of succeeding.
            while True:
                angle = random.random() * 2 * math.pi
                vec = [distance * math.cos(angle), distance * math.sin(angle)]
                new_pos = curr_pos[:]
                new_pos[0] += vec[0]
                new_pos[1] += vec[1]

                # Check if this segment shortens the distance.
                # Terminates if a suitable new position is found.
                if dist(curr_pos, end) > dist(new_pos, end):
                    color = (
                        random.randint(224, 255),
                        random.randint(206, 238),
                        random.randint(16, 48),
                    )
                    new_lightning_segment = LightningSegment(curr_pos, new_pos, color)
                    self.lightning_segments.append(
                        (new_lightning_segment, (curr_time, curr_time + duration))
                    )

                    # Set current position to new position.
                    curr_pos = new_pos
                    break

            # Increments the time for which this segment should start displaying.
            curr_time += random.randint(0, 2)

    def display(self, surface: pygame.Surface):
        """Display the lightning onto the given surface.

        Args:
            surface: The pygame surface to draw the lightning on.
        """
        for lightning_segment in self.lightning_segments:
            time_range = lightning_segment[1]

            # Displays only if in correct time range.
            if time_range[0] <= self.time <= time_range[1]:
                lightning_segment[0].display(surface)

        # Increments time.
        # Only advances if called. This will be paused when the game is paused.
        self.time += 1

    def check_used(self) -> bool:
        """Checks if this lightning is being displayed.
        
        Since it might be expensive to display a lightning, the lightning can
        be removed if unused.
        
        Returns True if used and False otherwise."""
        if self.time > self.lightning_segments[-1][1][1]:
            return False
        return True
