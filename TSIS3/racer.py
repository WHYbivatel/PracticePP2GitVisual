import os
import random
import pygame


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
RED = (220, 70, 70)
GREEN = (70, 200, 90)
BLUE = (60, 120, 220)
YELLOW = (240, 210, 70)
ORANGE = (245, 160, 70)
CYAN = (90, 220, 255)
GRAY = (110, 110, 110)
DARK = (28, 28, 35)
ROAD = (65, 65, 72)
LANE = (225, 225, 225)
OIL = (35, 35, 35)
PURPLE = (170, 90, 230)

WIDTH, HEIGHT = 400, 600
LANE_X = [80, 200, 320]

DIFFICULTY_SETTINGS = {
    "Easy": {
        "traffic_speed": 2.4,
        "road_speed": 2.2,
        "spawn_delay": 1700,
        "hazard_spawn_delay": 2600,
        "powerup_spawn_delay": 6500,
        "coin_spawn_delay": 1800,
        "distance_goal": 2200,
        "difficulty_step_distance": 700,
    },
    "Medium": {
        "traffic_speed": 3.0,
        "road_speed": 2.7,
        "spawn_delay": 1450,
        "hazard_spawn_delay": 2200,
        "powerup_spawn_delay": 5600,
        "coin_spawn_delay": 1600,
        "distance_goal": 2600,
        "difficulty_step_distance": 600,
    },
    "Hard": {
        "traffic_speed": 3.7,
        "road_speed": 3.2,
        "spawn_delay": 1200,
        "hazard_spawn_delay": 1900,
        "powerup_spawn_delay": 5000,
        "coin_spawn_delay": 1450,
        "distance_goal": 3000,
        "difficulty_step_distance": 500,
    },
}


def load_image(filename, use_alpha=True):
    path1 = os.path.join(BASE_DIR, filename)
    path2 = os.path.join(ASSETS_DIR, filename)
    path = path1 if os.path.exists(path1) else path2
    if os.path.exists(path):
        img = pygame.image.load(path)
        return img.convert_alpha() if use_alpha else img.convert()
    return None


def load_sound(filename):
    path1 = os.path.join(BASE_DIR, filename)
    path2 = os.path.join(ASSETS_DIR, filename)
    path = path1 if os.path.exists(path1) else path2
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error:
            return None
    return None


def tint_image(image, tint_color):
    tinted = image.copy()
    tinted.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted


class Player(pygame.sprite.Sprite):
    def __init__(self, settings, player_image=None):
        super().__init__()
        self.settings = settings
        self.base_speed = 5
        self.speed = 5
        self.shield = False
        self.repair = False
        self.slipping_timer = 0

        color_map = {
            "blue": BLUE,
            "green": GREEN,
            "red": RED,
        }

        if player_image is not None:
            base = pygame.transform.scale(player_image, (48, 90))
            color = color_map.get(settings["car_color"], BLUE)
            self.image = tint_image(base, color + (255,))
        else:
            self.image = pygame.Surface((48, 90), pygame.SRCALPHA)
            self.image.fill(color_map.get(settings["car_color"], BLUE))
            pygame.draw.rect(self.image, BLACK, (8, 10, 32, 15))
            pygame.draw.rect(self.image, BLACK, (8, 65, 32, 15))

        self.rect = self.image.get_rect(center=(LANE_X[1], 510))

    def update(self):
        pressed = pygame.key.get_pressed()

        if self.slipping_timer > 0:
            self.slipping_timer -= 1
            self.rect.x += random.choice([-2, -1, 1, 2])

        if pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.left < 35:
            self.rect.left = 35
        if self.rect.right > WIDTH - 35:
            self.rect.right = WIDTH - 35


class TrafficCar(pygame.sprite.Sprite):
    def __init__(self, speed, enemy_img=None, lane=None):
        super().__init__()

        if enemy_img is not None:
            self.image = pygame.transform.scale(enemy_img, (46, 88))
        else:
            self.image = pygame.Surface((46, 88), pygame.SRCALPHA)
            self.image.fill(RED)
            pygame.draw.rect(self.image, BLACK, (7, 12, 32, 12))
            pygame.draw.rect(self.image, BLACK, (7, 64, 32, 12))

        if lane is None:
            lane = random.choice(LANE_X)

        self.rect = self.image.get_rect(center=(lane, -80))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT + 20:
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self, speed, coin_img, lane=None):
        super().__init__()
        self.speed = speed

        yellow = tint_image(coin_img, (255, 255, 120, 255))
        orange = tint_image(coin_img, (255, 180, 80, 255))
        red = tint_image(coin_img, (255, 120, 120, 255))

        choice = random.choices(
            population=[("yellow", 1, yellow), ("orange", 2, orange), ("red", 3, red)],
            weights=[60, 30, 10],
            k=1,
        )[0]

        self.kind = choice[0]
        self.value = choice[1]
        self.image = choice[2]

        if lane is None:
            lane = random.choice(LANE_X)

        self.rect = self.image.get_rect(center=(lane, -30))

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT + 10:
            self.kill()


