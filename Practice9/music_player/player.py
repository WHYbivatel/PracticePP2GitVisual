import os
import pygame


class MusicPlayer:
    def __init__(self, music_folder: str):
        self.music_folder = music_folder
        self.playlist = self.load_playlist()
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.track_start_time = 0

    def load_playlist(self):
        supported_formats = (".mp3", ".wav", ".ogg")
        tracks = []

        if not os.path.exists(self.music_folder):
            print(f"Folder not found: {self.music_folder}")
            return tracks

        for file_name in os.listdir(self.music_folder):
            if file_name.lower().endswith(supported_formats):
                tracks.append(os.path.join(self.music_folder, file_name))

        tracks.sort()
        return tracks

    def get_current_track(self):
        if not self.playlist:
            return "No tracks loaded"
        return os.path.basename(self.playlist[self.current_index])

    def play(self):
        if not self.playlist:
            print("Playlist is empty.")
            return

        current_track = self.playlist[self.current_index]
        pygame.mixer.music.load(current_track)
        pygame.mixer.music.play()

        self.is_playing = True
        self.is_paused = False
        self.track_start_time = pygame.time.get_ticks()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False

    def next_track(self):
        if not self.playlist:
            return

        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous_track(self):
        if not self.playlist:
            return

        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def get_track_length(self):
        if not self.playlist:
            return 0

        try:
            track = pygame.mixer.Sound(self.playlist[self.current_index])
            return int(track.get_length())
        except pygame.error:
            return 0

    def get_current_position(self):
        if not self.is_playing:
            return 0

        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms == -1:
            return 0
        return pos_ms // 1000

    def update_auto_next(self):
        if self.is_playing and not pygame.mixer.music.get_busy():
            self.next_track()