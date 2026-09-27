#======================import modules===================
import sys
import os
import random
import subprocess as sp
import tkinter as tk
from tkinter import messagebox as mb

import pygame

#=======================prompt====================
if hasattr(sys, "_MEIPASS") or "__compiled__" in globals() or "__nuitka_binary_dir" in globals():
    root = tk.Tk()
    root.withdraw()
    show = mb.askyesno("确认", "是否弹出资源文件夹")
    root.destroy()

def open_folder(p):
    if not os.path.isdir(p):
        return
    if sys.platform == "darwin":         
        sp.Popen(["open", p])
    elif os.name == "nt":                
        os.startfile(p)
    else:                              
        sp.Popen(["xdg-open", p])

if hasattr(sys, "_MEIPASS"):                               
    target = sys._MEIPASS
elif "__compiled__" in globals() or "__nuitka_binary_dir" in globals(): 
    target = os.path.dirname(os.path.abspath(sys.argv[0]))
else:                                                        
    target = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()

try:
    if show: open_folder(target)
except NameError:
    pass

#========================change dir====================
if "__file__" in globals(): os.chdir(os.path.dirname(os.path.abspath(__file__)))

#=======================temp dir path=================
if hasattr(sys, "_MEIPASS"):
    print(sys._MEIPASS)
elif "__compiled__" in globals() or "__nuitka_binary_dir" in globals():
    print(os.path.dirname(os.path.abspath(sys.argv[0])))

#======================constant varibles==================
FILE = os.path.join(os.path.expanduser("~"), "pygame_whack_a_mole_score.txt")
WIDTH, HEIGHT = 1000, 800
INITIAL_TIME = 30
MOLE_SHOW_TIME = 1.5
MOLE_HIDE_TIME = 0.4

#=======================define fuctions====================
def path(*name):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, *name)

    elif "__compiled__" in globals() or "__nuitka_binary_dir" in globals():
        base = os.path.dirname(os.path.abspath(sys.argv[0]))

    else:
        base = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()

    return os.path.join(base, *name)

def show_error(prompt, error):
    font = pygame.font.SysFont(None, 32)
    small = pygame.font.SysFont(None, 22)

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                waiting = False
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((50, 0, 0))

        title = font.render(prompt, True, (255, 120, 120))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 300)))

        detail = small.render(str(error), True, (255, 255, 255))
        screen.blit(detail, detail.get_rect(center=(WIDTH // 2, 400)))

        hint = small.render("press any key to continue", True, (180, 180, 180))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 500)))

        pygame.display.flip()
        pygame.time.delay(30)

def show_mole_at(hole):
    mole_rect.x = hole[0]
    mole_rect.y = hole[1]

def hide_mole():
    global mole_rect
    mole_rect.x = -200
    mole_rect.y = -200

def play_sound(sound):
    if sound:
        sound.play()

def save_score():
    global latest_score, last_score
    last_score = score
    if score > latest_score:
        latest_score = score
    try:
        with open(FILE, "w", encoding="utf-8") as f:
            f.write(str(latest_score) + "\n" + str(last_score))
    except Exception as e:
        show_error("failed to save score", str(e))

def reset_game():
    global score, time_left, game_over, mole_visible, mole_timer, paused, music_started
    score = 0
    time_left = INITIAL_TIME
    game_over = False
    paused = False
    mole_visible = False
    mole_timer = 0
    hide_mole()
    if bg_music:
        pygame.mixer.music.play(-1)
        music_started = True

#=====================pygame setup=====================
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
pygame.display.set_caption("打地鼠")

#=========================load assets==================
try:
    icon = pygame.image.load(path("assets", "icon", "icon.png"))
    pygame.display.set_icon(icon)
except Exception:
    pass

try:
    font_small = pygame.font.Font(path("assets", "fonts", "hiraginosansgb.ttc"), 20)
except Exception as e:
    show_error("failed to load font", str(e))
    font_small = pygame.font.SysFont(None, 20)

try:
    whacked = pygame.mixer.Sound(path("assets", "music", "whacked.mp3"))
    over = pygame.mixer.Sound(path("assets", "music", "over.mp3"))
    pygame.mixer.music.load(path("assets", "music", "bg_music.mp3"))
    pygame.mixer.music.set_volume(0.2)
    bg_music = True
