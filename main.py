import tkinter

import customtkinter
import pygame
from PIL import Image, ImageTk

from audio_metadata import extract_audio_metadata
from music_loader import load_supported_audio_files
from playback_utils import mixer_elapsed_to_position, position_to_progress, progress_to_position

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.title("Reproductor Choro MP3")
root.geometry("420x520")
root.minsize(320, 420)
pygame.mixer.init()

song_list = load_supported_audio_files("music")
current_song_index = 0
current_song_path = None
current_song_duration = None
is_user_seeking = False
internal_progress_update = False
pending_seek_value = None
playback_start_offset_seconds = 0.0
paused_position_seconds = 0.0
is_paused = False
base_cover_image = None
rendered_cover = None


def set_song_title(text):
    song_name_label.configure(text=text)


def get_song_duration(song_path, metadata_duration):
    if metadata_duration and metadata_duration > 0:
        return metadata_duration
    try:
        duration = pygame.mixer.Sound(song_path).get_length()
        return duration if duration > 0 else None
    except pygame.error:
        return None


def render_cover_image():
    global rendered_cover
    if base_cover_image is None:
        cover_label.configure(image="", text="Sin portada")
        return
    target_size = max(120, min(300, cover_container.winfo_width() - 20, cover_container.winfo_height() - 20))
    if target_size <= 0:
        return
    image = base_cover_image.resize((target_size, target_size), Image.Resampling.LANCZOS)
    rendered_cover = ImageTk.PhotoImage(image)
    cover_label.configure(image=rendered_cover, text="")


def update_song_details(song_path):
    global current_song_duration, base_cover_image
    metadata = extract_audio_metadata(song_path)
    current_song_duration = get_song_duration(song_path, metadata.duration)
    set_song_title(metadata.title)
    base_cover_image = metadata.cover_image
    render_cover_image()
    if current_song_duration:
        progress_slider.configure(state="normal")
    else:
        progress_slider.configure(state="disabled")
    set_progress_slider(0.0)


def set_progress_slider(value):
    global internal_progress_update
    internal_progress_update = True
    progress_slider.set(value)
    internal_progress_update = False


def update_pause_button():
    pause_button.configure(text="Reanudar" if is_paused else "Pausar")


def get_current_position_seconds():
    if current_song_duration is None:
        return None
    if is_paused:
        return paused_position_seconds
    current_position_ms = pygame.mixer.music.get_pos()
    current_seconds = mixer_elapsed_to_position(current_position_ms, playback_start_offset_seconds)
    if current_seconds is None:
        return None
    return min(current_seconds, current_song_duration)


def play_song(index):
    global current_song_index, current_song_path, playback_start_offset_seconds, paused_position_seconds, is_paused
    if not song_list:
        print("No compatible audio files found in music/")
        return
    current_song_index = index % len(song_list)
    current_song_path = song_list[current_song_index]
    try:
        pygame.mixer.music.load(current_song_path)
        pygame.mixer.music.play(loops=0)
    except pygame.error as error:
        print(f"Could not play file {current_song_path}: {error}")
        return
    pygame.mixer.music.set_volume(volume_slider.get())
    playback_start_offset_seconds = 0.0
    paused_position_seconds = 0.0
    is_paused = False
    update_song_details(current_song_path)
    update_pause_button()
    pause_button.configure(state="normal")


def play_music():
    play_song(current_song_index)


def skip_forward():
    play_song(current_song_index + 1)


def skip_backward():
    play_song(current_song_index - 1)


def set_volume(value):
    pygame.mixer.music.set_volume(float(value))


def seek_to_progress(value):
    global playback_start_offset_seconds, paused_position_seconds
    if current_song_path is None:
        return
    target_seconds = progress_to_position(float(value), current_song_duration)
    if target_seconds is None:
        return
    try:
        if is_paused:
            pygame.mixer.music.load(current_song_path)
            pygame.mixer.music.play(loops=0, start=target_seconds)
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.set_pos(target_seconds)
    except pygame.error:
        try:
            pygame.mixer.music.load(current_song_path)
            pygame.mixer.music.play(loops=0, start=target_seconds)
            if is_paused:
                pygame.mixer.music.pause()
        except pygame.error:
            return
    playback_start_offset_seconds = target_seconds
    paused_position_seconds = target_seconds
    pygame.mixer.music.set_volume(volume_slider.get())
    set_progress_slider(position_to_progress(target_seconds, current_song_duration))


