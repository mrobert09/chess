import os
import pygame as pg

# Folder setup
game_folder = os.path.dirname(__file__)
def path(src, dst):
    return './imgs/' + dst
img_folder = './imgs'

# game options/settings
TITLE = "Chess"
WIDTH = 800
HEIGHT = 700
FPS = 60
FONT_NAME = pg.font.match_font('arial')
FONT_SIZE = 20

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (133, 133, 133)
PINK = (239, 99, 210)

# tile data
TILESIZE = 64
TILEWIDTH = 8
TILEHEIGHT = 8
BOARDWIDTH = TILEWIDTH * TILESIZE
BOARDHEIGHT = TILEHEIGHT * TILESIZE

# offsets for grid placement in window
X_OFFSET = 50
Y_OFFSET = 50