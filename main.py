import tkinter
import customtkinter
import pygame
from PIL import Image, ImageTk
from threading import *
import time
import math
from music_loader import load_supported_audio_files

customtkinter.set_appearance_mode("System") 
customtkinter.set_default_color_theme('blue') 

root = customtkinter.CTk()
root.title("Reproductor Choro MP3") #Título de la ventana
root.geometry("400x480") #Dimensiones de la ventana
pygame.mixer.init() #Iniciar mixer

songList = load_supported_audio_files("music")
albumcoverList = []
n = 0

def getAlbumCover(songName, n):
    if n >= len(albumcoverList):
        return
    image1 = Image.open(albumcoverList[n])
    image2 = image1.resize((200, 200))
    load = ImageTk.PhotoImage(image2)
    label1 = tkinter.Label(root, image=load)
    label1.image = load
    label1.place(relx=0.19, rely=0.06)

    strippedString = songName[6:-3]
    songNameLabel = tkinter.Label(text = strippedString, bg='#222222', fg='white')
    songNameLabel.place(relx=0.4, rely=0.6)

def progress(songIndex):
    a = pygame.mixer.Sound(f'{songList[songIndex]}')
    songLength = a.get_length() * 3
    for i in range(0, math.ceil(songLength)):
        time.sleep(.3)
        progressBar.set(pygame.mixer.music.get_pos() / 1000000)

def threading(songIndex):
    t1 = Thread(target=progress, args=(songIndex,), daemon=True)
    t1.start()

def playMusic():
    global n
    if not songList:
        print("No compatible audio files found in music/")
        return
    if n >= len(songList):
        n = 0
    currentSong = n
    songName = songList[currentSong]
    pygame.mixer.music.load(songName)
    pygame.mixer.music.play(loops = 0)
    pygame.mixer.music.set_volume(.5)
    threading(currentSong)
    getAlbumCover(songName, currentSong)

    n = currentSong + 1

def skipForward():
    playMusic()

def skipBackward():
    global n
    if not songList:
        print("No compatible audio files found in music/")
        return
    n -= 2
    playMusic()

def volume(value):
    pygame.mixer.music.set_volume(value)


playButton = customtkinter.CTkButton(master=root, text="Play", command=playMusic)
playButton.place(relx=0.5, rely=0.8, anchor=tkinter.CENTER)

skipFButton = customtkinter.CTkButton(master=root, text=">>", command=skipForward, width=2)
skipFButton.place(relx=0.75, rely=0.8, anchor=tkinter.CENTER)

skipBButton = customtkinter.CTkButton(master=root, text="<<", command=skipBackward, width=2)
skipBButton.place(relx=0.25, rely=0.8, anchor=tkinter.CENTER)

slider = customtkinter.CTkSlider(master=root, from_=0, to=1, command=volume, width=200)
slider.place(relx=0.5, rely=0.72, anchor=tkinter.CENTER)

progressBar = customtkinter.CTkProgressBar(master=root, progress_color='#e34646', width=225)
progressBar.place(relx=0.5, rely=0.65, anchor=tkinter.CENTER)

root.mainloop()