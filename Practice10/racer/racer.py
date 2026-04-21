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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# FPS
# =========================
FPS = 60
FramePerSec = pygame.time.Clock()

# =========================
# COLORS
# =========================
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# =========================
# GAME SETTINGS
# =========================
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COINS_COLLECTED = 0
ROAD_SPEED = 6

# =========================
# FONTS
# =========================
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# =========================
# WINDOW
# =========================
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer Game")

# =========================
# LOAD FILES
# =========================
background = pygame.image.load(os.path.join(BASE_DIR, "AnimatedStreet.png")).convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Теперь у картинок прозрачный фон, поэтому используем convert_alpha()
player_img = pygame.image.load(os.path.join(BASE_DIR, "Player.png")).convert_alpha()
enemy_img = pygame.image.load(os.path.join(BASE_DIR, "Enemy.png")).convert_alpha()
coin_img = pygame.image.load(os.path.join(BASE_DIR, "Coin.png")).convert_alpha()

crash_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "crash.wav"))

# =========================
# RESIZE IMAGES
# =========================
player_img = pygame.transform.scale(player_img, (50, 100))
enemy_img = pygame.transform.scale(enemy_img, (50, 100))
coin_img = pygame.transform.scale(coin_img, (30, 30))

# =========================
# BACKGROUND POSITION
# =========================
bg_y1 = 0
bg_y2 = -SCREEN_HEIGHT

# =========================
# PLAYER CLASS
# =========================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, 520)

    def move(self):
        pressed_keys = pygame.key.get_pressed()

        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)

        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:
            self.rect.move_ip(5, 0)

# =========================
# ENEMY CLASS
# =========================
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        self.rect.centerx = random.randint(40, SCREEN_WIDTH - 40)
        self.rect.y = -120

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.reset_position()

# =========================
# COIN CLASS
# =========================
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = coin_img
        self.rect = self.image.get_rect()
        self.active = False
        self.hide()

    def spawn(self):
        self.rect.centerx = random.randint(40, SCREEN_WIDTH - 40)
        self.rect.y = -50
        self.active = True

    def move(self):
        if self.active:
            self.rect.move_ip(0, SPEED)

            if self.rect.top > SCREEN_HEIGHT:
                self.hide()

    def hide(self):
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
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_COIN, 2000)

# =========================
# GAME LOOP
# =========================
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == INC_SPEED:
            SPEED += 0.5

        if event.type == SPAWN_COIN:
            if not C1.active and random.randint(1, 100) <= 60:
                C1.spawn()

    # =========================
    # MOVE BACKGROUND
    # =========================
    bg_y1 += ROAD_SPEED
    bg_y2 += ROAD_SPEED

    if bg_y1 >= SCREEN_HEIGHT:
        bg_y1 = -SCREEN_HEIGHT
    if bg_y2 >= SCREEN_HEIGHT:
        bg_y2 = -SCREEN_HEIGHT

    DISPLAYSURF.blit(background, (0, bg_y1))
    DISPLAYSURF.blit(background, (0, bg_y2))

    # =========================
    # DRAW TEXT
    # =========================
    score_text = font_small.render("Score: " + str(SCORE), True, BLACK)
    DISPLAYSURF.blit(score_text, (10, 10))

    coins_text = font_small.render("Coins: " + str(COINS_COLLECTED), True, BLACK)
    coins_rect = coins_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    DISPLAYSURF.blit(coins_text, coins_rect)

    # =========================
    # DRAW AND MOVE SPRITES
    # =========================
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move()

    # =========================
    # COIN COLLISION
    # =========================
    collected_coin = pygame.sprite.spritecollideany(P1, coins)
    if collected_coin and collected_coin.active:
        COINS_COLLECTED += 1
        collected_coin.hide()

    # =========================
    # ENEMY COLLISION
    # =========================
    if pygame.sprite.spritecollideany(P1, enemies):
        crash_sound.play()
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()

        for entity in all_sprites:
            entity.kill()

        time.sleep(2)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)