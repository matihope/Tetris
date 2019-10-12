import pygame
import time
import random
import os
import am

pygame.init()

black = (50, 50, 50)
white = (255, 255, 255)

tile_size = 30

FPS = 60

WIN_WIDTH = 10*tile_size
WIN_HEIGHT = 24*tile_size + 50
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
bar = pygame.Rect((0, 0, WIN_WIDTH, WIN_HEIGHT-tile_size*24))

"""
0:
    ##
    ##
    
    center:
        #   #
          #
        #   #
1:
    # # # #
        ^-center
2:
       #
center>##
       #
3:
center>##
       #
       #
"""
shapes = (
    (
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1)
    ),

    (
        (0, -1),
        (0, 0),
        (0, 1),
        (0, 2)
    ),

    (
        (0, -1),
        (0, 0),
        (1, 0),
        (0, 1)
    ),

    (
        (0, 0),
        (1, 0),
        (0, 1),
        (0, 2)
    ),
)


def board_x(x):
    """Return x position on board"""
    return (WIN_WIDTH - 10*tile_size) + int(x)*tile_size


def board_y(y):
    """Return y position on board"""
    return (WIN_HEIGHT - 24*tile_size) + int(y)*tile_size


def load_img(file_name):
    """Load image and and return as image object"""
    full_name = os.path.join('resources', file_name)
    try:
        image = pygame.image.load(full_name)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error as message:
        print('Cannot load image:', full_name)
        raise SystemExit(message)
    return image


class BasicFigure:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image

    def draw(self, surface):
        surface.blit(self.image, (board_x(self.x), board_y(self.y)))


class FallingFigure(BasicFigure):
    def __init__(self, x, y):
        shape_index = random.randint(0, len(shapes)-1)

        self.shape = shapes[2]
        super().__init__(x, y, load_img(f"basic_shape{2}.png"))  # Later shape_index instead of 2

        self.y_vel = 0
        self.speed = 0
        self.rotation = random.randint(0, 3) * 90
        self.body = self.translate_shape()

    def move(self, right, left):
        move = int(right) - int(left)
        min_x = min(self.body, key=lambda x: x[0])[0]
        max_x = max(self.body, key=lambda x: x[0])[0]
        if 0 < min_x + move and \
                max_x + tile_size*move < WIN_WIDTH:
            self.x += move

        self.y += 2/FPS

        self.body = self.translate_shape()

    def rotate(self, value):
        self.rotation += value if value > 0 else 360-value
        self.rotation %= 360
        self.body = self.translate_shape()

    def translate_shape(self):
        new_body = []

        for piece in self.shape:

            new_x = piece[0]
            new_y = piece[1]
            if self.rotation == 90:
                new_x = piece[1]
                new_y = piece[0] if piece[0] > 0 else -piece[0]
            elif self.rotation == 180:
                new_x = -piece[0]
                new_y = -piece[1]
            elif self.rotation == 270:
                new_x = piece[1]
                new_y = piece[0] if piece[0] < 0 else -piece[0]

            new_body.append((board_x(new_x + self.x), board_y(new_y + self.y)))
        return new_body

    def draw(self, surface):
        for piece_coordinates in self.body:
            surface.blit(self.image, piece_coordinates)


def draw_window(win_surface, shape):
    win_surface.fill(black)

    shape.draw(win)

    pygame.draw.rect(win_surface, white, bar)


def main():
    clock = pygame.time.Clock()

    shape1 = FallingFigure(5, 0)

    run = True
    while run:
        clock.tick(FPS)
        right, left = False, False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                    right = True
                if e.key == pygame.K_LEFT or e.key == pygame.K_a:
                    left = True
                
                if e.key == pygame.K_w:
                    shape1.rotate(90)
                if e.key == pygame.K_s:
                    shape1.rotate(-90)

        shape1.move(right, left)

        draw_window(win, shape1)
        pygame.display.update()


if __name__ == '__main__':
    main()
