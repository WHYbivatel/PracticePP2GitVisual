import pygame
import random
import sys

# -----------------------------
# Initialization
# -----------------------------
pygame.init()

# Window settings
WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20

# Grid size
COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game with Levels")

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 40)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)
RED = (220, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 120, 255)

# -----------------------------
# Game settings
# -----------------------------
INITIAL_SPEED = 7
LEVEL_UP_EVERY = 3      # next level every 3 foods
WALL_THICKNESS = 1      # thickness in cells


# -----------------------------
# Helper functions
# -----------------------------
def draw_text(text, font_obj, color, x, y):
    """Draw text on the screen."""
    img = font_obj.render(text, True, color)
    screen.blit(img, (x, y))


def get_walls_for_level(level):
    """
    Return a set of wall coordinates depending on level.
    Each wall coordinate is a tuple: (x, y)
    """
    walls = set()

    # Level 1: only border walls
    # Level 2+: add extra internal walls
    if level >= 2:
        # Horizontal wall in upper-middle
        for x in range(8, 22):
            walls.add((x, 8))

    if level >= 3:
        # Horizontal wall in lower-middle
        for x in range(8, 22):
            walls.add((x, 21))

    if level >= 4:
        # Vertical wall on left-middle
        for y in range(11, 19):
            walls.add((10, y))

    if level >= 5:
        # Vertical wall on right-middle
        for y in range(11, 19):
            walls.add((19, y))

    return walls


def generate_food(snake, walls):
    """
    Generate random food position so that it does not appear:
    - on the snake
    - on border walls
    - on internal walls
    """
    while True:
        x = random.randint(WALL_THICKNESS, COLS - WALL_THICKNESS - 1)
        y = random.randint(WALL_THICKNESS, ROWS - WALL_THICKNESS - 1)

        if (x, y) not in snake and (x, y) not in walls:
            return (x, y)


def draw_border_walls():
    """Draw border walls around the playing area."""
    # Top and bottom
    for x in range(COLS):
        pygame.draw.rect(screen, GRAY, (x * CELL_SIZE, 0, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(
            screen,
            GRAY,
            (x * CELL_SIZE, (ROWS - 1) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )

    # Left and right
    for y in range(ROWS):
        pygame.draw.rect(screen, GRAY, (0, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(
            screen,
            GRAY,
            ((COLS - 1) * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )


def draw_internal_walls(walls):
    """Draw internal level walls."""
    for wx, wy in walls:
        pygame.draw.rect(
            screen,
            BLUE,
            (wx * CELL_SIZE, wy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )


def draw_snake(snake):
    """Draw snake on the screen."""
    for i, segment in enumerate(snake):
        x, y = segment
        color = DARK_GREEN if i == 0 else GREEN
        pygame.draw.rect(
            screen,
            color,
            (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        )


def draw_food(food):
    """Draw food."""
    x, y = food
    pygame.draw.rect(
        screen,
        RED,
        (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    )


def show_game_over(score, level):
    """Display game over screen."""
    screen.fill(BLACK)
    draw_text("GAME OVER", big_font, RED, WIDTH // 2 - 120, HEIGHT // 2 - 70)
    draw_text(f"Score: {score}", font, WHITE, WIDTH // 2 - 50, HEIGHT // 2)
    draw_text(f"Level: {level}", font, WHITE, WIDTH // 2 - 45, HEIGHT // 2 + 40)
    draw_text("Press any key to exit", font, WHITE, WIDTH // 2 - 110, HEIGHT // 2 + 90)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False


# -----------------------------
# Main game function
# -----------------------------
def main():
    # Snake starts in center
    snake = [(COLS // 2, ROWS // 2)]
    direction = (1, 0)          # moving right
    next_direction = direction

    score = 0
    foods_eaten = 0
    level = 1
    speed = INITIAL_SPEED

    walls = get_walls_for_level(level)
    food = generate_food(snake, walls)

    running = True
    game_over = False

    while running:
        # -----------------------------
        # Event handling
        # -----------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Prevent instant reverse direction
                if event.key == pygame.K_UP and direction != (0, 1):
                    next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_direction = (1, 0)

        if game_over:
            show_game_over(score, level)
            break

        direction = next_direction

        # -----------------------------
        # Move snake
        # -----------------------------
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        # -----------------------------
        # Border collision / leaving playing area
        # -----------------------------
        # Leaving playing area
        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            game_over = True
            continue

        # Collision with border walls
        if (
            new_head[0] == 0 or
            new_head[0] == COLS - 1 or
            new_head[1] == 0 or
            new_head[1] == ROWS - 1
        ):
            game_over = True
            continue

        # Collision with snake body
        if new_head in snake:
            game_over = True
            continue

        # Collision with internal walls
        if new_head in walls:
            game_over = True
            continue

        # Add new head
        snake.insert(0, new_head)

        # -----------------------------
        # Food logic
        # -----------------------------
        if new_head == food:
            score += 1
            foods_eaten += 1

            # Level up every LEVEL_UP_EVERY foods
            new_level = foods_eaten // LEVEL_UP_EVERY + 1

            if new_level != level:
                level = new_level
                speed += 2  # increase speed on next level
                walls = get_walls_for_level(level)

            food = generate_food(snake, walls)
        else:
            # If no food eaten, remove tail
            snake.pop()

        # -----------------------------
        # Drawing
        # -----------------------------
        screen.fill(BLACK)

        draw_border_walls()
        draw_internal_walls(walls)
        draw_snake(snake)
        draw_food(food)

        # Score and level counters
        draw_text(f"Score: {score}", font, WHITE, 10, 10)
        draw_text(f"Level: {level}", font, WHITE, 10, 40)
        draw_text(f"Speed: {speed}", font, WHITE, 10, 70)

        pygame.display.flip()
        clock.tick(speed)

    pygame.quit()
    sys.exit()


# -----------------------------
# Run the game
# -----------------------------
if __name__ == "__main__":
    main()