except Exception as e:
    show_error("failed to load music", str(e))
    bg_music = None

try:
    mole = pygame.image.load(path("assets", "images", "mole.png")).convert_alpha()
    bg = pygame.image.load(path("assets", "images", "bg.png")).convert()
    start = pygame.image.load(path("assets", "images", "start.png")).convert()
    end = pygame.image.load(path("assets", "images", "end.png")).convert()
except Exception as e:
    show_error("failed to load image", str(e))
    mole = pygame.Surface((100, 80), pygame.SRCALPHA)
    bg = pygame.Surface((WIDTH, HEIGHT))
    bg.fill((34, 139, 34))
    start = pygame.Surface((WIDTH, HEIGHT))
    start.fill((20, 20, 30))
    end = pygame.Surface((WIDTH, HEIGHT))
    end.fill((40, 0, 0))

#=========================varibles====================
score = 0
time_left = INITIAL_TIME
clock = pygame.time.Clock()
whacked = None
over = None

holes = [(150, 350), (440, 350), (780, 330), (260, 495), (650, 510)]

mole_rect = mole.get_rect()
mole_visible = False
mole_timer = 0

#=====================score file========================
try:
    with open(FILE, "r", encoding="utf-8") as f:
        latest_score, last_score = [int(w) for w in f.readlines()]
except (FileNotFoundError, ValueError):
    latest_score, last_score = 0, 0

hide_mole()

#=======================game state===================
running = True
game_started = False
game_over = False
paused = False
music_started = False

#=====================game loop===================
while running:
    dt = clock.tick(60) / 1000

    #===================event loop=====================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                pygame.display.toggle_fullscreen()
            
            elif not game_started:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                else:
                    game_started = True
                    if bg_music:
                        pygame.mixer.music.play(-1)
                        music_started = True
                continue

            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False

            elif event.key == pygame.K_r:
                reset_game()

            elif event.key == pygame.K_p and not game_over:
                if not paused:
                    if bg_music:
                        pygame.mixer.music.pause()
                    paused = True
                else:
                    if bg_music:
                        pygame.mixer.music.unpause()
                    paused = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_started and not game_over and not paused:
                if mole_visible and mole_rect.collidepoint(event.pos):
                    score += 1
                    play_sound(whacked)
                    mole_visible = False
                    mole_timer = 0
                    hide_mole()

    if not game_started:
        screen.blit(start, (0, 0))
        pygame.display.flip()
        continue

    if game_started and not game_over and not paused:
        time_left -= dt
        if time_left <= 0:
            time_left = 0
            game_over = True
            play_sound(over)
            if bg_music:
                pygame.mixer.music.stop()
            music_started = False
            save_score()

        mole_timer += dt
        if not mole_visible and mole_timer >= MOLE_HIDE_TIME:
            show_mole_at(random.choice(holes))
            mole_visible = True
            mole_timer = 0
        elif mole_visible and mole_timer >= MOLE_SHOW_TIME:
            mole_visible = False
            mole_timer = 0
            hide_mole()

    if game_over:
        screen.blit(end, (0, 0))
        pygame.display.flip()
        continue

    screen.fill("black")
    screen.blit(bg, (0, 0))

    score_text = font_small.render("得分：" + str(score), True, (255, 255, 255))
    time_text = font_small.render("时间：" + str(int(time_left)) + "秒", True, (255, 255, 255))
    latest_score_text = font_small.render("最高分：" + str(latest_score), True, (255, 255, 255))
    last_score_text = font_small.render("上次得分：" + str(last_score), True, (255, 255, 255))

    screen.blit(score_text, (10, 10))
    screen.blit(time_text, (445, 10))
    screen.blit(latest_score_text, (10, 760))
    screen.blit(last_score_text, (805, 760))

    if paused:
        pause_text = font_small.render("已暂停  按 P 继续", True, (255, 255, 255))
        screen.blit(pause_text, (400, 390))

    if mole_visible:
        screen.blit(mole, mole_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()