from math import dist


def collides(circle1, circle2):
    x1, y1, z1, r1 = circle1
    x2, y2, z2, r2 = circle2
    d = dist((x1, y1, z1), (x2, y2, z2))
    return d < r1 + r2
