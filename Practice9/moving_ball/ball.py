import pygame


class Ball:
    def __init__(self, x: int, y: int, radius: int, color: tuple[int, int, int], screen_width: int, screen_height: int):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.step = 20

    def move(self, dx: int, dy: int):
        new_x = self.x + dx
        new_y = self.y + dy

        # Проверка границ экрана
        if self.radius <= new_x <= self.screen_width - self.radius:
            self.x = new_x

        if self.radius <= new_y <= self.screen_height - self.radius:
            self.y = new_y

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)