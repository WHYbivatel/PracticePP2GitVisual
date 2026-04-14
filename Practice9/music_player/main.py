import os
import sys
import pygame
from player import MusicPlayer


WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
GREEN = (50, 200, 50)
BLUE = (50, 120, 255)


def draw_text(screen, text, font, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_progress_bar(screen, x, y, width, height, progress):
    pygame.draw.rect(screen, GRAY, (x, y, width, height), border_radius=8)
    fill_width = int(width * progress)
    pygame.draw.rect(screen, GREEN, (x, y, fill_width, height), border_radius=8)


def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Music Player with Keyboard Controller")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("arial", 28)
    small_font = pygame.font.SysFont("arial", 22)

    music_folder = os.path.join(os.path.dirname(__file__), "music")
    player = MusicPlayer(music_folder)

    if not player.playlist:
        print("No audio files found in the music folder.")
        pygame.quit()
        sys.exit()

    running = True

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    player.play()
                elif event.key == pygame.K_s:
                    player.stop()
                elif event.key == pygame.K_n:
                    player.next_track()
                elif event.key == pygame.K_b:
                    player.previous_track()
                elif event.key == pygame.K_q:
                    running = False

        player.update_auto_next()

        current_track = player.get_current_track()
        current_pos = player.get_current_position()
        total_length = player.get_track_length()

        progress = 0
        if total_length > 0:
            progress = min(current_pos / total_length, 1)

        draw_text(screen, "Music Player", font, BLACK, 300, 30)
        draw_text(screen, f"Track: {current_track}", small_font, BLUE, 60, 100)

        status = "Playing" if player.is_playing else "Stopped"
        draw_text(screen, f"Status: {status}", small_font, BLACK, 60, 150)

        draw_text(
            screen,
            f"Time: {format_time(current_pos)} / {format_time(total_length)}",
            small_font,
            BLACK,
            60,
            200
        )

        draw_progress_bar(screen, 60, 250, 680, 25, progress)

        controls = "P = Play | S = Stop | N = Next | B = Previous | Q = Quit"
        draw_text(screen, controls, small_font, BLACK, 60, 320)

        pygame.display.flip()
        clock.tick(30)

    pygame.mixer.music.stop()
    pygame.quit()


if __name__ == "__main__":
    main()