import pygame
import random
import sys

# ---------------------------------
# Инициализация pygame
# ---------------------------------
pygame.init()

# Размер окна
WIDTH = 600
HEIGHT = 600
CELL = 20

# Размер сетки
COLS = WIDTH // CELL
ROWS = HEIGHT // CELL

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake with weighted disappearing food")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# ---------------------------------
# Цвета
# ---------------------------------
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
DARK_GREEN = (0, 120, 0)
WHITE = (255, 255, 255)
RED = (220, 50, 50)
YELLOW = (240, 220, 70)
BLUE = (70, 140, 255)
GRAY = (120, 120, 120)

# ---------------------------------
# Настройки игры
# ---------------------------------
FPS = 8

# Время жизни еды в миллисекундах
FOOD_LIFETIME = 5000  # 5 секунд

# Возможные типы еды:
# position -> координата
# weight -> сколько очков дает
# color -> цвет еды
FOOD_TYPES = [
    {"weight": 1, "color": RED},
    {"weight": 2, "color": YELLOW},
    {"weight": 3, "color": BLUE},
]


def draw_text(text, x, y, color=WHITE):
    """Рисует текст на экране."""
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def generate_food(snake):
    """
    Генерирует еду в случайной позиции,
    которая не занята змейкой.
    
    Также случайно выбирается 'вес' еды.
    """
    while True:
        x = random.randint(0, COLS - 1)
        y = random.randint(0, ROWS - 1)

        if (x, y) not in snake:
            food_type = random.choice(FOOD_TYPES)
            food = {
                "position": (x, y),
                "weight": food_type["weight"],
                "color": food_type["color"],
                "spawn_time": pygame.time.get_ticks()
            }
            return food


def draw_snake(snake):
    """Рисует змейку."""
    for i, (x, y) in enumerate(snake):
        # Голова темнее
        color = DARK_GREEN if i == 0 else GREEN
        pygame.draw.rect(screen, color, (x * CELL, y * CELL, CELL, CELL))


def draw_food(food):
    """Рисует еду."""
    x, y = food["position"]
    pygame.draw.rect(screen, food["color"], (x * CELL, y * CELL, CELL, CELL))

    # Показываем вес еды цифрой поверх квадрата
    text = font.render(str(food["weight"]), True, BLACK)
    text_rect = text.get_rect(center=(x * CELL + CELL // 2, y * CELL + CELL // 2))
    screen.blit(text, text_rect)


def game_over_screen(score):
    """Экран конца игры."""
    screen.fill(BLACK)
    draw_text("GAME OVER", WIDTH // 2 - 80, HEIGHT // 2 - 40, RED)
    draw_text(f"Score: {score}", WIDTH // 2 - 50, HEIGHT // 2, WHITE)
    draw_text("Press any key to exit", WIDTH // 2 - 110, HEIGHT // 2 + 40, GRAY)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False


def main():
    # Начальная змейка
    snake = [(10, 10), (9, 10), (8, 10)]

    # Направление движения
    dx = 1
    dy = 0

    score = 0

    # Генерируем первую еду
    food = generate_food(snake)

    running = True
    while running:
        clock.tick(FPS)

        # -----------------------------
        # Обработка событий клавиатуры
        # -----------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Запрещаем мгновенно двигаться в противоположную сторону
                if event.key == pygame.K_UP and dy != 1:
                    dx, dy = 0, -1
                elif event.key == pygame.K_DOWN and dy != -1:
                    dx, dy = 0, 1
                elif event.key == pygame.K_LEFT and dx != 1:
                    dx, dy = -1, 0
                elif event.key == pygame.K_RIGHT and dx != -1:
                    dx, dy = 1, 0

        # -----------------------------
        # Проверка: не исчезла ли еда
        # -----------------------------
        current_time = pygame.time.get_ticks()
        if current_time - food["spawn_time"] > FOOD_LIFETIME:
            # Если время жизни еды закончилось,
            # просто создаем новую еду в другом месте
            food = generate_food(snake)

        # -----------------------------
        # Движение змейки
        # -----------------------------
        head_x, head_y = snake[0]
        new_head = (head_x + dx, head_y + dy)

        # -----------------------------
        # Проверка столкновения со стеной
        # -----------------------------
        if (
            new_head[0] < 0 or new_head[0] >= COLS or
            new_head[1] < 0 or new_head[1] >= ROWS
        ):
            game_over_screen(score)
            break

        # -----------------------------
        # Проверка столкновения с собой
        # -----------------------------
        if new_head in snake:
            game_over_screen(score)
            break

        # Добавляем новую голову
        snake.insert(0, new_head)

        # -----------------------------
        # Проверка: съела ли змейка еду
        # -----------------------------
        if new_head == food["position"]:
            # Добавляем очки по весу еды
            score += food["weight"]

            # Чтобы змейка выросла, хвост НЕ удаляем
            # После съедения создаем новую еду
            food = generate_food(snake)
        else:
            # Если не съели еду, удаляем хвост
            snake.pop()

        # -----------------------------
        # Отрисовка
        # -----------------------------
        screen.fill(BLACK)

        draw_snake(snake)
        draw_food(food)

        draw_text(f"Score: {score}", 10, 10)

        # Показываем, сколько еще проживет еда
        time_left = max(0, (FOOD_LIFETIME - (current_time - food["spawn_time"])) // 1000)
        draw_text(f"Food timer: {time_left}", 10, 40)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()