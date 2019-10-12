import pygame
import time
import random
import os

pygame.init()

black = (50, 50, 50)

tile_size = 40

WIN_WIDTH, WIN_HEIGHT = 400, 1040
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))


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
    def __init__(self, x, y, image, rotation=random.randint(0, 3)*90):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.image = load_img(image)
        self.body = [(self.x, self.y), (self.x+40, self.y)]

    def update_body(self):
        pass

    def draw(self, surface):
        for piece_coordinates in self.body:
            surface.blit(self.image, piece_coordinates)


class FloatingFigure(BasicFigure):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.y_vel = 0
        self.speed = 0


def draw_window(win_surface, shape):
    win_surface.fill(black)
    pygame.draw.line(win, (255, 255, 255), (0, WIN_HEIGHT-tile_size*24), (tile_size*10, WIN_HEIGHT-tile_size*24))

    shape.draw(win)


def main():
    clock = pygame.time.Clock()
    fps = 30

    shape1 = BasicFigure(200, 160, "basic_shape1.png")

    run = True
    while run:
        clock.tick(fps)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                quit()

        draw_window(win, shape1)
        pygame.display.update()


if __name__ == '__main__':
    main()
