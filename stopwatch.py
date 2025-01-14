import time

import pygame


class Stopwatch:
    def __init__(self, precision=2):
        """Create a stopwatch with specified precision.
        Default state is paused"""
        self.start_time = time.time()
        self.precision = precision
        self.elapsed_time = 0
        self.running = False

    def start(self):
        """Start the stopwatch if it is paused"""
        if self.running:  # already started
            return
        self.start_time = time.time()
        self.running = True

    def pause(self):
        """Pause the stopwatch"""
        if not self.running:  # already paused
            return
        self.elapsed_time += time.time() - self.start_time
        self.start_time = time.time()
        self.running = False

    def get_elapsed_time(self):
        """Returns the total elapsed time of the stopwatch in seconds,
        rounded to the stopwatch's precision"""
        if self.running:
            self.elapsed_time += time.time() - self.start_time
        self.start_time = time.time()
        return round(self.elapsed_time, self.precision)

    def display(self, screen):
        """Display the current game's elapsed time on the given screen"""
        cur_time = self.get_elapsed_time()

        # draw the current time
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(str(cur_time), True, (255, 255, 255))
        text_rect = text_surface.get_rect(topleft=(980, 20))
        screen.blit(text_surface, text_rect)


    def reset(self):
        """Reset the stopwatch's time"""
        self.__init__()


if __name__ == '__main__':
    # testing code
    stopwatch = Stopwatch()
    stopwatch.start()
    print(stopwatch.get_elapsed_time())

    time.sleep(1)

    stopwatch.pause()
    print(stopwatch.get_elapsed_time())

    time.sleep(3)

    stopwatch.start()
    print(stopwatch.get_elapsed_time())
    time.sleep(1)
    stopwatch.pause()
    print(stopwatch.get_elapsed_time())

    stopwatch.reset()
    print(stopwatch.get_elapsed_time())
