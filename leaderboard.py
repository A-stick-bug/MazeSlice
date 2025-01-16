import json
from bisect import insort

import pygame


class Leaderboard:
    """Leaderboard that keeps track of top 10 scores in each difficulty.

    Attributes:
        bg_surf: A pygame surface for the background.
        leaderboard: A dictionary storing an array of the highest scores for
        each difficulty.

    Structure of leaderboard.json:
    {
    "easy": list[float],
    "medium": list[float],
    "hard": list[float],
    "???": list[float]
    }
    """

    def __init__(self):
        """Initializes the leaderboard.

        Try loading the leaderboard from `leaderboard.json`, otherwise
        create an empty one."""
        self.bg_surf = pygame.image.load("graphics/leaderboard_bg.png").convert_alpha()
        self.leaderboard = {"easy": [], "medium": [], "hard": [], "???": []}
        try:  # Try loading leaderboard.
            with open("leaderboard.json", "r") as f:
                self.leaderboard = json.load(f)
        except (ValueError, FileNotFoundError):  # Create an empty json file.
            self.save_to_file()

    def save_to_file(self) -> None:
        """Save the current leaderboard to `leaderboard.json`"""
        with open("leaderboard.json", "w") as f:
            json.dump(self.leaderboard, f)

    def add_score(self, difficulty: str, score: float) -> None:
        """Add a score to the leaderboard in the given difficulty level.
        
        Increasing property will be maintained
        
        Args:
            difficulty: the difficulty level
            score: the score of this run. Equal to the elapsed time from stopwatch.
        """
        insort(self.leaderboard[difficulty], score)  # Insert, list stays .
        if len(self.leaderboard[difficulty]) > 10:
            self.leaderboard[difficulty].pop()
        self.save_to_file()

    def display(self, screen: pygame.Surface) -> None:
        """Displays the leaderboard on the given screen."""
        # colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GRAY = (150, 150, 150)
        CYAN = "#4FC3F7"

        # Clear screen and draw background for leaderboard.
        screen.fill(BLACK)
        screen.blit(self.bg_surf, (0, 0))

        # Draw title.
        font = pygame.font.SysFont("comicsansms", 35)  # font for title
        title_surface = font.render("Leaderboard", True, WHITE)
        screen.blit(
            title_surface,
            (screen.get_width() // 2 - title_surface.get_width() // 2, 30),
        )

        entry_font = pygame.font.SysFont("comicsansms", 25)  # font for rankings
        column_titles = self.leaderboard.keys()
        column_spacing = screen.get_width() // len(column_titles)

        # Draw columns.
        for i, column_title in enumerate(column_titles):
            x_pos = i * column_spacing + column_spacing // 2

            # column subtitle
            title_surface = entry_font.render(column_title.capitalize(), True, CYAN)
            screen.blit(title_surface, (x_pos - title_surface.get_width() // 2, 110))

            if self.leaderboard[column_title]:
                # scores
                for j, score in enumerate(self.leaderboard[column_title]):
                    score_surface = entry_font.render(
                        f"{j + 1}. {score:.2f}s", True, WHITE
                    )
                    screen.blit(
                        score_surface,
                        (x_pos - score_surface.get_width() // 2, 155 + j * 40),
                    )
            else:
                # no scores
                no_scores_surface = entry_font.render("No Scores", True, GRAY)
                screen.blit(
                    no_scores_surface, (x_pos - no_scores_surface.get_width() // 2, 155)
                )
