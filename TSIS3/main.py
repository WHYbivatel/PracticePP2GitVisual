import pygame
import sys

from racer import RacerGame
from ui import (
    Button,
    TextInput,
    draw_centered_text,
    draw_label_value,
)
from persistence import (
    load_settings,
    save_settings,
    load_leaderboard,
    save_score,
)

pygame.init()

WIDTH, HEIGHT = 400, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSIS 3 Racer Game")

CLOCK = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
DARK = (28, 28, 35)
GRAY = (170, 170, 170)
RED = (220, 70, 70)

TITLE_FONT = pygame.font.SysFont("Verdana", 28, bold=True)
FONT = pygame.font.SysFont("Verdana", 20)
SMALL_FONT = pygame.font.SysFont("Verdana", 16)

SETTINGS = load_settings()
LEADERBOARD = load_leaderboard()


def run_game(username: str, settings: dict):
    game = RacerGame(SCREEN, settings, username)
    return game.run()


def main_menu():
    play_btn = Button(120, 180, 160, 44, "Play")
    leaderboard_btn = Button(120, 240, 160, 44, "Leaderboard")
    settings_btn = Button(120, 300, 160, 44, "Settings")
    quit_btn = Button(120, 360, 160, 44, "Quit")

    while True:
        SCREEN.fill(DARK)
        draw_centered_text(SCREEN, "Racer Game", TITLE_FONT, WHITE, WIDTH // 2, 70)
        draw_centered_text(
            SCREEN,
            "Advanced Driving, Leaderboard & Power-Ups",
            SMALL_FONT,
            GRAY,
            WIDTH // 2,
            105,
        )

        for btn in (play_btn, leaderboard_btn, settings_btn, quit_btn):
            btn.draw(SCREEN, FONT)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if play_btn.handle_event(event):
                username = username_screen()
                if username is not None:
                    result = run_game(username, SETTINGS)
                    if result:
                        save_score(result)
                return

            if leaderboard_btn.handle_event(event):
                leaderboard_screen()

            if settings_btn.handle_event(event):
                settings_screen()

            if quit_btn.handle_event(event):
                pygame.quit()
                sys.exit()

        CLOCK.tick(FPS)


def username_screen():
    input_box = TextInput(80, 230, 240, 42)
    start_btn = Button(120, 310, 160, 44, "Start")
    back_btn = Button(120, 370, 160, 44, "Back")

    while True:
        SCREEN.fill(DARK)
        draw_centered_text(SCREEN, "Enter Username", TITLE_FONT, WHITE, WIDTH // 2, 110)
        draw_centered_text(
            SCREEN,
            "This name will be saved in leaderboard",
            SMALL_FONT,
            GRAY,
            WIDTH // 2,
            145,
        )

        input_box.draw(SCREEN, FONT)
        start_btn.draw(SCREEN, FONT)
        back_btn.draw(SCREEN, FONT)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            input_box.handle_event(event)

            if start_btn.handle_event(event):
                name = input_box.text.strip()
                if name:
                    return name

            if back_btn.handle_event(event):
                return None

        CLOCK.tick(FPS)


def settings_screen():
    sound_btn = Button(120, 210, 160, 40, "")
    color_btn = Button(120, 270, 160, 40, "")
    difficulty_btn = Button(120, 330, 160, 40, "")
    back_btn = Button(120, 410, 160, 44, "Back")

    color_cycle = ["blue", "green", "red"]
    difficulty_cycle = ["Easy", "Medium", "Hard"]

    while True:
        SCREEN.fill(DARK)
        draw_centered_text(SCREEN, "Settings", TITLE_FONT, WHITE, WIDTH // 2, 90)

        sound_btn.text = f"Sound: {'On' if SETTINGS['sound'] else 'Off'}"
        color_btn.text = f"Car: {SETTINGS['car_color'].title()}"
        difficulty_btn.text = f"Difficulty: {SETTINGS['difficulty']}"

        sound_btn.draw(SCREEN, FONT)
        color_btn.draw(SCREEN, FONT)
        difficulty_btn.draw(SCREEN, FONT)
        back_btn.draw(SCREEN, FONT)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if sound_btn.handle_event(event):
                SETTINGS["sound"] = not SETTINGS["sound"]
                save_settings(SETTINGS)

            if color_btn.handle_event(event):
                idx = color_cycle.index(SETTINGS["car_color"])
                SETTINGS["car_color"] = color_cycle[(idx + 1) % len(color_cycle)]
                save_settings(SETTINGS)

            if difficulty_btn.handle_event(event):
                idx = difficulty_cycle.index(SETTINGS["difficulty"])
                SETTINGS["difficulty"] = difficulty_cycle[(idx + 1) % len(difficulty_cycle)]
                save_settings(SETTINGS)

            if back_btn.handle_event(event):
                return

        CLOCK.tick(FPS)


def leaderboard_screen():
    back_btn = Button(120, 530, 160, 40, "Back")

    while True:
        SCREEN.fill(DARK)
        draw_centered_text(SCREEN, "Top 10 Leaderboard", TITLE_FONT, WHITE, WIDTH // 2, 55)

        entries = load_leaderboard()

        y = 105
        header = SMALL_FONT.render("Rank  Name        Score   Dist", True, WHITE)
        SCREEN.blit(header, (42, y))
        y += 28

        if not entries:
            draw_centered_text(SCREEN, "No scores yet", FONT, GRAY, WIDTH // 2, 180)
        else:
            for i, item in enumerate(entries[:10], start=1):
                line = f"{i:>2}.  {item['name'][:10]:<10}  {item['score']:>5}  {int(item['distance']):>5}"
                text = SMALL_FONT.render(line, True, WHITE)
                SCREEN.blit(text, (35, y))
                y += 28

        back_btn.draw(SCREEN, FONT)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if back_btn.handle_event(event):
                return

        CLOCK.tick(FPS)


if __name__ == "__main__":
    while True:
        main_menu()