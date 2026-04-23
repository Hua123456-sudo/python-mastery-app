from __future__ import annotations

import json
from pathlib import Path

import pygame

from src.config import ROOT_DIR

FONT_NAME = "Microsoft YaHei"

PRIMARY = "#3B82F6"
PRIMARY_HOVER = "#2563EB"
PRIMARY_ACTIVE = "#1D4ED8"
BACK_BUTTON_BG = "#CFE3FF"
BACK_BUTTON_HOVER = "#BDD8FF"
BACK_BUTTON_ACTIVE = "#A9CCFF"
BACK_BUTTON_TEXT = "#23415F"
BACK_BUTTON_BORDER = "#A7C5EC"

BACKGROUND_TOP = "#0F172A"
BACKGROUND_BOTTOM = "#1E293B"
CARD_BG = "#1E2A3A"
CARD_BG_HOVER = "#253449"
CARD_BG_SELECTED = "#2A4568"
CARD_BG_HOME_HOVER = "#1B2538"
CARD_BORDER = "#2D3B52"
CARD_MUTED = "#223044"
PANEL_SOFT = "#162233"
PANEL_DEEP = "#111C2C"

TEXT_PRIMARY = "#EAF2FF"
TEXT_SECONDARY = "#C7D2E0"
TEXT_MUTED = "#8FA3BF"
TEXT_ON_ACCENT = "#F8FBFF"

QUIZ = "#3B82F6"
ANALYTICS = "#8B5CF6"
ALGORITHMS = "#F59E0B"
SUCCESS = "#34D399"
ERROR = "#FB7185"
WARNING = "#F59E0B"

BUTTON_SECONDARY_BG = "#223044"
BUTTON_SECONDARY_HOVER = "#30435E"
BUTTON_SECONDARY_ACTIVE = "#3A4D6A"
BUTTON_GHOST_BG = "#172233"
BUTTON_GHOST_HOVER = "#213149"
BUTTON_GHOST_ACTIVE = "#273855"

STATUS_SUCCESS_BG = "#0E2230"
STATUS_SUCCESS_BORDER = "#1C6A53"
STATUS_ERROR_BG = "#32161E"
STATUS_ERROR_BORDER = "#7F1D1D"
STATUS_WARNING_BG = "#332313"
STATUS_WARNING_BORDER = "#A16207"

SHADOW = "#080D18"
SHADOW_RGB = (8, 13, 24)
CHIP_TEXT_DARK = "#08111F"
GRAPH_LINK = "#93C5FD"
GRAPH_LINK_HOVER = "#BFDBFE"

THEME_PATH = ROOT_DIR / "assets" / "themes" / "theme.json"

# Backward-compatible aliases used across screen modules.
UI_FONT_NAME = FONT_NAME
ACCENT = PRIMARY
ACCENT_STRONG = PRIMARY_HOVER
QUIZ_ACCENT = QUIZ
ANALYTICS_ACCENT = ANALYTICS
ALGORITHM_ACCENT = ALGORITHMS
CARD_BACKGROUND = CARD_BG
TEXT_FAINT = TEXT_MUTED


def color(value: str | tuple[int, int, int] | tuple[int, int, int, int]) -> pygame.Color:
    return pygame.Color(value)


def build_theme_dict() -> dict:
    return {
        "defaults": {
            "colours": {
                "normal_bg": CARD_BG,
                "dark_bg": PANEL_DEEP,
                "normal_border": CARD_BORDER,
                "selected_bg": PRIMARY,
                "active_bg": PRIMARY_ACTIVE,
                "hovered_bg": PRIMARY_HOVER,
                "disabled_bg": CARD_MUTED,
                "normal_text": TEXT_PRIMARY,
                "selected_text": TEXT_ON_ACCENT,
                "disabled_text": TEXT_MUTED,
                "link_text": GRAPH_LINK,
                "link_hover": GRAPH_LINK_HOVER,
                "text_shadow": "#000000",
            },
            "font": {
                "name": FONT_NAME,
                "size": "20",
            },
            "misc": {
                "shape": "rounded_rectangle",
                "shape_corner_radius": "12",
                "border_width": "1",
                "shadow_width": "0",
            },
        },
        "#screen_title": {
            "font": {"name": FONT_NAME, "size": "36", "bold": "1"},
            "colours": {"normal_text": TEXT_PRIMARY},
        },
        "#screen_subtitle": {
            "font": {"name": FONT_NAME, "size": "19"},
            "colours": {"normal_text": TEXT_SECONDARY},
        },
        "#screen_caption": {
            "font": {"name": FONT_NAME, "size": "17", "bold": "1"},
            "colours": {"normal_text": TEXT_PRIMARY},
        },
        "#status_info": {
            "font": {"name": FONT_NAME, "size": "18"},
            "colours": {"normal_text": TEXT_SECONDARY},
        },
        "#status_success": {
            "font": {"name": FONT_NAME, "size": "18"},
            "colours": {"normal_text": SUCCESS},
        },
        "#status_error": {
            "font": {"name": FONT_NAME, "size": "18"},
            "colours": {"normal_text": ERROR},
        },
        "#primary_button": {
            "misc": {"shape_corner_radius": "12", "border_width": "0"},
            "colours": {
                "normal_bg": PRIMARY,
                "hovered_bg": PRIMARY_HOVER,
                "active_bg": PRIMARY_ACTIVE,
                "normal_text": TEXT_ON_ACCENT,
            },
        },
        "#secondary_button": {
            "misc": {"shape_corner_radius": "12", "border_width": "1"},
            "colours": {
                "normal_bg": BUTTON_SECONDARY_BG,
                "hovered_bg": BUTTON_SECONDARY_HOVER,
                "active_bg": BUTTON_SECONDARY_ACTIVE,
                "normal_text": TEXT_PRIMARY,
                "normal_border": CARD_BORDER,
            },
        },
        "#back_home_button": {
            "misc": {"shape_corner_radius": "12", "border_width": "1"},
            "colours": {
                "normal_bg": BACK_BUTTON_BG,
                "hovered_bg": BACK_BUTTON_HOVER,
                "active_bg": BACK_BUTTON_ACTIVE,
                "normal_text": BACK_BUTTON_TEXT,
                "normal_border": BACK_BUTTON_BORDER,
            },
        },
        "#ghost_button": {
            "misc": {"shape_corner_radius": "12", "border_width": "1"},
            "colours": {
                "normal_bg": BUTTON_GHOST_BG,
                "hovered_bg": BUTTON_GHOST_HOVER,
                "active_bg": BUTTON_GHOST_ACTIVE,
                "normal_text": TEXT_SECONDARY,
                "normal_border": CARD_BORDER,
            },
        },
        "#text_entry": {
            "misc": {"shape_corner_radius": "12", "border_width": "2"},
            "colours": {
                "dark_bg": PANEL_DEEP,
                "normal_border": CARD_BORDER,
                "selected_bg": PRIMARY,
                "normal_text": TEXT_PRIMARY,
            },
        },
        "#dropdown": {
            "misc": {"shape_corner_radius": "12", "border_width": "2"},
            "colours": {
                "dark_bg": PANEL_DEEP,
                "normal_border": CARD_BORDER,
                "normal_text": TEXT_PRIMARY,
            },
        },
    }


def ensure_theme_file() -> str:
    THEME_PATH.parent.mkdir(parents=True, exist_ok=True)
    THEME_PATH.write_text(json.dumps(build_theme_dict(), indent=2), encoding="utf-8")
    return str(THEME_PATH)