class Hazard(pygame.sprite.Sprite):
    def __init__(self, speed, hazard_type, lane=None):
        super().__init__()
        self.speed = speed
        self.hazard_type = hazard_type
        self.lane = lane if lane is not None else random.choice(LANE_X)

        if hazard_type == "oil":
            self.image = pygame.Surface((54, 24), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, OIL, (0, 0, 54, 24))
            self.effect = "slip"
        elif hazard_type == "slow":
            self.image = pygame.Surface((70, 18), pygame.SRCALPHA)
            pygame.draw.rect(self.image, ORANGE, (0, 0, 70, 18), border_radius=6)
            self.effect = "slow"
        elif hazard_type == "barrier":
            self.image = pygame.Surface((82, 22), pygame.SRCALPHA)
            pygame.draw.rect(self.image, YELLOW, (0, 0, 82, 22), border_radius=4)
            pygame.draw.line(self.image, BLACK, (0, 11), (82, 11), 3)
            self.effect = "crash"
        elif hazard_type == "bump":
            self.image = pygame.Surface((62, 16), pygame.SRCALPHA)
            pygame.draw.rect(self.image, GRAY, (0, 0, 62, 16), border_radius=6)
            self.effect = "bump"
        elif hazard_type == "moving_barrier":
            self.image = pygame.Surface((74, 22), pygame.SRCALPHA)
            pygame.draw.rect(self.image, YELLOW, (0, 0, 74, 22), border_radius=6)
            pygame.draw.line(self.image, BLACK, (8, 11), (66, 11), 3)
            self.effect = "crash"
        else:
            self.image = pygame.Surface((74, 22), pygame.SRCALPHA)
            pygame.draw.rect(self.image, PURPLE, (0, 0, 74, 22), border_radius=6)
            self.effect = "nitro_strip"

        self.rect = self.image.get_rect(center=(self.lane, -30))
        self.dx = random.choice([-1, 1]) if hazard_type == "moving_barrier" else 0

    def update(self):
        self.rect.y += self.speed

        if self.hazard_type == "moving_barrier":
            self.rect.x += self.dx * 1.4
            if self.rect.left < 40 or self.rect.right > WIDTH - 40:
                self.dx *= -1

        if self.rect.top > HEIGHT + 20:
            self.kill()


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, speed, kind, lane=None):
        super().__init__()
        self.kind = kind
        self.speed = speed
        self.spawn_time = pygame.time.get_ticks()
        self.timeout_ms = 4500

        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        color = CYAN
        label = "N"

        if kind == "shield":
            color = GREEN
            label = "S"
        elif kind == "repair":
            color = YELLOW
            label = "R"

        pygame.draw.circle(self.image, color, (16, 16), 15)
        pygame.draw.circle(self.image, BLACK, (16, 16), 15, 2)

        font = pygame.font.SysFont("Verdana", 18, bold=True)
        txt = font.render(label, True, BLACK)
        self.image.blit(txt, txt.get_rect(center=(16, 16)))

        if lane is None:
            lane = random.choice(LANE_X)

        self.rect = self.image.get_rect(center=(lane, -35))

    def expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.timeout_ms

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT + 10 or self.expired():
            self.kill()


