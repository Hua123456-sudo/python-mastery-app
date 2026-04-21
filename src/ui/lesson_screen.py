from __future__ import annotations

import pygame
import pygame_gui

from src.ui.base_screen import BaseScreen


class LessonScreen(BaseScreen):
    """Placeholder lesson page for future course content."""

    def __init__(self, app) -> None:
        super().__init__(app, "lesson")
        self.back_button: pygame_gui.elements.UIButton | None = None

    def enter(self) -> None:
        if not self.require_login():
            return
        super().enter()

    def rebuild_ui(self) -> None:
        self.clear_ui()
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(180, 116, 128, 46),
            text="Back Home",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(250, 118, 320, 44),
            text="Lesson Hub",
            manager=self.app.ui_manager,
            object_id="#screen_title",
        )
        subtitle = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(250, 160, 640, 28),
            text="This page currently acts as a styled placeholder for future chapter navigation, examples, and lesson notes.",
            manager=self.app.ui_manager,
            object_id="#screen_subtitle",
        )
        self.ui_elements.extend([self.back_button, title, subtitle])

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.back_button:
            self.app.router.navigate("home")

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        hero = pygame.Rect(180, 220, 920, 180)
        grid = pygame.Rect(180, 430, 920, 300)
        self._draw_panel(
            surface,
            hero,
            title="Lesson Content Can Be Added Here",
            subtitle="The page is already integrated into the overall product design so future course material can fit in naturally.",
            accent="#38BDF8",
        )
        self._draw_empty_state(
            surface,
            grid,
            "Waiting for Lesson Content",
            "You can later place chapter outlines, code examples, concept summaries, and guided practice prompts here.",
        )
