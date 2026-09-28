import tkinter
from tkinter import filedialog

import customtkinter
import pygame
from PIL import Image, ImageTk

from audio_metadata import extract_audio_metadata
from music_loader import load_supported_audio_files
from playback_utils import (
    calculate_locked_cover_size,
    mixer_elapsed_to_position,
    position_to_progress,
    progress_to_position,
    resolve_play_button_text,
    resolve_playback_action,
)

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# Red accent palette used throughout the UI.
RED = ("#B71C1C", "#EF5350")
RED_HOVER = ("#8E0000", "#C62828")

root = customtkinter.CTk()
root.title("Reproductor Choro MP3")
root.geometry("460x620")
root.minsize(340, 460)
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
current_rendered_size = None
current_rendered_image_id = None
current_rendered_song_path = None
resize_after_id = None


def set_song_artist(text):
    artist_name_label.configure(text=text)


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


def get_available_cover_dimensions():
    w = main_frame.winfo_width()
    h = main_frame.winfo_height()
    if w <= 1 or h <= 1:
        w = max(100, root.winfo_width() - 24)
        h = max(100, root.winfo_height() - 24)

    other_widgets = (top_bar, artist_name_label, song_name_label, progress_slider, volume_slider, controls_frame)
    measured_other_h = sum(widget.winfo_height() for widget in other_widgets if widget.winfo_ismapped())
    fixed_vertical = (measured_other_h + 62) if measured_other_h > 0 else 240
    avail_w = max(100, w - 16)
    avail_h = max(100, h - fixed_vertical)
    return avail_w, avail_h


def render_cover_image(force=False):
    global rendered_cover, current_rendered_size, current_rendered_image_id, current_rendered_song_path
    avail_w, avail_h = get_available_cover_dimensions()
    target_size = calculate_locked_cover_size(avail_w, avail_h)
    image_id = id(base_cover_image) if base_cover_image is not None else None

    if (
        not force
        and target_size == current_rendered_size
        and image_id == current_rendered_image_id
        and current_song_path == current_rendered_song_path
    ):
        return

    cover_container.configure(width=target_size, height=target_size)
    current_rendered_size = target_size
    current_rendered_image_id = image_id
    current_rendered_song_path = current_song_path

    if base_cover_image is None:
        rendered_cover = None
        cover_label.configure(image="", text="Sin portada")
        return

    image = base_cover_image.resize((target_size, target_size), Image.Resampling.LANCZOS)
    rendered_cover = ImageTk.PhotoImage(image)
    cover_label.configure(image=rendered_cover, text="")


def update_song_details(song_path):
    global current_song_duration, base_cover_image
    metadata = extract_audio_metadata(song_path)
    current_song_duration = get_song_duration(song_path, metadata.duration)
    set_song_artist(metadata.artist)
    set_song_title(metadata.title)
    base_cover_image = metadata.cover_image
    render_cover_image(force=True)
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


def is_music_busy():
    try:
        return pygame.mixer.music.get_busy()
    except pygame.error:
        return False


def update_play_button():
    is_playing = bool(current_song_path) and is_music_busy() and not is_paused
    play_button.configure(text=resolve_play_button_text(is_paused, is_playing))


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
    update_play_button()


def toggle_playback():
    global is_paused, paused_position_seconds
    if not song_list:
        print("No compatible audio files found in music/")
        return
    action = resolve_playback_action(is_paused, is_music_busy())
    if action == "play":
        play_song(current_song_index)
        return
    if current_song_path is None:
        play_song(current_song_index)
        return
    if action == "resume":
        try:
            pygame.mixer.music.unpause()
        except pygame.error:
            return
        is_paused = False
    else:
        current_position = get_current_position_seconds()
        try:
            pygame.mixer.music.pause()
        except pygame.error:
            return
        paused_position_seconds = current_position if current_position is not None else 0.0
        is_paused = True
    update_play_button()


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
        pygame.mixer.music.load(current_song_path)
        pygame.mixer.music.play(loops=0, start=target_seconds)
        if is_paused:
            pygame.mixer.music.pause()
    except pygame.error as error:
        print(f"Could not seek in file {current_song_path}: {error}")
        return
    playback_start_offset_seconds = target_seconds
    paused_position_seconds = target_seconds
    pygame.mixer.music.set_volume(volume_slider.get())
    set_progress_slider(position_to_progress(target_seconds, current_song_duration))


def on_progress_drag(value):
    global pending_seek_value
    if internal_progress_update:
        return
    pending_seek_value = float(value)


def on_seek_start(_event):
    global is_user_seeking, pending_seek_value
    is_user_seeking = True
    if pending_seek_value is None:
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
    update_play_button()
    root.after(200, refresh_progress)


def update_label_wraplength():
    wrap = max(260, root.winfo_width() - 48)
    if "artist_name_label" in globals():
        artist_name_label.configure(wraplength=wrap)
    if "song_name_label" in globals():
        song_name_label.configure(wraplength=wrap)


