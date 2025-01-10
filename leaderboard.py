"""
Leaderboard that keeps track of top 10 scores in each difficulty level.
Structure of leaderboard.json:
{
   "easy": list[float],
   "medium": list[float],
   "hard": list[float]
}
"""

import json
from bisect import insort


class Leaderboard:
    def __init__(self):
        """Try loading the leaderboard from `leaderboard.json`, otherwise
        create an empty one."""
        self.leaderboard = {"easy": [], "medium": [], "hard": []}
        try:  # try loading leaderboard
            with open("leaderboard.json", "r") as f:
                self.leaderboard = json.load(f)
        except (ValueError, FileNotFoundError):  # create empty one
            self.save_to_file()

    def save_to_file(self) -> None:
        """Save the current leaderboard to `leaderboard.json`"""
        with open("leaderboard.json", "w") as f:
            json.dump(self.leaderboard, f)

    def add_score(self, difficulty: str, score: float) -> None:
        """Add a score to the leaderboard in the given difficulty level,
        Increasing property wil lbe maintained"""
        insort(self.leaderboard[difficulty], score)
        if len(self.leaderboard[difficulty]) > 10:
            self.leaderboard[difficulty].pop()
        self.save_to_file()

    def get_scores(self, difficulty: str) -> list[float]:
        """Return the top 10 scores in the given difficulty level"""
        return self.leaderboard[difficulty]

    def __str__(self):
        """Convert the leaderboard to a string as a python dictionary"""
        return str(self.leaderboard)


if __name__ == '__main__':
    leaderboard = Leaderboard()  # testing code
    leaderboard.add_score("easy", 10)
    leaderboard.add_score("easy", 20)
    leaderboard.add_score("easy", 15)
    leaderboard.add_score("hard", 5)
    leaderboard.add_score("hard", 1)
    leaderboard.add_score("medium", 3)

    print(leaderboard)
