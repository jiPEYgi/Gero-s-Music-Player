import tkinter
import customtkinter
import pygame
from PIL import Image, ImageTk
from threading import *
import time
import math

customtkinter.set_appearance_mode("System") 
customtkinter.set_default_color_theme('blue') 

root = customtkinter.CTk()
root.title("Reproductor Choro MP3") #Título de la ventana
root.geometry("400x480") #Dimensiones de la ventana
pygame.mixer.init() #Iniciar mixer

songList = []
albumcoverList = []
n = a

def getAlbumCover(songName, n):
    image1 = Image.open(albumcoverList[n])
    image2 = image1.resize((200, 200))
    load = ImageTk.PhotoImage(image2)
    label1 = tkinter.Label(root, image=load)
    label1.image = load
    label1.place(relx=0.19, rely=0.06)

    strippedString = songName[6:-3]
    songNameLabel = tkinter.label(text = strippedString, bg='#222222', fg='white')
    songNameLabel.place(relx=0.4, rely=0.6)

def progress():
    a = pygame.mixer.sound(f'{songList[n]}')
    songLength = a.get_length() * 3
    for i in range(0, math.ceil(songLength)):
        time.sleep(.3)
        progressBar.set(pygame.mixer.music.get_pos() / 1000000)

def threading():
    t1 = Thread(target=progress)
    t1.start()

def playMusic():
    threading()
    global n
    currentSong = n
    if n > 2:
        n = 0
    songName = songList[n]
    pygame.mixer.music.load(songName)
    pygame.mixer.music.play(loops = 0)
    pygame.mixer.music.set_volume(.5)
    getAlbumCover(songName, n)

    n += 1

def skipForward():
    playMusic()

def skipBackward():
    global n
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