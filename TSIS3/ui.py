import pygame

WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
GRAY = (170, 170, 170)
BTN = (80, 110, 180)
BTN_HOVER = (105, 135, 210)
INPUT_BG = (50, 50, 60)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen, font):
        mouse_pos = pygame.mouse.get_pos()
        color = BTN_HOVER if self.rect.collidepoint(mouse_pos) else BTN
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        txt = font.render(self.text, True, WHITE)
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class TextInput:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            elif len(self.text) < 16 and event.unicode.isprintable():
                self.text += event.unicode

    def draw(self, screen, font):
        pygame.draw.rect(screen, INPUT_BG, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        txt = font.render(self.text or "Enter name...", True, WHITE if self.text else GRAY)
        screen.blit(txt, (self.rect.x + 10, self.rect.y + 9))


def draw_centered_text(screen, text, font, color, x, y):
    surf = font.render(text, True, color)
    screen.blit(surf, surf.get_rect(center=(x, y)))


def draw_label_value(screen, font, color, label, value, x, y):
    surf = font.render(f"{label}: {value}", True, color)
    screen.blit(surf, (x, y))