class RacerGame:
    def __init__(self, screen, settings, username):
        self.screen = screen
        self.settings = settings
        self.username = username

        self.width = WIDTH
        self.height = HEIGHT
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Verdana", 18)
        self.small_font = pygame.font.SysFont("Verdana", 14)
        self.big_font = pygame.font.SysFont("Verdana", 42, bold=True)

        self.config = DIFFICULTY_SETTINGS.get(settings["difficulty"], DIFFICULTY_SETTINGS["Easy"])

        self.traffic_speed = self.config["traffic_speed"]
        self.road_speed = self.config["road_speed"]
        self.base_spawn_delay = self.config["spawn_delay"]
        self.hazard_spawn_delay = self.config["hazard_spawn_delay"]
        self.powerup_spawn_delay = self.config["powerup_spawn_delay"]
        self.coin_spawn_delay = self.config["coin_spawn_delay"]
        self.distance_goal = self.config["distance_goal"]
        self.step_distance = self.config["difficulty_step_distance"]

        self.last_traffic_spawn = 0
        self.last_hazard_spawn = 0
        self.last_powerup_spawn = 0
        self.last_coin_spawn = 0
        self.last_scale_step = 0

        self.score = 0
        self.distance = 0.0
        self.coins = 0
        self.power_bonus = 0
        self.running = True
        self.result = None
        self.active_powerup = None
        self.active_powerup_end = 0
        self.safe_lane = None
        self.safe_lane_end = 0

        self.bg_y1 = 0
        self.bg_y2 = -HEIGHT

        self.background = load_image("AnimatedStreet.png", use_alpha=False)
        self.player_img = load_image("Player.png")
        self.enemy_img = load_image("Enemy.png")
        self.coin_base_img = load_image("Coin.png")
        self.crash_sound = load_sound("crash.wav")

        if self.background is not None:
            self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))

        if self.coin_base_img is not None:
            self.coin_base_img = pygame.transform.scale(self.coin_base_img, (28, 28))
        else:
            self.coin_base_img = pygame.Surface((28, 28), pygame.SRCALPHA)
            pygame.draw.circle(self.coin_base_img, YELLOW, (14, 14), 12)
            pygame.draw.circle(self.coin_base_img, BLACK, (14, 14), 12, 2)

        self.player = Player(settings, self.player_img)
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.traffic_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.hazard_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()

    def lane_is_occupied(self, lane_x, y_min=-140, y_max=140):
        """
        Проверяет, есть ли в полосе объект рядом с верхней зоной спавна.
        Это нужно, чтобы coin/powerup не появлялись прямо внутри машин,
        hazards и других объектов.
        """
        groups_to_check = [
            self.traffic_group,
            self.hazard_group,
            self.coin_group,
            self.powerup_group,
        ]

        for group in groups_to_check:
            for obj in group:
                if abs(obj.rect.centerx - lane_x) < 35 and y_min <= obj.rect.y <= y_max:
                    return True
        return False

    def get_free_lane(self):
        """
        Возвращает случайную свободную полосу.
        Если все полосы заняты, возвращает None.
        """
        free_lanes = [lane for lane in LANE_X if not self.lane_is_occupied(lane)]
        if not free_lanes:
            return None
        return random.choice(free_lanes)

    def draw_fallback_background(self):
        self.screen.fill((24, 110, 40))
        pygame.draw.rect(self.screen, ROAD, (40, 0, 320, HEIGHT))
        pygame.draw.line(self.screen, WHITE, (120, 0), (120, HEIGHT), 4)
        pygame.draw.line(self.screen, WHITE, (280, 0), (280, HEIGHT), 4)

        for y in range(-20, HEIGHT, 40):
            pygame.draw.rect(
                self.screen,
                LANE,
                (196, (y + int(self.bg_y1)) % HEIGHT, 8, 22),
                border_radius=3,
            )

    def move_background(self):
        self.bg_y1 += self.road_speed
        self.bg_y2 += self.road_speed

        if self.bg_y1 >= HEIGHT:
            self.bg_y1 = -HEIGHT
        if self.bg_y2 >= HEIGHT:
            self.bg_y2 = -HEIGHT

        if self.background is not None:
            self.screen.blit(self.background, (0, self.bg_y1))
            self.screen.blit(self.background, (0, self.bg_y2))
        else:
            self.draw_fallback_background()

    def spawn_traffic(self, now):
        if now - self.last_traffic_spawn >= self.base_spawn_delay:
            self.last_traffic_spawn = now

            possible_lanes = LANE_X[:]
            if self.safe_lane in possible_lanes:
                possible_lanes.remove(self.safe_lane)

            random.shuffle(possible_lanes)

            chosen_lane = None
            for lane in possible_lanes:
                if not self.lane_is_occupied(lane, y_min=-180, y_max=120):
                    chosen_lane = lane
                    break

            if chosen_lane is None:
                return

            traffic = TrafficCar(self.traffic_speed, self.enemy_img, lane=chosen_lane)
            traffic.rect.centerx = chosen_lane
            traffic.rect.y = -80
            self.traffic_group.add(traffic)

    def spawn_coin(self, now):
        if now - self.last_coin_spawn >= self.coin_spawn_delay:
            self.last_coin_spawn = now

            free_lane = self.get_free_lane()
            if free_lane is None:
                return

            coin = Coin(self.traffic_speed, self.coin_base_img, lane=free_lane)
            coin.rect.centerx = free_lane
            coin.rect.y = -30
            self.coin_group.add(coin)

    def spawn_hazard(self, now):
        if now - self.last_hazard_spawn >= self.hazard_spawn_delay:
            self.last_hazard_spawn = now

            self.safe_lane = random.choice(LANE_X)
            self.safe_lane_end = now + 2600

            hazard_type = random.choice(["oil", "slow", "barrier", "bump", "moving_barrier"])
            lanes = [x for x in LANE_X if x != self.safe_lane]
            random.shuffle(lanes)

            chosen_lane = None
            for lane in lanes:
                if not self.lane_is_occupied(lane, y_min=-180, y_max=120):
                    chosen_lane = lane
                    break

            if chosen_lane is None:
                return

            h = Hazard(self.traffic_speed, hazard_type, lane=chosen_lane)
            self.hazard_group.add(h)

    def spawn_powerup(self, now):
        if self.active_powerup is not None:
            return

        if len(self.powerup_group) > 0:
            return

        if now - self.last_powerup_spawn >= self.powerup_spawn_delay:
            self.last_powerup_spawn = now

            free_lane = self.get_free_lane()
            if free_lane is None:
                return

            kind = random.choice(["nitro", "shield", "repair"])
            p = PowerUp(self.traffic_speed, kind, lane=free_lane)
            p.rect.centerx = free_lane
            p.rect.y = -35
            self.powerup_group.add(p)

    def update_difficulty(self):
        current_step = int(self.distance // self.step_distance)
        if current_step > self.last_scale_step:
            self.last_scale_step = current_step
            self.traffic_speed = min(self.traffic_speed + 0.2, 6.0)
            self.road_speed = min(self.road_speed + 0.1, 5.0)
            self.base_spawn_delay = max(900, self.base_spawn_delay - 80)
            self.hazard_spawn_delay = max(1300, self.hazard_spawn_delay - 70)

    def apply_powerup(self, kind):
        now = pygame.time.get_ticks()

        if kind == "nitro":
            self.active_powerup = "Nitro"
            self.active_powerup_end = now + 4000
            self.player.speed = 7
            self.power_bonus += 20

        elif kind == "shield":
            self.active_powerup = "Shield"
            self.active_powerup_end = 0
            self.player.shield = True
            self.power_bonus += 15

        elif kind == "repair":
            self.active_powerup = "Repair"
            self.active_powerup_end = now + 1200
            self.player.repair = True
            self.power_bonus += 10

    def clear_powerup(self):
        self.active_powerup = None
        self.active_powerup_end = 0
        self.player.speed = self.player.base_speed
        self.player.shield = False
        self.player.repair = False

    def update_powerup_state(self):
        if self.active_powerup == "Nitro" and pygame.time.get_ticks() >= self.active_powerup_end:
            self.clear_powerup()
        elif self.active_powerup == "Repair" and pygame.time.get_ticks() >= self.active_powerup_end:
            self.clear_powerup()

    def process_collisions(self):
        traffic_hit = pygame.sprite.spritecollideany(self.player, self.traffic_group)
        if traffic_hit:
            if self.player.shield:
                traffic_hit.kill()
                self.clear_powerup()
            elif self.player.repair:
                traffic_hit.kill()
                self.clear_powerup()
            else:
                self.game_over()
                return

        coin_hit = pygame.sprite.spritecollideany(self.player, self.coin_group)
        if coin_hit:
            self.coins += coin_hit.value
            self.score += coin_hit.value * 5
            coin_hit.kill()

        power_hit = pygame.sprite.spritecollideany(self.player, self.powerup_group)
        if power_hit:
            self.powerup_group.empty()
            self.apply_powerup(power_hit.kind)

        hazard_hit = pygame.sprite.spritecollideany(self.player, self.hazard_group)
        if hazard_hit:
            effect = hazard_hit.effect

            if effect == "crash":
                if self.player.shield or self.player.repair:
                    hazard_hit.kill()
                    self.clear_powerup()
                else:
                    self.game_over()
                    return

            elif effect == "slip":
                self.player.slipping_timer = 25
                hazard_hit.kill()

            elif effect == "slow":
                self.player.speed = 3
                pygame.time.set_timer(pygame.USEREVENT + 99, 1000, loops=1)
                hazard_hit.kill()

            elif effect == "bump":
                self.distance = max(0, self.distance - 20)
                hazard_hit.kill()

            elif effect == "nitro_strip":
                self.apply_powerup("nitro")
                hazard_hit.kill()

    def game_over(self):
        if self.settings.get("sound", True) and self.crash_sound is not None:
            self.crash_sound.play()

        final_score = int(self.score + self.distance + self.coins * 10 + self.power_bonus)
        self.result = {
            "name": self.username,
            "score": final_score,
            "distance": round(self.distance, 1),
            "coins": self.coins,
        }

        self.show_game_over_screen()

    def draw_hud(self):
        remaining = max(0, int(self.distance_goal - self.distance))

        hud1 = self.font.render(f"Score: {int(self.score)}", True, WHITE)
        hud2 = self.font.render(f"Coins: {self.coins}", True, WHITE)
        hud3 = self.font.render(f"Dist: {int(self.distance)}", True, WHITE)
        hud4 = self.small_font.render(f"Left: {remaining}", True, WHITE)

        self.screen.blit(hud1, (10, 10))
        self.screen.blit(hud2, (WIDTH - 110, 10))
        self.screen.blit(hud3, (10, 34))
        self.screen.blit(hud4, (WIDTH - 85, 38))

        if self.safe_lane is not None and pygame.time.get_ticks() < self.safe_lane_end:
            lane_text = "Safe lane: "
            if self.safe_lane == LANE_X[0]:
                lane_text += "Left"
            elif self.safe_lane == LANE_X[1]:
                lane_text += "Center"
            else:
                lane_text += "Right"

            txt = self.small_font.render(lane_text, True, CYAN)
            self.screen.blit(txt, (10, 58))

        if self.active_powerup:
            if self.active_powerup_end > 0:
                sec_left = max(0, (self.active_powerup_end - pygame.time.get_ticks()) // 1000 + 1)
                ptext = f"{self.active_powerup}: {sec_left}s"
            else:
                ptext = f"{self.active_powerup}: active"

            power_label = self.small_font.render(ptext, True, YELLOW)
            self.screen.blit(power_label, (WIDTH - 145, 58))

    def show_game_over_screen(self):
        retry_rect = pygame.Rect(100, 390, 200, 44)
        menu_rect = pygame.Rect(100, 450, 200, 44)

        while True:
            self.screen.fill(DARK)
            title = self.big_font.render("Game Over", True, RED)
            self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 120)))

            lines = [
                f"Player: {self.username}",
                f"Score: {self.result['score']}",
                f"Distance: {int(self.result['distance'])}",
                f"Coins: {self.result['coins']}",
            ]

            y = 200
            for line in lines:
                txt = self.font.render(line, True, WHITE)
                self.screen.blit(txt, txt.get_rect(center=(WIDTH // 2, y)))
                y += 34

            pygame.draw.rect(self.screen, (80, 140, 90), retry_rect, border_radius=8)
            pygame.draw.rect(self.screen, (90, 90, 120), menu_rect, border_radius=8)

            retry_txt = self.font.render("Retry", True, WHITE)
            menu_txt = self.font.render("Main Menu", True, WHITE)

            self.screen.blit(retry_txt, retry_txt.get_rect(center=retry_rect.center))
            self.screen.blit(menu_txt, menu_txt.get_rect(center=menu_rect.center))

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if retry_rect.collidepoint(event.pos):
                        self.__init__(self.screen, self.settings, self.username)
                        self.run()
                        return
                    if menu_rect.collidepoint(event.pos):
                        self.running = False
                        return

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.USEREVENT + 99:
                self.player.speed = 7 if self.active_powerup == "Nitro" else self.player.base_speed

    def run(self):
        while self.running:
            self.handle_events()

            now = pygame.time.get_ticks()

            if self.safe_lane is not None and now >= self.safe_lane_end:
                self.safe_lane = None

            self.move_background()
            self.spawn_traffic(now)
            self.spawn_coin(now)
            self.spawn_hazard(now)
            self.spawn_powerup(now)
            self.update_difficulty()
            self.update_powerup_state()

            self.player_group.update()
            self.traffic_group.update()
            self.coin_group.update()
            self.hazard_group.update()
            self.powerup_group.update()

            self.process_collisions()

            self.player_group.draw(self.screen)
            self.traffic_group.draw(self.screen)
            self.coin_group.draw(self.screen)
            self.hazard_group.draw(self.screen)
            self.powerup_group.draw(self.screen)

            self.draw_hud()

            self.distance += self.road_speed * 0.35
            self.score += 0.03 * self.road_speed

            if self.distance >= self.distance_goal:
                self.result = {
                    "name": self.username,
                    "score": int(self.score + self.distance + self.coins * 10 + self.power_bonus + 100),
                    "distance": round(self.distance, 1),
                    "coins": self.coins,
                }
                self.show_game_over_screen()
                self.running = False

            pygame.display.update()
            self.clock.tick(60)

        return self.result