def toggle_pause():
    global is_paused, paused_position_seconds, playback_start_offset_seconds
    if current_song_path is None:
        return
    if is_paused:
        try:
            pygame.mixer.music.unpause()
        except pygame.error:
            return
        playback_start_offset_seconds = paused_position_seconds
        is_paused = False
    else:
        current_position = get_current_position_seconds()
        try:
            pygame.mixer.music.pause()
        except pygame.error:
            return
        paused_position_seconds = current_position if current_position is not None else 0.0
        is_paused = True
    update_pause_button()


def on_progress_drag(value):
    global pending_seek_value
    if internal_progress_update or not is_user_seeking:
        return
    pending_seek_value = float(value)


def on_seek_start(_event):
    global is_user_seeking, pending_seek_value
    is_user_seeking = True
    pending_seek_value = progress_slider.get()


def on_seek_end(_event):
    global is_user_seeking, pending_seek_value
    is_user_seeking = False
    seek_value = pending_seek_value if pending_seek_value is not None else progress_slider.get()
    pending_seek_value = None
    seek_to_progress(seek_value)


def refresh_progress():
    global paused_position_seconds
    if current_song_duration and not is_user_seeking:
        current_seconds = get_current_position_seconds()
        if current_seconds is not None:
            paused_position_seconds = current_seconds
            set_progress_slider(position_to_progress(current_seconds, current_song_duration))
    root.after(200, refresh_progress)


def on_window_resize(_event):
    render_cover_image()


root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

main_frame = customtkinter.CTkFrame(root)
main_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(0, weight=1)

cover_container = customtkinter.CTkFrame(main_frame)
cover_container.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))
cover_container.grid_columnconfigure(0, weight=1)
cover_container.grid_rowconfigure(0, weight=1)

cover_label = tkinter.Label(cover_container, bg="#222222", fg="white", text="Sin portada")
cover_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

song_name_label = customtkinter.CTkLabel(main_frame, text="Selecciona una canción", wraplength=360)
song_name_label.grid(row=1, column=0, sticky="ew", padx=8, pady=(4, 8))

progress_slider = customtkinter.CTkSlider(main_frame, from_=0, to=1, command=on_progress_drag)
progress_slider.grid(row=2, column=0, sticky="ew", padx=8, pady=6)
progress_slider.configure(state="disabled")
progress_slider.bind("<ButtonPress-1>", on_seek_start)
progress_slider.bind("<ButtonRelease-1>", on_seek_end)

volume_slider = customtkinter.CTkSlider(main_frame, from_=0, to=1, command=set_volume)
volume_slider.grid(row=3, column=0, sticky="ew", padx=8, pady=6)
volume_slider.set(0.5)
set_volume(0.5)

controls_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
controls_frame.grid(row=4, column=0, sticky="ew", padx=8, pady=(8, 6))
controls_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

skip_back_button = customtkinter.CTkButton(controls_frame, text="<<", command=skip_backward, width=44)
skip_back_button.grid(row=0, column=0, padx=6, sticky="ew")

play_button = customtkinter.CTkButton(controls_frame, text="Play", command=play_music)
play_button.grid(row=0, column=1, padx=6, sticky="ew")

pause_button = customtkinter.CTkButton(controls_frame, text="Pausar", command=toggle_pause, state="disabled")
pause_button.grid(row=0, column=2, padx=6, sticky="ew")

skip_forward_button = customtkinter.CTkButton(controls_frame, text=">>", command=skip_forward, width=44)
skip_forward_button.grid(row=0, column=3, padx=6, sticky="ew")

root.bind("<Configure>", on_window_resize)
refresh_progress()
root.mainloop()