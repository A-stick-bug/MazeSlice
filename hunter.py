# hunter.py

from math import dist
from random import random

from main import Player
from shapes import Circle

class Hunter(Circle):
    """"""

    def __init__(self, x, y, z, radius, speed=0.0):
        super().__init__(x, y, z, radius)
        self.speed = speed

    def z_distance_from_player(self, player: Player):
        return abs(self.z, player.get_z())

    def handle_movement(self, player: Player) -> None:
        """"""
        # maybe just let hunter move freely through obstacles

        if self.z_distance_from_player(player) <= 20:
            player_location = player.get_location()[:2]
            cur_location = (self.x, self.y)
            distance_from_player = dist(player_location, cur_location)
            movement_scalar = player.speed / distance_from_player
            self.x += (player.get_x() - self.x) * movement_scalar
            self.y += (player.get_y() - self.y) * movement_scalar
            if self.z > player.get_z():
                if random.random() > self.speed / 10:
                    self.z -= 1
            elif self.z < player.get_z():
                if random.random() > self.speed / 10:
                    self.z += 1
            # separate z movement from xy, and cheap non integral speed implementation