import math


def length_dir_x(speed, angle):
    return math.cos(angle * (math.pi/180)) * speed


def length_dir_y(speed, angle):
    return math.sin(angle * (math.pi / 180)) * speed


def get_angle(w, h):
    return (math.atan(h/w) * 180) / math.pi


def pitagoras(a, b):
    return math.sqrt(a**2 + b**2)


def rotate(hb, center, w, h, new_direction):
    new_hitbox = []

    arm = pitagoras(w / 2, h / 2)
    special_angle = get_angle(w, h)  # That is math.atan

    for corner in range(len(hb)):
        new_x, new_y = center

        # TOP LEFT
        if corner == 0:
            new_x += length_dir_x(arm, 180 + special_angle + new_direction)
            new_y += length_dir_y(arm, 180 + special_angle + new_direction)

        # TOP RIGHT
        elif corner == 1:
            new_x += length_dir_x(arm, 360 - special_angle + new_direction)
            new_y += length_dir_y(arm, 360 - special_angle + new_direction)

        # BOTTOM RIGHT
        elif corner == 2:
            new_x += length_dir_x(arm, special_angle + new_direction)
            new_y += length_dir_y(arm, special_angle + new_direction)

        # BOTTOM LEFT
        elif corner == 3:
            new_x += length_dir_x(arm, 180 - special_angle + new_direction)
            new_y += length_dir_y(arm, 180 - special_angle + new_direction)

        new_hitbox.append((new_x, new_y))

    return new_hitbox


def get_center(hb, w, h, direction):
    arm = pitagoras(w / 2, h / 2)
    special_angle = get_angle(w, h)

    return (round(hb[0][0] + length_dir_x(arm, special_angle + direction)),
            round(hb[0][1] + length_dir_y(arm, special_angle + direction)))


def sign(x):
    if x > 0:
        return 1

    elif x < 0:
        return -1

    elif x == 0:
        return 0