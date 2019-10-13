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
bar = pygame.Rect((0, 0, WIN_WIDTH, WIN_HEIGHT - tile_size * board_size_y))

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
    """Return x position on screen from position on board"""
    return (WIN_WIDTH - board_size_x * tile_size) + int(x) * tile_size


def board_y(y):
    """Return y position on screen from position on board"""
    return (WIN_HEIGHT - board_size_y * tile_size) + int(y) * tile_size


def board_pos(pos):
    """Return x,y position on screen from position on board"""
    return board_x(pos[0]), board_y(pos[1])


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


def next_move_available(body, game_blocks):
    def next_move(pos): return int(pos[0]), int(pos[1]) + 1

    for piece in body:
        if next_move(piece) in [b.pos for b in game_blocks]:
            return False

    max_y_piece = max(body, key=lambda pos: pos[1])
    if next_move(max_y_piece)[1] < board_size_y:
        return True
    return False


class BasicFigure:
    def __init__(self, x, y, image):
        self.x = int(x)
        self.y = int(y)
        self.pos = (self.x, self.y)
        self.image = image

    def draw(self, surface):
        surface.blit(self.image, board_pos(self.pos))


class FallingFigure(BasicFigure):
    def __init__(self, x=5, y=1, speed=48):
        shape_index = random.randrange(len(shapes))
        self.shape = shapes[shape_index]
        super().__init__(x, y, load_img(f"basic_shape{shape_index}.png"))

        self.speed = speed
        self.rotation = random.randrange(4) * 90
        self.preview_image = load_img('basic_shape_preview.png')
        self.body = self.translate_shape()

    def move(self, right=False, left=False):
        move = int(right) - int(left)
        min_x = min(self.body, key=lambda pos: pos[0])[0]
        max_x = max(self.body, key=lambda pos: pos[0])[0]
        if 0 <= min_x + move and max_x + move < board_size_x:
            self.x += move

        self.y += 1 / self.speed

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
            new_body.append((new_x + self.x, new_y + self.y))
        return new_body

    def draw(self, surface):
        for piece_coordinates in self.body:
            surface.blit(self.image, board_pos(piece_coordinates))

    def draw_preview(self, surface, game_blocks):
        to_go = 0

        body = self.body.copy()
        while next_move_available(body, game_blocks):
            to_go += 1
            for i, piece in enumerate(body):
                body[i] = int(piece[0]), int(piece[1])+1
                print(body[i])

        for piece in body:
            surface.blit(self.preview_image, board_pos(piece))


def draw_window(surface, game_blocks, falling_fig):
    surface.fill(black)
    for block in game_blocks:
        block.draw(surface)

    falling_fig.draw_preview(surface, game_blocks)
    falling_fig.draw(surface)

    pygame.draw.rect(surface, white, bar)


def main():
    clock = pygame.time.Clock()

    ff = FallingFigure()  # Stands for falling_figure
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
                    ff.rotate(90, game_blocks)
                if e.key == pygame.K_s:
                    ff.rotate(-90, game_blocks)

                if e.key == pygame.K_SPACE:
                    print('HEJ!')
                    while next_move_available(ff.body, game_blocks):
                        ff.move()

        ff.move(right, left)
        if not next_move_available(ff.body, game_blocks):
            for piece in ff.body:
                game_blocks.append(BasicFigure(piece[0], piece[1], ff.image))
            ff = FallingFigure()

        count_removed_lines = 0
        for y_level in range(board_size_y):
            blocks_to_remove = []
            for block in game_blocks:
                # Count blocks
                if block.y == y_level:
                    blocks_to_remove.append(block)

            if len(blocks_to_remove) == board_size_x:
                # Remove blocks
                count_removed_lines += 1
                for block in blocks_to_remove:
                    game_blocks.remove(block)

                for block in game_blocks:
                    if block.y < y_level:
                        block.y += 1
                        block.pos = (block.x, block.y)

        draw_window(win, game_blocks, ff)
        pygame.display.update()


if __name__ == '__main__':
    main()
