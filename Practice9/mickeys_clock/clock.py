import os
import sys
from datetime import datetime

import pygame


class MickeyClock:
    def __init__(self) -> None:
        pygame.init()

        self.width = 900
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Mickey's Clock")

        self.clock = pygame.time.Clock()
        self.running = True

        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.images_dir = os.path.join(self.base_dir, "images")

        self.bg_color = (245, 245, 245)
        self.text_color = (200, 70, 60)

        self.base_image = self.load_image("mickey_base.png")
        self.left_hand_image = self.load_image("mickey_left.png")
        self.right_hand_image = self.load_image("mickey_right.png")

        self.base_image = pygame.transform.smoothscale(self.base_image, (520, 520))
        self.left_hand_image = pygame.transform.smoothscale(self.left_hand_image, (320, 320))
        self.right_hand_image = pygame.transform.smoothscale(self.right_hand_image, (320, 320))

        self.base_rect = self.base_image.get_rect(center=(self.width // 2, self.height // 2 + 40))

        # Подгонка положения рук
        self.left_center = (self.width // 2 - 2, self.height // 2 + 40)
        self.right_center = (self.width // 2 + 2, self.height // 2 + 40)

        self.font = pygame.font.SysFont("consolas", 48, bold=True)

        # Для проверки точек
        self.show_debug = False

    def load_image(self, filename: str) -> pygame.Surface:
        path = os.path.join(self.images_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image not found: {path}")
        return pygame.image.load(path).convert_alpha()

    def get_current_time(self) -> tuple[int, int]:
        now = datetime.now()
        return now.minute, now.second

    def get_angles(self, minute: int, second: int) -> tuple[int, int]:
        return minute * 6, second * 6

    def rotate_hand(self, image: pygame.Surface, center_pos: tuple[int, int], angle: float):
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=center_pos)
        return rotated_image, rotated_rect

    def draw_time_text(self, minute: int, second: int) -> None:
        time_str = f"{minute:02d}:{second:02d}"
        text_surface = self.font.render(time_str, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.width // 2, 70))
        self.screen.blit(text_surface, text_rect)

    def draw(self) -> None:
        minute, second = self.get_current_time()
        minute_angle, second_angle = self.get_angles(minute, second)

        self.screen.fill(self.bg_color)

        # Сначала база
        self.screen.blit(self.base_image, self.base_rect)

        # Потом руки поверх базы, чтобы они точно были видны
        left_rotated, left_rect = self.rotate_hand(
            self.left_hand_image,
            self.left_center,
            -second_angle
        )
        self.screen.blit(left_rotated, left_rect)

        right_rotated, right_rect = self.rotate_hand(
            self.right_hand_image,
            self.right_center,
            -minute_angle
        )
        self.screen.blit(right_rotated, right_rect)

        if self.show_debug:
            pygame.draw.circle(self.screen, (255, 0, 0), self.left_center, 5)
            pygame.draw.circle(self.screen, (0, 0, 255), self.right_center, 5)

        self.draw_time_text(minute, second)
        pygame.display.flip()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()