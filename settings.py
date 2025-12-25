# settings.py
import pygame
from enum import Enum
from collections import namedtuple

pygame.init()
pygame.font.init()

# --- CONFIGS ---
BLOCK_SIZE = 10
SPEED_TRAIN = 10000
SPEED_DEMO = 30
GRID_W = 20
GRID_H = 20
NUM_ENVS = 16
COLS = 4
ROWS = 4

# Base resolution
BASE_GAME_W = GRID_W * BLOCK_SIZE
BASE_GAME_H = GRID_H * BLOCK_SIZE
BASE_WIDTH = BASE_GAME_W * COLS
BASE_HEIGHT = BASE_GAME_H * ROWS + 50 

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# --- THEME & COLORS ---
class Theme:
    BG_DARK     = (18, 18, 24)
    GRID_LINE   = (40, 40, 50)
    SNAKE_HEAD  = (0, 255, 150)
    SNAKE_BODY  = (0, 180, 100)
    FOOD_OUTER  = (255, 80, 80)
    FOOD_INNER  = (255, 200, 200)
    TEXT_MAIN   = (240, 240, 240)
    TEXT_SUB    = (150, 150, 160)
    ACCENT      = (255, 215, 0)
    
    # Button Colors
    BTN_DEFAULT = (50, 50, 65)
    BTN_HOVER   = (70, 70, 90)
    BTN_TEXT    = (255, 255, 255)
    BTN_RESET   = (180, 60, 60)
    BTN_RESET_H = (200, 80, 80)

# --- FONTS ---
try:
    font_main = pygame.font.SysFont('consolas', 14, bold=True)
    font_title = pygame.font.SysFont('consolas', 28, bold=True)
    font_btn = pygame.font.SysFont('arial', 18, bold=True)
except:
    font_main = pygame.font.SysFont('arial', 14)
    font_title = pygame.font.SysFont('arial', 28)
    font_btn = pygame.font.SysFont('arial', 18)