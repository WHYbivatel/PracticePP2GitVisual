import json
import random
from dataclasses import dataclass
from pathlib import Path

import pygame

import db
from config import (
    BG,
    BLACK,
    BLUE,
    CELL_SIZE,
    COLS,
    CYAN,
    DARK_GREEN,
    DARK_RED,
    FPS,
    FOOD_LIFETIME,
    GRAY,
    GREEN,
    HEIGHT,
    INITIAL_SPEED,
    LEVEL_UP_EVERY,
    LIGHT_GRAY,
    OBSTACLE_START_LEVEL,
    ORANGE,
    PANEL,
    POWERUP_EFFECT_TIME,
    POWERUP_LIFETIME,
    PURPLE,
    RED,
    ROWS,
    SNAKE_COLOR_CHOICES,
    WHITE,
    WIDTH,
    YELLOW,
)

SETTINGS_PATH = Path(__file__).with_name('settings.json')

FOOD_TYPES = [
    {'weight': 1, 'color': RED},
    {'weight': 2, 'color': YELLOW},
    {'weight': 3, 'color': BLUE},
]

POWERUP_TYPES = {
    'speed': {'color': ORANGE, 'label': 'Speed +', 'duration': POWERUP_EFFECT_TIME},
    'slow': {'color': CYAN, 'label': 'Slow', 'duration': POWERUP_EFFECT_TIME},
    'shield': {'color': PURPLE, 'label': 'Shield', 'duration': None},
}


@dataclass
class Button:
    rect: pygame.Rect
    label: str


