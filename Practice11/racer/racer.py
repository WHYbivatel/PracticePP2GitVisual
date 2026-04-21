import pygame
import sys
import random
import time
import os
from pygame.locals import *

# =========================
# INITIALIZATION
# =========================
pygame.init()
pygame.mixer.init()

# Путь к папке, где лежит текущий .py файл
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# FPS
# =========================
FPS = 60
FramePerSec = pygame.time.Clock()

# =========================
# COLORS
# =========================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# =========================
# SCREEN SETTINGS
# =========================
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Начальная скорость врага
SPEED = 5

# Скорость движения дороги
ROAD_SPEED = 6

# Счет: сколько врагов прошло вниз
SCORE = 0

# Сколько "веса монет" собрано
COINS_COLLECTED = 0

# После каждых N монет увеличиваем скорость врага
N = 5

# Чтобы скорость не увеличивалась много раз на одном и том же значении
LAST_SPEEDUP_STEP = 0

# =========================
# FONTS
# =========================
font_big = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font_big.render("Game Over", True, BLACK)

# =========================
# WINDOW
# =========================
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Game")

# =========================
# LOAD FILES
# =========================
# Загружаем фон дороги
background = pygame.image.load(os.path.join(BASE_DIR, "AnimatedStreet.png")).convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Загружаем машину игрока и врага
player_img = pygame.image.load(os.path.join(BASE_DIR, "Player.png")).convert_alpha()
enemy_img = pygame.image.load(os.path.join(BASE_DIR, "Enemy.png")).convert_alpha()

# Уменьшаем машины
player_img = pygame.transform.scale(player_img, (50, 100))
enemy_img = pygame.transform.scale(enemy_img, (50, 100))

# Загружаем одну исходную желтую монету
base_coin_img = pygame.image.load(os.path.join(BASE_DIR, "Coin.png")).convert_alpha()
base_coin_img = pygame.transform.scale(base_coin_img, (28, 28))

# Загружаем звук аварии
crash_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "crash.wav"))

# =========================
# FUNCTION FOR TINTING COINS
# =========================
def tint_image(image, tint_color):
    """
    Перекрашивает копию изображения.
    Лучше всего работает, если исходная картинка светлая/желтая.
    """
    tinted = image.copy()
    tinted.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

# =========================
# CREATE 3 COIN VARIANTS FROM ONE IMAGE
# =========================
# Желтая монета: вес 1
coin_yellow_img = tint_image(base_coin_img, (255, 255, 120, 255))

# Оранжевая монета: вес 2
coin_orange_img = tint_image(base_coin_img, (255, 180, 80, 255))

# Красная монета: вес 3
coin_red_img = tint_image(base_coin_img, (255, 120, 120, 255))

# =========================
# BACKGROUND POSITIONS
# =========================
# Два фона нужны для бесконечной прокрутки дороги
bg_y1 = 0
bg_y2 = -SCREEN_HEIGHT

# =========================
# PLAYER CLASS
# =========================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Картинка игрока
        self.image = player_img

        # Прямоугольник игрока
        self.rect = self.image.get_rect()

        # Начальная позиция игрока
        self.rect.center = (SCREEN_WIDTH // 2, 520)

    def move(self):
        # Получаем состояние клавиш
        pressed_keys = pygame.key.get_pressed()

        # Движение влево
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)

        # Движение вправо
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

# =========================
# ENEMY CLASS
# =========================
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Картинка врага
        self.image = enemy_img

        # Прямоугольник врага
        self.rect = self.image.get_rect()

        # Ставим врага выше экрана
        self.reset_position()

    def reset_position(self):
        # Случайная позиция по X
        self.rect.centerx = random.randint(40, SCREEN_WIDTH - 40)

        # Позиция выше экрана
        self.rect.y = -120

    def move(self):
        global SCORE

        # Двигаем врага вниз
        self.rect.move_ip(0, SPEED)

        # Если враг ушел за экран, возвращаем наверх
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.reset_position()

