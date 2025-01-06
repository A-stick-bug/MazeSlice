import pygame

from shapes import Cylinder

class Item(Cylinder):
    def __init__(self, x, y, start_z, end_z, radius):
        super().__init__(x, y, start_z, end_z, radius)