def _on_debounced_resize():
    global resize_after_id
    resize_after_id = None
    update_label_wraplength()
    render_cover_image()


def schedule_cover_render(delay_ms=30):
    global resize_after_id
    if resize_after_id is not None:
        root.after_cancel(resize_after_id)
    resize_after_id = root.after(delay_ms, _on_debounced_resize)


def on_window_resize(event):
    if event.widget != root:
        return
    schedule_cover_render()


root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

main_frame = customtkinter.CTkFrame(root)
main_frame.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)


def replace_song_library(new_song_list):
    global song_list, current_song_index, current_song_path, current_song_duration
    global playback_start_offset_seconds, paused_position_seconds, is_paused, base_cover_image
    song_list = new_song_list
    current_song_index = 0
    current_song_path = None
    current_song_duration = None
    playback_start_offset_seconds = 0.0
    paused_position_seconds = 0.0
    is_paused = False
    base_cover_image = None
    try:
        pygame.mixer.music.stop()
    except pygame.error:
        pass
    set_song_artist("")
    set_progress_slider(0.0)
    progress_slider.configure(state="disabled")
    render_cover_image(force=True)
    update_play_button()


def select_music_folder():
    selected_directory = filedialog.askdirectory(title="Selecciona una carpeta con música")
    if not selected_directory:
        return
    selected_song_list = load_supported_audio_files(selected_directory)
    if not selected_song_list:
        set_song_artist("")
        set_song_title("La carpeta no contiene archivos .wav, .mp3 o .flac")
        return
    replace_song_library(selected_song_list)
    set_song_artist("")
    set_song_title(f"Carpeta cargada ({len(song_list)} canciones)")


top_bar = customtkinter.CTkFrame(main_frame, fg_color="transparent")
top_bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
top_bar.grid_columnconfigure(0, weight=1)

add_folder_button = customtkinter.CTkButton(
    top_bar,
    text="+ Carpeta",
    width=96,
    command=select_music_folder,
    fg_color=RED,
    hover_color=RED_HOVER,
)
add_folder_button.grid(row=0, column=1, sticky="e")

cover_container = customtkinter.CTkFrame(main_frame, width=300, height=300)
cover_container.grid(row=1, column=0, padx=8, pady=(0, 4))
cover_container.grid_propagate(False)
cover_container.grid_columnconfigure(0, weight=1)
cover_container.grid_rowconfigure(0, weight=1)

cover_label = tkinter.Label(cover_container, bg="#222222", fg="white", text="Sin portada")
cover_label.grid(row=0, column=0, sticky="nsew")

artist_name_label = customtkinter.CTkLabel(
    main_frame,
    text="",
    font=customtkinter.CTkFont(size=14),
    text_color=("gray60", "gray75"),
    wraplength=360,
)
artist_name_label.grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 0))

song_name_label = customtkinter.CTkLabel(
    main_frame,
    text="Selecciona una canción",
    font=customtkinter.CTkFont(size=16, weight="bold"),
    wraplength=360,
)
song_name_label.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 4))

progress_slider = customtkinter.CTkSlider(
    main_frame,
    from_=0,
    to=1,
    command=on_progress_drag,
    button_color=RED,
    button_hover_color=RED_HOVER,
    progress_color=RED,
)
progress_slider.grid(row=4, column=0, sticky="ew", padx=8, pady=6)
progress_slider.configure(state="disabled")
progress_slider.bind("<ButtonPress-1>", on_seek_start)
progress_slider.bind("<ButtonRelease-1>", on_seek_end)

volume_slider = customtkinter.CTkSlider(
    main_frame,
    from_=0,
    to=1,
    command=set_volume,
    button_color=RED,
    button_hover_color=RED_HOVER,
    progress_color=RED,
)
volume_slider.grid(row=5, column=0, sticky="ew", padx=8, pady=6)
volume_slider.set(0.5)
set_volume(0.5)

controls_frame = customtkinter.CTkFrame(main_frame, fg_color="transparent")
controls_frame.grid(row=6, column=0, sticky="ew", padx=8, pady=(8, 6))
controls_frame.grid_columnconfigure((0, 1, 2), weight=1)

button_style = {"fg_color": RED, "hover_color": RED_HOVER}
skip_back_button = customtkinter.CTkButton(controls_frame, text="<<", command=skip_backward, width=44, **button_style)
skip_back_button.grid(row=0, column=0, padx=6, sticky="ew")

play_button = customtkinter.CTkButton(controls_frame, text="Play", command=toggle_playback, **button_style)
play_button.grid(row=0, column=1, padx=6, sticky="ew")

skip_forward_button = customtkinter.CTkButton(controls_frame, text=">>", command=skip_forward, width=44, **button_style)
skip_forward_button.grid(row=0, column=2, padx=6, sticky="ew")

root.bind("<Configure>", on_window_resize)
refresh_progress()
root.mainloop()
