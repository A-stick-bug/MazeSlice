import time
import pygame


class Stopwatch:
    """
    Stopwatch with start, pause, and reset functionalities.

    Attributes:
        start_time (float): The timestamp when the stopwatch was last started.
        precision (int): The number of decimal places to round the elapsed time.
        elapsed_time (float): The total accumulated elapsed time.
        running (bool): Indicates whether the stopwatch is currently running.
    """

    def __init__(self, precision=2):
        """
        Initializes the Stopwatch instance with specified precision.

        Args:
            precision (int, optional): Number of decimal places for elapsed time. Defaults to 2.
        """
        self.start_time = time.time()
        self.precision = precision
        self.elapsed_time = 0
        self.running = False

    def start(self):
        """
        Starts the stopwatch if it is currently paused.

        If the stopwatch is already running, this method has no effect.
        """
        if self.running:  # already started
            return
        self.start_time = time.time()
        self.running = True

    def pause(self):
        """
        Pauses the stopwatch.

        If the stopwatch is already paused, this method has no effect.
        """
        if not self.running:  # already paused
            return
        self.elapsed_time += time.time() - self.start_time
        self.start_time = time.time()
        self.running = False

    def get_elapsed_time(self):
        """
        Retrieves the total elapsed time in seconds, rounded to the specified precision.

        If the stopwatch is running, it includes the time since it was last started.

        Returns:
            float: The total elapsed time in seconds, rounded to the stopwatch's precision.
        """
        if self.running:
            current_elapsed = self.elapsed_time + (time.time() - self.start_time)
            return round(current_elapsed, self.precision)
        return round(self.elapsed_time, self.precision)

    def display(self, screen):
        """
        Renders the current elapsed time onto the given Pygame screen.

        The time is displayed in white color at the position (980, 20) with two decimal places.

        Args:
            screen (pygame.Surface): The Pygame surface where the time will be displayed.
        """
        cur_time = self.get_elapsed_time()

        # Draw the current time to the specified precision
        font = pygame.font.SysFont("comicsansms", 25)
        text_surface = font.render(f"{cur_time:.2f}s", True, (255, 255, 255))
        text_rect = text_surface.get_rect(topleft=(980, 20))
        screen.blit(text_surface, text_rect)

    def reset(self):
        """
        Resets the stopwatch's elapsed time and pauses it.

        After resetting, the stopwatch starts in a paused state with zero elapsed time.
        """
        self.__init__()


if __name__ == '__main__':
    # Testing code for the Stopwatch class
    stopwatch = Stopwatch()
    stopwatch.start()
    print("Elapsed Time after starting:", stopwatch.get_elapsed_time())

    time.sleep(1)

    stopwatch.pause()
    print("Elapsed Time after pausing:", stopwatch.get_elapsed_time())

    time.sleep(3)

    stopwatch.start()
    print("Elapsed Time after restarting:", stopwatch.get_elapsed_time())
    time.sleep(1)
    stopwatch.pause()
    print("Elapsed Time after second pausing:", stopwatch.get_elapsed_time())

    stopwatch.reset()
    print("Elapsed Time after resetting:", stopwatch.get_elapsed_time())
