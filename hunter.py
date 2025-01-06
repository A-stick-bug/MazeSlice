import pygame

from math import dist

from item import Item
from main import Player

class Hunter(Item):
    """"""

    def __init__(self, x, y, start_z, end_z, radius, speed):
        super().__init__(x, y, start_z, end_z, radius, 0)
        self.speed = speed

    def handle_movement(self, player):
        """"""
        # maybe just let hunter move freely through obstacles

        player_location = player.get_location()
        mid_z = (self.start_z + self.end_z) / 2
        cur_location = (self.x, self.y, mid_z) # may be replaced by self.get_location()
        distance_from_player = dist(player_location, cur_location)
        movement_scalar = player.speed / distance_from_player
        self.x += (player.get_x() - self.x) * movement_scalar
        self.y += (player.get_y() - self.y) * movement_scalar
        self.start_z += (player.get_x() - mid_z) * movement_scalar
        self.end_z += (player.get_x() - mid_z) * movement_scalar