import pygame
import random
import os

pygame.font.init()
pygame.init()

black = (50, 50, 50)
white = (255, 255, 255)
bar_bg = (200, 200, 200)

tile_size = 30
board_size_x, board_size_y = 10, 24

FPS = 60

WIN_WIDTH = board_size_x * tile_size
WIN_HEIGHT = board_size_y * tile_size + 50
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
bar = pygame.Rect((0, 0, WIN_WIDTH, WIN_HEIGHT - tile_size * board_size_y))

STAT_FONT = pygame.font.SysFont("comicsans", 24)

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
        (1, 0),
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


def rotate_piece(piece, degree):
    """Return rotated piece by a degree"""
    new_x = piece[0]
    new_y = piece[1]
    if degree == 90:
        new_x = -piece[1]
        new_y = piece[0]
    elif degree == 180:
        new_x = -piece[0]
        new_y = -piece[1]
    elif degree == 270:
        new_x = piece[1]
        new_y = -piece[0]
    return new_x, new_y


def next_move_available(body, game_blocks):
    """Return true if body will not collide with other blocks, if its y += 1"""
    def next_move(pos): return int(pos[0]), int(pos[1]) + 1
    positions = [b.pos for b in game_blocks]

    for piece in body:
        # If positions match
        if next_move(piece) in positions:
            return False

    max_y_piece = max(body, key=lambda pos: pos[1])[1]
    if max_y_piece+1 < board_size_y:
        return True
    return False


def get_score(lines_cleared, level):
    """Return score for clearing lines"""
    if lines_cleared == 1:
        return 40 * (level + 1)
    elif lines_cleared == 2:
        return 100 * (level + 1)
    elif lines_cleared == 3:
        return 300 * (level + 1)
    elif lines_cleared >= 4:
        return 1200 * (level + 1)
    return 0


def get_speed(level):
    if 0 <= level <= 8:
        return 48 - 5*level
    elif level == 9:
        return 6
    elif 10 <= level <= 18:
        return 5 - ((level-10)//3)
    elif 19 <= level <= 28:
        return 2
    return 1


class BasicFigure:
    """Base of FallingFigure, also a game block"""
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
        self.rect = ()

    def move(self, right=False, left=False):
        """Move the figure, called every frame"""
        move = int(right) - int(left)
        self.x += move
        self.body = self.translate_shape()

        min_x = min(self.body, key=lambda pos: pos[0])[0]
        max_x = max(self.body, key=lambda pos: pos[0])[0]

        self.x = max(self.x, self.x-min_x)                       # Left barrier
        self.x = min(self.x, self.x - (max_x-board_size_x + 1))  # Right barrier

        self.y += 1 / self.speed

        self.body = self.translate_shape()

    def rotate(self, value, game_blocks):
        """Rotate and object by a degree, check if doesn't collide with other blocks"""
        new_rotation = self.rotation + value
        new_rotation %= 360

        for piece in self.body:
            if rotate_piece(piece, new_rotation) in [b.pos for b in game_blocks]:
                return

        self.rotation = new_rotation
        self.body = self.translate_shape()

    def translate_shape(self):
        """Return positions of body pieces, accordingly to figure's position and rotation"""
        new_body = []
        for piece in self.shape:
            new_x, new_y = rotate_piece(piece, self.rotation)
            new_body.append((new_x + self.x, new_y + self.y))

        return new_body

    def draw(self, surface):
        """Draw an object to the screen"""
        for piece_coordinates in self.body:
            surface.blit(self.image, board_pos(piece_coordinates))

    def draw_preview(self, surface, game_blocks):
        """Draw predicted position of the figure"""
        body = self.body.copy()
        while next_move_available(body, game_blocks):
            for i, piece in enumerate(body):
                body[i] = int(piece[0]), int(piece[1])+1

        for piece in body:
            surface.blit(self.preview_image, board_pos(piece))


def draw_window(surface, game_blocks, falling_fig, score_text):
    """Draw objects to the window"""
    surface.fill(black)
    for block in game_blocks:
        block.draw(surface)

    falling_fig.draw_preview(surface, game_blocks)
    falling_fig.draw(surface)

    # Drawing bar and score
    stats = STAT_FONT.render(score_text, 1, black)
    stats_x = WIN_WIDTH/2-stats.get_width()/2
    stats_y = ((WIN_HEIGHT - (board_size_y * tile_size)) / 2) - stats.get_height()/2

    pygame.draw.rect(surface, bar_bg, bar)
    surface.blit(stats, (stats_x, stats_y))


def main():
    """Main function, also a game loop"""
    clock = pygame.time.Clock()

    ff = FallingFigure()  # Stands for falling figure
    game_blocks = []

    score = 0
    game_level = 0
    lines_cleared_total = 0 if game_level == 0 else game_level*10

    run = True
    while run:
        clock.tick(FPS)
        right, left = False, False
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit(print(score))

            if e.type == pygame.KEYDOWN:
                # Check for move
                if e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                    right = True
                if e.key == pygame.K_LEFT or e.key == pygame.K_a:
                    left = True

                # Check for rotation
                if e.key == pygame.K_w:
                    ff.rotate(90, game_blocks)
                if e.key == pygame.K_s:
                    ff.rotate(-90, game_blocks)

                # Check for apply block
                if e.key == pygame.K_SPACE:
                    while next_move_available(ff.body, game_blocks):
                        ff.move()

        ff.move(right, left)

        # On collision
        if not next_move_available(ff.body, game_blocks):
            for piece in ff.body:
                game_blocks.append(BasicFigure(piece[0], piece[1], ff.image))
            ff = FallingFigure(speed=get_speed(game_level))
            score += 10

        # Iterate over all levels on the board
        lines_cleared = 0
        for y_level in range(board_size_y):
            blocks_to_remove = []
            for block in game_blocks:
                # Count blocks
                if block.y == y_level:
                    blocks_to_remove.append(block)

                if block.y == 0:
                    run = False

            # If line is full
            if len(blocks_to_remove) == board_size_x:
                lines_cleared += 1

                # Remove blocks
                for block in blocks_to_remove:
                    game_blocks.remove(block)

                # Move down the rest of the blocks
                for block in game_blocks:
                    if block.y < y_level:
                        block.y += 1
                        block.pos = (block.x, block.y)

        lines_cleared_total += lines_cleared
        game_level = lines_cleared_total // 10
        score += get_score(lines_cleared, game_level)

        text = f"Score: {score} | Level: {game_level} | Lines: {lines_cleared}"
        draw_window(win, game_blocks, ff, score_text=text)

        pygame.display.update()

    print(f'Score: {score}')


if __name__ == '__main__':
    main()