# =========================
# COIN CLASS
# =========================
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # По умолчанию ставим желтую монету
        self.image = coin_yellow_img
        self.rect = self.image.get_rect()

        # Вес монеты
        self.value = 1

        # Активна ли монета на экране
        self.active = False

        # Сразу прячем монету
        self.hide()

    def spawn(self):
        """
        Случайно выбираем тип монеты:
        yellow = 1
        orange = 2
        red = 3
        """
        coin_type = random.choices(
            population=["yellow", "orange", "red"],
            weights=[60, 30, 10],   # вероятности появления
            k=1
        )[0]

        if coin_type == "yellow":
            self.image = coin_yellow_img
            self.value = 1
        elif coin_type == "orange":
            self.image = coin_orange_img
            self.value = 2
        else:
            self.image = coin_red_img
            self.value = 3

        # После смены картинки обновляем rect
        self.rect = self.image.get_rect()

        # Ставим монету в случайную точку сверху
        self.rect.centerx = random.randint(40, SCREEN_WIDTH - 40)
        self.rect.y = -50

        self.active = True

    def move(self):
        # Двигаем монету вниз, если она активна
        if self.active:
            self.rect.move_ip(0, SPEED)

            # Если монета ушла вниз, прячем ее
            if self.rect.top > SCREEN_HEIGHT:
                self.hide()

    def hide(self):
        # Убираем монету за экран
        self.rect.center = (-100, -100)
        self.active = False

# =========================
# CREATE OBJECTS
# =========================
P1 = Player()
E1 = Enemy()
C1 = Coin()

# =========================
# GROUPS
# =========================
enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()
coins.add(C1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)

# =========================
# CUSTOM EVENTS
# =========================
# Появление монеты каждые 1.8 сек
SPAWN_COIN = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_COIN, 1800)

# =========================
# GAME LOOP
# =========================
while True:
    for event in pygame.event.get():
        # Закрытие окна
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # Появление новой монеты
        if event.type == SPAWN_COIN:
            if not C1.active:
                C1.spawn()

    # =========================
    # MOVE BACKGROUND
    # =========================
    # Двигаем оба фона вниз
    bg_y1 += ROAD_SPEED
    bg_y2 += ROAD_SPEED

    # Когда фон ушел вниз, переносим его наверх
    if bg_y1 >= SCREEN_HEIGHT:
        bg_y1 = -SCREEN_HEIGHT
    if bg_y2 >= SCREEN_HEIGHT:
        bg_y2 = -SCREEN_HEIGHT

    # Рисуем два фона
    DISPLAYSURF.blit(background, (0, bg_y1))
    DISPLAYSURF.blit(background, (0, bg_y2))

    # =========================
    # DRAW TEXT
    # =========================
    # Счет врагов
    score_text = font_small.render("Score: " + str(SCORE), True, BLACK)
    DISPLAYSURF.blit(score_text, (10, 10))

    # Счет монет
    coins_text = font_small.render("Coins: " + str(COINS_COLLECTED), True, BLACK)
    coins_rect = coins_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    DISPLAYSURF.blit(coins_text, coins_rect)

    # Можно показывать текущую скорость
    speed_text = font_small.render("Speed: " + str(SPEED), True, BLACK)
    DISPLAYSURF.blit(speed_text, (10, 35))

    # =========================
    # DRAW AND MOVE SPRITES
    # =========================
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # =========================
    # CHECK COIN COLLISION
    # =========================
    collected_coin = pygame.sprite.spritecollideany(P1, coins)
    if collected_coin and collected_coin.active:
        # Добавляем вес монеты
        COINS_COLLECTED += collected_coin.value

        # Прячем монету после сбора
        collected_coin.hide()

        # Проверяем, не пора ли увеличить скорость врага
        current_step = COINS_COLLECTED // N
        if current_step > LAST_SPEEDUP_STEP:
            SPEED += 1
            LAST_SPEEDUP_STEP = current_step

    # =========================
    # CHECK ENEMY COLLISION
    # =========================
    if pygame.sprite.spritecollideany(P1, enemies):
        crash_sound.play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()

        # Удаляем все объекты
        for entity in all_sprites:
            entity.kill()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    # =========================
    # UPDATE SCREEN
    # =========================
    pygame.display.update()
    FramePerSec.tick(FPS)