class SettingsManager:
    def __init__(self):
        self.default = {
            'snake_color': list(SNAKE_COLOR_CHOICES[0]),
            'grid_on': True,
            'sound_on': False,
        }

    def load(self):
        if not SETTINGS_PATH.exists():
            self.save(self.default)
            return self.default.copy()
        with SETTINGS_PATH.open('r', encoding='utf-8') as f:
            data = json.load(f)
        merged = self.default.copy()
        merged.update(data)
        return merged

    def save(self, settings):
        with SETTINGS_PATH.open('w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)


class SnakeApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Snake Game TSIS3')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        self.big_font = pygame.font.SysFont('Arial', 40)
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load()
        self.username = ''
        self.personal_best = 0
        self.status_message = ''

    def run(self):
        try:
            db.init_db()
        except Exception as e:
            self.status_message = f'DB error: {e.__class__.__name__}'
        while True:
            action = self.main_menu()
            if action == 'quit':
                break
            if action == 'leaderboard':
                self.leaderboard_screen()
            elif action == 'settings':
                self.settings_screen()
            elif action == 'play':
                if self.username.strip():
                    try:
                        self.personal_best = db.get_personal_best(self.username.strip())
                    except Exception as e:
                        self.personal_best = 0
                        self.status_message = f'DB error: {e.__class__.__name__}'
                    self.game_loop()
        pygame.quit()

    # ---------- UI helpers ----------
    def draw_text(self, text, x, y, color=WHITE, font=None, center=False):
        font = font or self.font
        img = font.render(text, True, color)
        rect = img.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(img, rect)

    def button(self, x, y, w, h, label):
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=10)
        pygame.draw.rect(self.screen, LIGHT_GRAY, rect, 2, border_radius=10)
        self.draw_text(label, rect.centerx, rect.centery, center=True)
        return Button(rect, label)

    def draw_grid(self):
        if not self.settings.get('grid_on', True):
            return
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (35, 35, 45), (x, 140), (x, HEIGHT))
        for y in range(140, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (35, 35, 45), (0, y), (WIDTH, y))

    def play_area_to_screen(self, pos):
        x, y = pos
        return x * CELL_SIZE, 140 + y * CELL_SIZE

    def generate_food(self, snake, obstacles, poison_food):
        while True:
            pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
            if pos in snake or pos in obstacles:
                continue
            if poison_food and pos == poison_food['position']:
                continue
            food_type = random.choice(FOOD_TYPES)
            return {
                'position': pos,
                'weight': food_type['weight'],
                'color': food_type['color'],
                'spawn_time': pygame.time.get_ticks(),
            }

    def generate_poison_food(self, snake, obstacles, normal_food):
        while True:
            pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
            if pos in snake or pos in obstacles or pos == normal_food['position']:
                continue
            return {
                'position': pos,
                'color': DARK_RED,
                'spawn_time': pygame.time.get_ticks(),
            }

    def generate_powerup(self, snake, obstacles, normal_food, poison_food):
        while True:
            pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
            forbidden = {normal_food['position'], poison_food['position']}
            if pos in snake or pos in obstacles or pos in forbidden:
                continue
            kind = random.choice(list(POWERUP_TYPES.keys()))
            return {
                'position': pos,
                'kind': kind,
                'spawn_time': pygame.time.get_ticks(),
            }

    def valid_obstacle_spawn(self, pos, snake, obstacle_set):
        head = snake[0]
        hx, hy = head
        px, py = pos
        # keep area around head free so spawn does not trap snake immediately
        if abs(px - hx) <= 1 and abs(py - hy) <= 1:
            return False
        if pos in snake or pos in obstacle_set:
            return False
        return 1 <= px < COLS - 1 and 1 <= py < ROWS - 1

    def generate_obstacles(self, level, snake, existing_food_positions):
        if level < OBSTACLE_START_LEVEL:
            return set()
        obstacle_count = min(4 + level * 2, 18)
        obstacles = set()
        attempts = 0
        while len(obstacles) < obstacle_count and attempts < 3000:
            attempts += 1
            pos = (random.randint(2, COLS - 3), random.randint(2, ROWS - 3))
            if pos in existing_food_positions:
                continue
            if not self.valid_obstacle_spawn(pos, snake, obstacles):
                continue
            obstacles.add(pos)
        return obstacles

    def draw_snake(self, snake):
        snake_color = tuple(self.settings['snake_color'])
        for i, segment in enumerate(snake):
            sx, sy = self.play_area_to_screen(segment)
            color = tuple(max(c - 50, 0) for c in snake_color) if i == 0 else snake_color
            pygame.draw.rect(self.screen, color, (sx, sy, CELL_SIZE, CELL_SIZE), border_radius=4)

    def draw_food(self, food):
        fx, fy = self.play_area_to_screen(food['position'])
        pygame.draw.rect(self.screen, food['color'], (fx, fy, CELL_SIZE, CELL_SIZE), border_radius=4)
        self.draw_text(str(food['weight']), fx + CELL_SIZE // 2, fy + CELL_SIZE // 2, BLACK, self.small_font, True)

    def draw_poison_food(self, poison_food):
        fx, fy = self.play_area_to_screen(poison_food['position'])
        pygame.draw.rect(self.screen, poison_food['color'], (fx, fy, CELL_SIZE, CELL_SIZE), border_radius=4)
        self.draw_text('P', fx + CELL_SIZE // 2, fy + CELL_SIZE // 2, WHITE, self.small_font, True)

    def draw_powerup(self, powerup):
        fx, fy = self.play_area_to_screen(powerup['position'])
        color = POWERUP_TYPES[powerup['kind']]['color']
        pygame.draw.rect(self.screen, color, (fx, fy, CELL_SIZE, CELL_SIZE), border_radius=4)
        letter = powerup['kind'][0].upper()
        self.draw_text(letter, fx + CELL_SIZE // 2, fy + CELL_SIZE // 2, BLACK, self.small_font, True)

    def draw_obstacles(self, obstacles):
        for pos in obstacles:
            ox, oy = self.play_area_to_screen(pos)
            pygame.draw.rect(self.screen, GRAY, (ox, oy, CELL_SIZE, CELL_SIZE), border_radius=3)

    def save_result_safe(self, username, score, level):
        try:
            db.save_result(username, score, level)
            self.personal_best = max(self.personal_best, score)
            self.status_message = 'Result saved to PostgreSQL.'
        except Exception as e:
            self.status_message = f'Failed to save result: {e.__class__.__name__}'

    # ---------- Screens ----------
    def main_menu(self):
        selected = None
        input_box = pygame.Rect(WIDTH // 2 - 180, 150, 360, 50)
        while selected is None:
            self.screen.fill(BG)
            self.draw_text('Snake Game TSIS3', WIDTH // 2, 70, WHITE, self.big_font, True)
            self.draw_text('Enter username:', input_box.x, input_box.y - 30)
            pygame.draw.rect(self.screen, PANEL, input_box, border_radius=10)
            pygame.draw.rect(self.screen, LIGHT_GRAY, input_box, 2, border_radius=10)
            self.draw_text(self.username or 'Type here...', input_box.x + 15, input_box.y + 12, WHITE)

            buttons = [
                self.button(WIDTH // 2 - 120, 250, 240, 52, 'Play'),
                self.button(WIDTH // 2 - 120, 320, 240, 52, 'Leaderboard'),
                self.button(WIDTH // 2 - 120, 390, 240, 52, 'Settings'),
                self.button(WIDTH // 2 - 120, 460, 240, 52, 'Quit'),
            ]

            if self.status_message:
                self.draw_text(self.status_message, WIDTH // 2, 550, YELLOW, self.small_font, True)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'quit'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    elif event.key == pygame.K_RETURN:
                        if self.username.strip():
                            return 'play'
                    else:
                        if len(self.username) < 20 and event.unicode.isprintable() and event.unicode not in '\t\r\n':
                            self.username += event.unicode
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for b in buttons:
                        if b.rect.collidepoint(event.pos):
                            if b.label == 'Play' and self.username.strip():
                                selected = 'play'
                            elif b.label == 'Leaderboard':
                                selected = 'leaderboard'
                            elif b.label == 'Settings':
                                selected = 'settings'
                            elif b.label == 'Quit':
                                selected = 'quit'
            self.clock.tick(30)
        return selected

    def leaderboard_screen(self):
        while True:
            self.screen.fill(BG)
            self.draw_text('Leaderboard - Top 10', WIDTH // 2, 50, WHITE, self.big_font, True)
            back = self.button(WIDTH - 150, HEIGHT - 70, 110, 42, 'Back')
            headers = ['#', 'Username', 'Score', 'Level', 'Date']
            x_positions = [70, 130, 340, 450, 560]
            for x, header in zip(x_positions, headers):
                self.draw_text(header, x, 120, YELLOW)
            try:
                rows = db.get_top_scores(10)
            except Exception as e:
                rows = []
                self.draw_text(f'DB error: {e.__class__.__name__}', 60, 170, RED)
            for idx, row in enumerate(rows, start=1):
                y = 160 + idx * 38
                date_text = row['played_at'].strftime('%Y-%m-%d')
                values = [str(idx), row['username'], str(row['score']), str(row['level_reached']), date_text]
                for x, value in zip(x_positions, values):
                    self.draw_text(value, x, y, WHITE, self.small_font)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back.rect.collidepoint(event.pos):
                        return
            self.clock.tick(30)

    def settings_screen(self):
        color_index = 0
        current_color = tuple(self.settings['snake_color'])
        if current_color in SNAKE_COLOR_CHOICES:
            color_index = SNAKE_COLOR_CHOICES.index(current_color)
        while True:
            self.screen.fill(BG)
            self.draw_text('Settings', WIDTH // 2, 60, WHITE, self.big_font, True)
            grid_btn = self.button(180, 170, 440, 52, f"Grid overlay: {'ON' if self.settings['grid_on'] else 'OFF'}")
            sound_btn = self.button(180, 250, 440, 52, f"Sound: {'ON' if self.settings['sound_on'] else 'OFF'}")
            color_btn = self.button(180, 330, 440, 52, 'Change snake color')
            save_back = self.button(180, 440, 440, 52, 'Save & Back')
            preview_rect = pygame.Rect(WIDTH // 2 - 30, 395, 60, 60)
            pygame.draw.rect(self.screen, tuple(self.settings['snake_color']), preview_rect, border_radius=8)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if grid_btn.rect.collidepoint(event.pos):
                        self.settings['grid_on'] = not self.settings['grid_on']
                    elif sound_btn.rect.collidepoint(event.pos):
                        self.settings['sound_on'] = not self.settings['sound_on']
                    elif color_btn.rect.collidepoint(event.pos):
                        color_index = (color_index + 1) % len(SNAKE_COLOR_CHOICES)
                        self.settings['snake_color'] = list(SNAKE_COLOR_CHOICES[color_index])
                    elif save_back.rect.collidepoint(event.pos):
                        self.settings_manager.save(self.settings)
                        return
            self.clock.tick(30)

    def game_over_screen(self, score, level):
        retry = self.button(WIDTH // 2 - 150, 420, 300, 52, 'Retry')
        menu = self.button(WIDTH // 2 - 150, 490, 300, 52, 'Main Menu')
        while True:
            self.screen.fill(BG)
            self.draw_text('Game Over', WIDTH // 2, 120, RED, self.big_font, True)
            self.draw_text(f'Username: {self.username}', WIDTH // 2, 220, WHITE, self.font, True)
            self.draw_text(f'Final score: {score}', WIDTH // 2, 260, WHITE, self.font, True)
            self.draw_text(f'Level reached: {level}', WIDTH // 2, 300, WHITE, self.font, True)
            self.draw_text(f'Personal best: {max(self.personal_best, score)}', WIDTH // 2, 340, YELLOW, self.font, True)
            retry = self.button(WIDTH // 2 - 150, 420, 300, 52, 'Retry')
            menu = self.button(WIDTH // 2 - 150, 490, 300, 52, 'Main Menu')
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 'menu'
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if retry.rect.collidepoint(event.pos):
                        return 'retry'
                    if menu.rect.collidepoint(event.pos):
                        return 'menu'
            self.clock.tick(30)

    # ---------- Game loop ----------
    def game_loop(self):
        while True:
            snake = [(COLS // 2, ROWS // 2), (COLS // 2 - 1, ROWS // 2), (COLS // 2 - 2, ROWS // 2)]
            direction = (1, 0)
            next_direction = direction
            score = 0
            level = 1
            speed = INITIAL_SPEED
            foods_eaten = 0
            shield_ready = False
            speed_effect_until = 0
            slow_effect_until = 0

            temp_obstacles = set()
            normal_food = self.generate_food(snake, temp_obstacles, None)
            poison_food = self.generate_poison_food(snake, temp_obstacles, normal_food)
            obstacles = self.generate_obstacles(level, snake, {normal_food['position'], poison_food['position']})
            normal_food = self.generate_food(snake, obstacles, poison_food)
            poison_food = self.generate_poison_food(snake, obstacles, normal_food)
            powerup = None

            running = True
            saved = False
            while running:
                current_time = pygame.time.get_ticks()

                # Determine effective speed
                effective_speed = speed
                if current_time < speed_effect_until:
                    effective_speed = speed + 4
                if current_time < slow_effect_until:
                    effective_speed = max(4, speed - 3)
                self.clock.tick(effective_speed)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP and direction != (0, 1):
                            next_direction = (0, -1)
                        elif event.key == pygame.K_DOWN and direction != (0, -1):
                            next_direction = (0, 1)
                        elif event.key == pygame.K_LEFT and direction != (1, 0):
                            next_direction = (-1, 0)
                        elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                            next_direction = (1, 0)

                # Food timers
                if current_time - normal_food['spawn_time'] > FOOD_LIFETIME:
                    normal_food = self.generate_food(snake, obstacles, poison_food)
                if current_time - poison_food['spawn_time'] > FOOD_LIFETIME:
                    poison_food = self.generate_poison_food(snake, obstacles, normal_food)

                # Power-up spawn/disappear rules
                if powerup is None and random.random() < 0.01:
                    powerup = self.generate_powerup(snake, obstacles, normal_food, poison_food)
                if powerup and current_time - powerup['spawn_time'] > POWERUP_LIFETIME:
                    powerup = None

                direction = next_direction
                head_x, head_y = snake[0]
                dx, dy = direction
                new_head = (head_x + dx, head_y + dy)

                collision = False
                if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
                    collision = True
                if new_head[0] in (0, COLS - 1) or new_head[1] in (0, ROWS - 1):
                    collision = True
                if new_head in snake:
                    collision = True
                if new_head in obstacles:
                    collision = True

                if collision:
                    if shield_ready:
                        shield_ready = False
                        continue
                    running = False
                    if not saved:
                        self.save_result_safe(self.username.strip(), score, level)
                        saved = True
                    break

                snake.insert(0, new_head)

                ate_normal = new_head == normal_food['position']
                ate_poison = new_head == poison_food['position']
                ate_powerup = powerup and new_head == powerup['position']

                if ate_normal:
                    score += normal_food['weight']
                    foods_eaten += 1
                    new_level = foods_eaten // LEVEL_UP_EVERY + 1
                    if new_level != level:
                        level = new_level
                        speed += 1
                        obstacles = self.generate_obstacles(level, snake, {normal_food['position'], poison_food['position']})
                    normal_food = self.generate_food(snake, obstacles, poison_food)
                elif ate_poison:
                    # poison shortens snake by 2 segments; if too short -> game over
                    if len(snake) <= 3:
                        running = False
                        if not saved:
                            self.save_result_safe(self.username.strip(), score, level)
                            saved = True
                        break
                    snake.pop()
                    snake.pop()
                    poison_food = self.generate_poison_food(snake, obstacles, normal_food)
                else:
                    snake.pop()

                if ate_powerup:
                    kind = powerup['kind']
                    if kind == 'speed':
                        speed_effect_until = current_time + POWERUP_TYPES[kind]['duration']
                    elif kind == 'slow':
                        slow_effect_until = current_time + POWERUP_TYPES[kind]['duration']
                    elif kind == 'shield':
                        shield_ready = True
                    powerup = None

                if not ate_poison and new_head == poison_food['position']:
                    pass
                if ate_normal and poison_food['position'] in obstacles:
                    poison_food = self.generate_poison_food(snake, obstacles, normal_food)

                # redraw
                self.screen.fill(BG)
                pygame.draw.rect(self.screen, PANEL, (0, 0, WIDTH, 140))
                self.draw_grid()
                self.draw_obstacles(obstacles)
                self.draw_snake(snake)
                self.draw_food(normal_food)
                self.draw_poison_food(poison_food)
                if powerup:
                    self.draw_powerup(powerup)

                # HUD
                normal_time_left = max(0, (FOOD_LIFETIME - (current_time - normal_food['spawn_time'])) // 1000)
                poison_time_left = max(0, (FOOD_LIFETIME - (current_time - poison_food['spawn_time'])) // 1000)
                active_power = 'Shield ready' if shield_ready else 'None'
                if current_time < speed_effect_until:
                    active_power = 'Speed boost'
                if current_time < slow_effect_until:
                    active_power = 'Slow motion'
                self.draw_text(f'User: {self.username}', 16, 14)
                self.draw_text(f'Score: {score}', 16, 42)
                self.draw_text(f'Level: {level}', 16, 70)
                self.draw_text(f'Best: {self.personal_best}', 16, 98, YELLOW)
                self.draw_text(f'Speed: {effective_speed}', 220, 14)
                self.draw_text(f'Food timer: {normal_time_left}', 220, 42)
                self.draw_text(f'Poison timer: {poison_time_left}', 220, 70, RED)
                self.draw_text(f'Power-up: {active_power}', 220, 98, CYAN)
                if powerup:
                    remaining = max(0, (POWERUP_LIFETIME - (current_time - powerup['spawn_time'])) // 1000)
                    label = POWERUP_TYPES[powerup['kind']]['label']
                    self.draw_text(f'On field: {label} ({remaining}s)', 470, 14)
                self.draw_text('Shield ignores one collision.', 470, 42, LIGHT_GRAY, self.small_font)
                self.draw_text('P = poison, S/Sl/Sh = power-ups.', 470, 68, LIGHT_GRAY, self.small_font)

                pygame.display.flip()

            action = self.game_over_screen(score, level)
            if action == 'retry':
                continue
            return
