import os
import sys

import pygame


def _asset_path(relative_path):
    # PyInstaller extracts bundled data files to sys._MEIPASS at runtime,
    # which is not the process's working directory. Resolve every asset
    # relative to that (or this file's own directory when running from
    # source) instead of relying on cwd.
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60

# --- Fonts ---
# match_font() does a system font-directory scan, which doesn't exist in the
# browser/WASM sandbox (pygbag) and hangs there. Impact is rarely present on
# non-Mac systems anyway, so this was already falling back to the pygame
# default font (None) for most desktop players.
FONT_NAME = "impact"
FONT_PATH = None if sys.platform == "emscripten" else pygame.font.match_font(FONT_NAME)

# --- Modern UI palette ---
BG_DARK = (10, 13, 20)
PANEL_BG = (18, 22, 34, 218)
PANEL_BG_SOFT = (18, 22, 34, 150)
PANEL_BORDER = (58, 70, 96)
ACCENT = (72, 214, 255)
ACCENT_DIM = (34, 110, 140)
TEXT_PRIMARY = (240, 244, 250)
TEXT_MUTED = (150, 162, 185)
SUCCESS = (86, 224, 140)
DANGER = (240, 90, 96)
WARNING = (255, 200, 70)

PANEL_RADIUS = 18
BUTTON_RADIUS = 14
HUD_RADIUS = 16

# Legacy aliases used across draw code
WHITE = TEXT_PRIMARY
YELLOW = WARNING
NAVY = ACCENT
GREEN = SUCCESS
RED = DANGER

DEFAULT_MUSIC_VOLUME = 0.5

PLAYER_START_POS = (400, 300)
PLAYER_SPEED = 5

ENEMY_START_POS = (100, 100)
ENEMY_SPEED = 2

SPEED_BOOST_MULTIPLIER = 2
SPEED_BOOST_DURATION_MS = 15000
SPEEDUP_SPAWN_INTERVAL_MS = 8000
SPEEDUP_ICON_SIZE = (40, 40)

PLAYER_MAX_HP = 3
PLAYER_INVULNERABILITY_MS = 1000

ENEMY_MAX_HEALTH = 3
ENEMY_RESPAWN_DELAY_MS = 1500

WAVE_INTERVAL_SECONDS = 60
WAVE_SPEED_INCREMENT = 0.3
WAVE_HEALTH_INCREMENT = 1

QUIZ_CORRECT_INVULNERABILITY_MS = 2000
QUIZ_WRONG_ENEMY_ADVANCE = 0.4
QUIZ_FEEDBACK_DURATION_MS = 1500

BULLET_SPEED = 12
BULLET_RADIUS = 5
BULLET_COLOR = (255, 240, 60)

PLAYER_STARTING_AMMO = 10
PLAYER_MAX_AMMO = 20

AMMO_PICKUP_AMOUNT = 5
AMMO_PICKUP_COUNT = 4
AMMO_SPAWN_INTERVAL_MS = 6000
AMMO_ICON_SIZE = (24, 24)
AMMO_ICON_COLOR = (255, 215, 0)
AMMO_ICON_BORDER_COLOR = (120, 90, 10)

BACKGROUND_IMG_PATH = _asset_path("images/Background.jpg")
MENU_IMG_PATH = _asset_path("images/Title_Screen.jpg")
PLAYER_IMG_PATH = _asset_path("images/Running_Placeholder.png")
ENEMY_IMG_PATH = _asset_path("images/Ghost_Enemy.png")
SPEEDUP_IMG_PATH = _asset_path("images/Speed_Up.jpg")
MUSIC_PATH = _asset_path("audios/Backgroundmusic.ogg")
