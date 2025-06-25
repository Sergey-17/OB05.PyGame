import pygame
import random

# Настройки окна
WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 30
ROWS, COLS = HEIGHT // BLOCK_SIZE, WIDTH // BLOCK_SIZE

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
GREY = (128, 128, 128)

COLORS = [BLACK, RED, GREEN, BLUE, YELLOW, ORANGE, CYAN, PURPLE]

SHAPES = {
    'I': [[1, 1, 1, 1]],
    'J': [[1, 0, 0],
          [1, 1, 1]],
    'L': [[0, 0, 1],
          [1, 1, 1]],
    'O': [[1, 1],
          [1, 1]],
    'S': [[0, 1, 1],
          [1, 1, 0]],
    'Z': [[1, 1, 0],
          [0, 1, 1]],
    'T': [[0, 1, 0],
          [1, 1, 1]]
}

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[random.randint(1, len(COLORS)-1)]
        self.rotation = 0

    def image(self):
        return self.shape[self.rotation % len(self.shape)]

def draw_grid(surface, grid):
    surface.fill(BLACK)
    for y in range(ROWS):
        for x in range(COLS):
            pygame.draw.rect(
                surface,
                grid[y][x],
                (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                0
            )
            pygame.draw.rect(
                surface,
                GREY,
                (x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                1
            )

def check_full_rows(grid):
    rows_to_remove = []
    for y in range(ROWS):
        if BLACK not in grid[y]:
            rows_to_remove.append(y)
    return rows_to_remove

def remove_row(grid, row):
    del grid[row]
    empty_row = [BLACK for _ in range(COLS)]
    grid.insert(0, empty_row)

def draw_next_piece(next_piece, surface):
    font = pygame.font.SysFont('Comic Sans MS', 30)
    label = font.render('Next:', 1, WHITE)
    sx = WIDTH + 50
    sy = 100
    surface.blit(label, (sx + 10, sy - 30))
    shape_image = next_piece.image()
    for y in range(len(shape_image)):
        for x in range(len(shape_image[y])):
            if shape_image[y][x]:
                pygame.draw.rect(
                    surface,
                    next_piece.color,
                    (sx + x*BLOCK_SIZE, sy + y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    0
                )

def main():
    global grid
    pygame.init()
    win = pygame.display.set_mode((WIDTH + 150, HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()
    fall_time = 0
    change_piece = False
    current_piece = Piece(5, 0, SHAPES['I'])
    next_piece = Piece(5, 0, random.choice(list(SHAPES.values())))
    grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]

    run = True
    while run:
        fall_speed = 0.27
        grid = [[BLACK for _ in range(COLS)] for _ in range(ROWS)]
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(current_piece.image()[current_piece.y]) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not current_piece.image()[current_piece.y]:
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not current_piece.image()[current_piece.y]:
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not current_piece.image()[current_piece.y]:
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not current_piece.image()[current_piece.y]:
                        current_piece.rotation -= 1

        piece_pos = convert_shape_format(current_piece)
        for pos in piece_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in piece_pos:
                x, y = pos
                grid[y][x] = current_piece.color
            current_piece = next_piece
            next_piece = Piece(5, 0, random.choice(list(SHAPES.values())))
            change_piece = False

        full_rows = check_full_rows(grid)
        for index in full_rows:
            remove_row(grid, index)

        draw_grid(win, grid)
        draw_next_piece(next_piece, win)
        pygame.display.update()

    pygame.quit()

def convert_shape_format(piece):
    positions = []
    format = piece.image()
    for i, line in enumerate(format):
        row = line  # Здесь исправили ошибку
        for j, column in enumerate(row):
            if column:
                positions.append((piece.x + j, piece.y + i))
    return positions

if __name__ == '__main__':
    main()