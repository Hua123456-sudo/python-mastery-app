from __future__ import annotations

import pygame
import pygame_gui

from src.config import ACCENT, CARD_BACKGROUND, CARD_BORDER, TEXT_FAINT, TEXT_MUTED, TEXT_PRIMARY, UI_FONT_NAME
from src.ui.base_screen import BaseScreen


class HomeScreen(BaseScreen):
    """Main home screen after login."""

    def __init__(self, app) -> None:
        super().__init__(app, "home")
        self.lesson_button: pygame_gui.elements.UIButton | None = None
        self.admin_button: pygame_gui.elements.UIButton | None = None
        self.logout_button: pygame_gui.elements.UIButton | None = None
        self.quiz_card_rect = pygame.Rect(190, 292, 270, 260)
        self.analytics_card_rect = pygame.Rect(505, 292, 270, 260)
        self.algorithm_card_rect = pygame.Rect(820, 292, 270, 260)

    def enter(self) -> None:
        if not self.require_login():
            return
        super().enter()

    def rebuild_ui(self) -> None:
        self.clear_ui()
        current_user = self.app.current_user
        role = current_user.role if current_user is not None else "unknown"
        is_admin = role == "admin"

        self.lesson_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(414, 652, 170, 50),
            text="Lessons",
            manager=self.app.ui_manager,
            object_id="#ghost_button",
        )

        if is_admin:
            self.admin_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(604, 652, 190, 50),
                text="Admin Panel",
                manager=self.app.ui_manager,
                object_id="#secondary_button",
            )
            logout_x = 814
        else:
            self.admin_button = None
            logout_x = 604

        self.logout_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(logout_x, 652, 170, 50),
            text="Log Out",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )

        self.ui_elements.extend([self.lesson_button, self.logout_button])
        if self.admin_button is not None:
            self.ui_elements.append(self.admin_button)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.quiz_card_rect.collidepoint(event.pos):
                self.app.router.navigate("quiz")
                return
            if self.analytics_card_rect.collidepoint(event.pos):
                self.app.router.navigate("analytics")
                return
            if self.algorithm_card_rect.collidepoint(event.pos):
                self.app.router.navigate("algorithm")
                return

        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return
        if event.ui_element == self.lesson_button:
            self.app.router.navigate("lesson")
            return
        if event.ui_element == self.admin_button:
            self.app.router.navigate("admin")
            return
        if event.ui_element == self.logout_button:
            self.app.logout()

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        current_user = self.app.current_user
        username = current_user.username if current_user is not None else "Guest"

        content_rect = pygame.Rect(166, 110, 948, 610)
        section_rect = pygame.Rect(190, 220, 900, 370)
        hero_center_x = content_rect.centerx

        title_font = pygame.font.SysFont(UI_FONT_NAME, 34, bold=True)
        subtitle_font = pygame.font.SysFont(UI_FONT_NAME, 18)
        caption_font = pygame.font.SysFont(UI_FONT_NAME, 15)
        card_title_font = pygame.font.SysFont(UI_FONT_NAME, 28, bold=True)
        card_body_font = pygame.font.SysFont(UI_FONT_NAME, 17)

        welcome_surface = title_font.render(f"Welcome back, {username}", True, pygame.Color(TEXT_PRIMARY))
        surface.blit(welcome_surface, welcome_surface.get_rect(center=(hero_center_x, 172)))

        subtitle = "Choose a main module below to continue your learning, analysis, or classroom demonstration."
        subtitle_surface = subtitle_font.render(subtitle, True, pygame.Color(TEXT_MUTED))
        surface.blit(subtitle_surface, subtitle_surface.get_rect(center=(hero_center_x, 215)))

        self._draw_panel(surface, section_rect, accent=ACCENT)

        cards = [
            (
                self.quiz_card_rect,
                "Start Quiz",
                "Begin a quiz with configurable question amount, category, and difficulty.",
                ACCENT,
            ),
            (
                self.analytics_card_rect,
                "Analytics",
                "Review score trends, category accuracy, and difficulty distribution.",
                "#A78BFA",
            ),
            (
                self.algorithm_card_rect,
                "Algorithms",
                "Demonstrate arrays, linked lists, and trees with step-by-step visuals.",
                "#F59E0B",
            ),
        ]

        mouse_pos = pygame.mouse.get_pos()
        for rect, title, body, accent in cards:
            self._draw_home_card(
                surface=surface,
                rect=rect,
                title=title,
                body=body,
                accent=accent,
                hovered=rect.collidepoint(mouse_pos),
                title_font=card_title_font,
                body_font=card_body_font,
                caption_font=caption_font,
            )

        footer_note = "Primary actions live in the cards above. Secondary tools stay below for a cleaner home screen."
        footer_surface = caption_font.render(footer_note, True, pygame.Color(TEXT_FAINT))
        surface.blit(footer_surface, footer_surface.get_rect(center=(hero_center_x, 620)))

        if getattr(self.app, "home_notice_message", ""):
            kind = self.app.home_notice_kind if self.app.home_notice_kind in {"info", "success", "error", "warning"} else "info"
            self._draw_status_banner(surface, pygame.Rect(220, 720, 840, 38), self.app.home_notice_message, kind)

    def _draw_home_card(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        title: str,
        body: str,
        accent: str,
        hovered: bool,
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        caption_font: pygame.font.Font,
    ) -> None:
        shadow_rect = rect.move(0, 10)
        pygame.draw.rect(surface, (7, 11, 23), shadow_rect, border_radius=26)

        card_color = pygame.Color("#1B2538" if hovered else CARD_BACKGROUND)
        border_color = pygame.Color(accent if hovered else CARD_BORDER)
        pygame.draw.rect(surface, card_color, rect, border_radius=26)
        pygame.draw.rect(surface, border_color, rect, width=1, border_radius=26)

        accent_rect = pygame.Rect(rect.centerx - 42, rect.top + 22, 84, 6)
        pygame.draw.rect(surface, pygame.Color(accent), accent_rect, border_radius=8)

        title_surface = title_font.render(title, True, pygame.Color(TEXT_PRIMARY))
        surface.blit(title_surface, title_surface.get_rect(center=(rect.centerx, rect.top + 92)))

        description_lines = self._wrap_text(body, 26)[:3]
        for index, line in enumerate(description_lines):
            line_surface = body_font.render(line, True, pygame.Color(TEXT_MUTED))
            surface.blit(line_surface, line_surface.get_rect(center=(rect.centerx, rect.top + 146 + index * 24)))

        hint_surface = caption_font.render("Click to open", True, pygame.Color(TEXT_FAINT))
        surface.blit(hint_surface, hint_surface.get_rect(center=(rect.centerx, rect.bottom - 34)))

    def on_logout(self) -> None:
        self.app.home_notice_message = ""
        self.app.home_notice_kind = "info"
