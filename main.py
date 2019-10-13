import pygame
import time
import random
import os

pygame.init()

black = (50, 50, 50)
white = (255, 255, 255)

tile_size = 30
board_size_x, board_size_y = 10, 24

FPS = 60

WIN_WIDTH = board_size_x * tile_size
WIN_HEIGHT = board_size_y * tile_size + 50
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
bar = pygame.Rect((0, 0, WIN_WIDTH, WIN_HEIGHT-tile_size * board_size_y))

"""
0:
center>##
       ##
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
4:
    ##<center
     #
     #
5:
        #
center>##
       #
6:
    #
    ##<center
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
    (
        (-1, 0),
        (0, 0),
        (0, -1),
        (0, -2)
    ),
    (
        (1, -1),
        (1, 0),
        (0, 0),
        (0, 1)
    ),
    (
        (-1, -1),
        (-1, 0),
        (0, 0),
        (0, 1)
    )
)


def board_x(x):
    """Return x position on board"""
    return (WIN_WIDTH - board_size_x*tile_size) + int(x)*tile_size


def board_y(y):
    """Return y position on board"""
    return (WIN_HEIGHT - board_size_y*tile_size) + int(y)*tile_size


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


def rotate_body(piece, rotation):
    """Return rotated piece by a degree of rotation"""
    new_x = piece[0]
    new_y = piece[1]
    if rotation == 90:
        new_x = -piece[1]
        new_y = piece[0]
    elif rotation == 180:
        new_x = -piece[0]
        new_y = -piece[1]
    elif rotation == 270:
        new_x = piece[1]
        new_y = -piece[0]
    return new_x, new_y


class BasicFigure:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.image = image

    def draw(self, surface):
        surface.blit(self.image, self.pos)


class FallingFigure(BasicFigure):
    def __init__(self, x, y, speed):
        shape_index = random.randrange(len(shapes))
        self.shape = shapes[shape_index]
        super().__init__(x, y, load_img(f"basic_shape{shape_index}.png"))

        self.speed = speed/FPS
        self.rotation = random.randint(0, 3) * 90
        self.body = self.translate_shape()

    def move(self, right, left):
        move = int(right) - int(left)
        min_x = min(self.body, key=lambda x: x[0])[0]
        max_x = max(self.body, key=lambda x: x[0])[0]
        if 0 < min_x + move and max_x + tile_size*move < board_x(board_size_x):
            self.x += move

        self.y += self.speed

        self.body = self.translate_shape()

    def rotate(self, value, game_blocks):
        new_rotation = self.rotation + value
        new_rotation %= 360

        for piece in self.body:
            if rotate_body(piece, new_rotation) in [b.pos for b in game_blocks]:
                return

        self.rotation = new_rotation
        self.body = self.translate_shape()

    def translate_shape(self):
        new_body = []
        for piece in self.shape:
            new_x, new_y = rotate_body(piece, self.rotation)
            new_body.append((board_x(new_x + self.x), board_y(new_y + self.y)))
        return new_body

    def next_move_available(self, game_blocks):
        for piece in self.body:
            piece_pos_in_next_move = (piece[0], piece[1] + tile_size)
            if piece_pos_in_next_move in [b.pos for b in game_blocks]:
                return False

        max_y = max(self.body, key=lambda x: x[1])[1]
        if max_y + tile_size < board_y(board_size_y):
            return True
        return False

    def draw(self, surface):
        for piece_coordinates in self.body:
            surface.blit(self.image, piece_coordinates)


def draw_window(win_surface, blocks, falling_fig):
    win_surface.fill(black)
    for block in blocks:
        block.draw(win_surface)
    falling_fig.draw(win_surface)

    pygame.draw.rect(win_surface, white, bar)


def main():
    clock = pygame.time.Clock()

    falling_figure = FallingFigure(5, 3, 5)
    game_blocks = []

    score = 0

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
                    falling_figure.rotate(90, game_blocks)
                if e.key == pygame.K_s:
                    falling_figure.rotate(-90, game_blocks)

        falling_figure.move(right, left)
        if not falling_figure.next_move_available(game_blocks):
            for piece in falling_figure.body:
                game_blocks.append(BasicFigure(piece[0], piece[1], falling_figure.image))
            falling_figure = FallingFigure(5, 0, 5)

        draw_window(win, game_blocks, falling_figure)
        pygame.display.update()


if __name__ == '__main__':
    main()
