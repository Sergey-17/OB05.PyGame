import pygame
import random

# Инициализация pygame
pygame.init()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # I - голубой
    (0, 0, 255),  # J - синий
    (255, 165, 0),  # L - оранжевый
    (255, 255, 0),  # O - желтый
    (0, 255, 0),  # S - зеленый
    (128, 0, 128),  # T - фиолетовый
    (255, 0, 0)  # Z - красный
]

# Настройки игры
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 6)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
GAME_AREA_LEFT = BLOCK_SIZE

# Фигуры тетрамино
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]]  # Z
]


class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]
        self.rotation = 0

    def rotate(self):
        # Поворот фигуры на 90 градусов по часовой стрелке
        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]

        for r in range(rows):
            for c in range(cols):
                rotated[c][rows - 1 - r] = self.shape[r][c]

        return rotated


class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Тетрис')
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.fall_speed = 0.5  # секунды
        self.fall_time = 0
        self.move_delay = 0.5  # задержка для непрерывного движения
        self.move_time = 0
        self.keys_pressed = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_DOWN: False
        }

    def new_piece(self):
        # Создание новой случайной фигуры
        shape = random.choice(SHAPES)
        return Tetromino(GRID_WIDTH // 2 - len(shape[0]) // 2, 0, shape)

    def valid_move(self, piece, x_offset=0, y_offset=0, rotated_shape=None):
        # Проверка допустимости движения фигуры
        shape = rotated_shape if rotated_shape else piece.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + x_offset
                    new_y = piece.y + y + y_offset
                    if (new_x < 0 or new_x >= GRID_WIDTH or
                            new_y >= GRID_HEIGHT or
                            (new_y >= 0 and self.grid[new_y][new_x])):
                        return False
        return True

    def lock_piece(self):
        # Фиксация фигуры на игровом поле
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color

        # Проверка заполненных линий
        self.clear_lines()

        # Создание новой фигуры
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()

        # Проверка на завершение игры
        if not self.valid_move(self.current_piece):
            self.game_over = True

    def clear_lines(self):
        # Удаление заполненных линий и подсчет очков
        lines_cleared = 0
        for y in range(GRID_HEIGHT):
            if all(self.grid[y]):
                lines_cleared += 1
                # Сдвиг всех линий выше вниз
                for y2 in range(y, 0, -1):
                    self.grid[y2] = self.grid[y2 - 1][:]
                self.grid[0] = [0 for _ in range(GRID_WIDTH)]

        # Подсчет очков
        if lines_cleared == 1:
            self.score += 100 * self.level
        elif lines_cleared == 2:
            self.score += 300 * self.level
        elif lines_cleared == 3:
            self.score += 500 * self.level
        elif lines_cleared == 4:
            self.score += 800 * self.level

        # Увеличение уровня
        self.level = self.score // 2000 + 1
        self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)

    def draw_grid(self):
        # Отрисовка игрового поля
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(
                    self.screen,
                    GRAY if self.grid[y][x] == 0 else self.grid[y][x],
                    (GAME_AREA_LEFT + x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                    0 if self.grid[y][x] else 1
                )

    def draw_piece(self, piece):
        # Отрисовка текущей фигуры
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen,
                        piece.color,
                        (GAME_AREA_LEFT + (piece.x + x) * BLOCK_SIZE, (piece.y + y) * BLOCK_SIZE, BLOCK_SIZE,
                         BLOCK_SIZE),
                        0
                    )

    def draw_next_piece(self):
        # Отрисовка следующей фигуры
        font = pygame.font.SysFont('comicsans', 20)
        label = font.render('Следующая:', 1, WHITE)

        sx = GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE + 20
        sy = 50

        self.screen.blit(label, (sx, sy))

        for y, row in enumerate(self.next_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        self.screen,
                        self.next_piece.color,
                        (sx + x * BLOCK_SIZE, sy + y * BLOCK_SIZE + 30, BLOCK_SIZE, BLOCK_SIZE),
                        0
                    )

    def draw_score(self):
        # Отрисовка счета и уровня
        font = pygame.font.SysFont('comicsans', 20)

        score_label = font.render(f'Счет: {self.score}', 1, WHITE)
        level_label = font.render(f'Уровень: {self.level}', 1, WHITE)

        sx = GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE + 20
        sy = 150

        self.screen.blit(score_label, (sx, sy))
        self.screen.blit(level_label, (sx, sy + 30))

    def draw_pause(self):
        # Отрисовка сообщения о паузе
        font = pygame.font.SysFont('comicsans', 40)
        label = font.render('ПАУЗА', 1, WHITE)

        self.screen.blit(label, (GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE // 2 - label.get_width() // 2,
                                 GRID_HEIGHT * BLOCK_SIZE // 2 - label.get_height() // 2))

    def draw_game_over(self):
        # Отрисовка сообщения о завершении игры
        font = pygame.font.SysFont('comicsans', 40)
        label = font.render('Игра окончена!', 1, WHITE)

        self.screen.blit(label, (GAME_AREA_LEFT + GRID_WIDTH * BLOCK_SIZE // 2 - label.get_width() // 2,
                                 GRID_HEIGHT * BLOCK_SIZE // 2 - label.get_height() // 2))

    def handle_continuous_movement(self, delta_time):
        # Обработка непрерывного движения при удержании клавиш
        self.move_time += delta_time

        if self.move_time >= self.move_delay:
            self.move_time = 0

            if self.keys_pressed[pygame.K_LEFT] and self.valid_move(self.current_piece, x_offset=-1):
                self.current_piece.x -= 1
            if self.keys_pressed[pygame.K_RIGHT] and self.valid_move(self.current_piece, x_offset=1):
                self.current_piece.x += 1
            if self.keys_pressed[pygame.K_DOWN] and self.valid_move(self.current_piece, y_offset=1):
                self.current_piece.y += 1

    def run(self):
        # Главный игровой цикл
        running = True
        last_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000  # в секундах
            last_time = current_time

            if not self.paused and not self.game_over:
                self.fall_time += delta_time
                self.handle_continuous_movement(delta_time)

            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:  # Пауза по кнопке P
                        self.paused = not self.paused

                    if not self.game_over and not self.paused:
                        if event.key == pygame.K_LEFT:
                            self.keys_pressed[pygame.K_LEFT] = True
                            if self.valid_move(self.current_piece, x_offset=-1):
                                self.current_piece.x -= 1
                        elif event.key == pygame.K_RIGHT:
                            self.keys_pressed[pygame.K_RIGHT] = True
                            if self.valid_move(self.current_piece, x_offset=1):
                                self.current_piece.x += 1
                        elif event.key == pygame.K_DOWN:
                            self.keys_pressed[pygame.K_DOWN] = True
                            if self.valid_move(self.current_piece, y_offset=1):
                                self.current_piece.y += 1
                        elif event.key == pygame.K_UP:
                            rotated_shape = self.current_piece.rotate()
                            if self.valid_move(self.current_piece, rotated_shape=rotated_shape):
                                self.current_piece.shape = rotated_shape
                        elif event.key == pygame.K_SPACE:
                            # Мгновенное падение
                            while self.valid_move(self.current_piece, y_offset=1):
                                self.current_piece.y += 1
                            self.lock_piece()

                if event.type == pygame.KEYUP:
                    if event.key in self.keys_pressed:
                        self.keys_pressed[event.key] = False

            # Автоматическое падение фигуры
            if not self.game_over and not self.paused and self.fall_time >= self.fall_speed:
                self.fall_time = 0
                if self.valid_move(self.current_piece, y_offset=1):
                    self.current_piece.y += 1
                else:
                    self.lock_piece()

            # Отрисовка
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_piece(self.current_piece)
            self.draw_next_piece()
            self.draw_score()

            if self.paused:
                self.draw_pause()
            elif self.game_over:
                self.draw_game_over()

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Tetris()
    game.run()