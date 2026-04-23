from __future__ import annotations

import pygame
import pygame_gui

from src.ui.base_screen import BaseScreen
from src.ui.theme import (
    ACCENT,
    ALGORITHM_ACCENT,
    ANALYTICS_ACCENT,
    BUTTON_GHOST_BG,
    BUTTON_SECONDARY_BG,
    CARD_BG,
    CARD_BG_HOVER,
    CARD_BORDER,
    QUIZ_ACCENT,
    TEXT_MUTED,
    TEXT_PRIMARY,
    UI_FONT_NAME,
)


class HomeScreen(BaseScreen):
    """Main home screen after login."""

    def __init__(self, app) -> None:
        super().__init__(app, "home")
        self.lesson_button: pygame_gui.elements.UIButton | None = None
        self.admin_button: pygame_gui.elements.UIButton | None = None
        self.logout_button: pygame_gui.elements.UIButton | None = None
        self.quiz_card_rect = pygame.Rect(0, 0, 0, 0)
        self.analytics_card_rect = pygame.Rect(0, 0, 0, 0)
        self.algorithm_card_rect = pygame.Rect(0, 0, 0, 0)

    def enter(self) -> None:
        if not self.require_login():
            return
        super().enter()

    def rebuild_ui(self) -> None:
        self.clear_ui()
        layout = self._get_layout()
        current_user = self.app.current_user
        role = current_user.role if current_user is not None else "unknown"
        is_admin = role == "admin"
        self.quiz_card_rect = layout["quiz_card"]
        self.analytics_card_rect = layout["analytics_card"]
        self.algorithm_card_rect = layout["algorithm_card"]

        self.lesson_button = pygame_gui.elements.UIButton(
            relative_rect=layout["lesson_button"],
            text="Lessons",
            manager=self.app.ui_manager,
            object_id="#ghost_button",
        )

        if is_admin:
            self.admin_button = pygame_gui.elements.UIButton(
                relative_rect=layout["admin_button"],
                text="Admin Panel",
                manager=self.app.ui_manager,
                object_id="#secondary_button",
            )
        else:
            self.admin_button = None

        self.logout_button = pygame_gui.elements.UIButton(
            relative_rect=layout["logout_button"],
            text="Log Out",
            manager=self.app.ui_manager,
            object_id="#ghost_button",
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
        layout = self._get_layout()
        self.quiz_card_rect = layout["quiz_card"]
        self.analytics_card_rect = layout["analytics_card"]
        self.algorithm_card_rect = layout["algorithm_card"]

        current_user = self.app.current_user
        username = current_user.username if current_user is not None else "Guest"
        mouse_pos = pygame.mouse.get_pos()

        title_font = pygame.font.SysFont(UI_FONT_NAME, 40, bold=True)
        subtitle_font = pygame.font.SysFont(UI_FONT_NAME, 19)
        card_title_font = pygame.font.SysFont(UI_FONT_NAME, 28, bold=True)
        card_body_font = pygame.font.SysFont(UI_FONT_NAME, 17)
        hint_font = pygame.font.SysFont(UI_FONT_NAME, 15)

        # Draw header panel
        header_rect = layout["header_rect"]
        self._draw_panel(surface, header_rect, accent=ACCENT)
        title_surface = title_font.render(f"Welcome back, {username}", True, pygame.Color(TEXT_PRIMARY))
        surface.blit(title_surface, title_surface.get_rect(center=layout["title_center"]))
        subtitle_surface = subtitle_font.render("Choose one core module to continue.", True, pygame.Color(TEXT_MUTED))
        surface.blit(subtitle_surface, subtitle_surface.get_rect(center=layout["subtitle_center"]))

        cards = [
            (
                self.quiz_card_rect,
                "Start Quiz",
                "Answer a focused quiz with custom filters.",
                QUIZ_ACCENT,
            ),
            (
                self.analytics_card_rect,
                "Analytics",
                "Review score trends and accuracy clearly.",
                ANALYTICS_ACCENT,
            ),
            (
                self.algorithm_card_rect,
                "Algorithms",
                "Present arrays, lists, and trees visually.",
                ALGORITHM_ACCENT,
            ),
        ]

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
                hint_font=hint_font,
            )

        button_strip = layout["button_strip"]
        pygame.draw.rect(surface, (236, 244, 255, 8), button_strip, border_radius=24)
        pygame.draw.rect(surface, pygame.Color(CARD_BORDER), button_strip, width=1, border_radius=24)

        if getattr(self.app, "home_notice_message", ""):
            kind = self.app.home_notice_kind if self.app.home_notice_kind in {"info", "success", "error", "warning"} else "info"
            self._draw_status_banner(surface, layout["notice_rect"], self.app.home_notice_message, kind)



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
        hint_font: pygame.font.Font,
    ) -> None:
        shadow_alpha = 18 if hovered else 10
        shadow = pygame.Surface((rect.width + 12, rect.height + 16), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (10, 18, 30, shadow_alpha), shadow.get_rect(), border_radius=28)
        surface.blit(shadow, (rect.left - 6, rect.top + 8))

        card_color = pygame.Color(CARD_BG_HOVER if hovered else CARD_BG)
        border_color = pygame.Color(accent if hovered else CARD_BORDER)
        pygame.draw.rect(surface, card_color, rect, border_radius=24)
        pygame.draw.rect(surface, border_color, rect, width=1, border_radius=24)

        accent_rect = pygame.Rect(rect.left + 22, rect.top + 20, 74, 6)
        pygame.draw.rect(surface, pygame.Color(accent), accent_rect, border_radius=8)

        title_surface = title_font.render(title, True, pygame.Color(TEXT_PRIMARY))
        surface.blit(title_surface, (rect.left + 22, rect.top + 56))

        # Wrap body text to fit within card
        max_width = rect.width - 44  # 22px left and right margins
        lines = []
        current_line = ""
        words = body.split()
        
        for word in words:
            if not current_line:
                current_line = word
            else:
                test_line = f"{current_line} {word}"
                if body_font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
        if current_line:
            lines.append(current_line)
        
        # Draw wrapped body text
        for i, line in enumerate(lines[:2]):  # Limit to 2 lines
            body_surface = body_font.render(line, True, pygame.Color(TEXT_MUTED))
            surface.blit(body_surface, (rect.left + 22, rect.top + 114 + i * 22))

        hint_surface = hint_font.render("Open module", True, pygame.Color(TEXT_MUTED))
        surface.blit(hint_surface, (rect.left + 22, rect.bottom - 40))

    def _get_layout(self) -> dict[str, pygame.Rect | tuple[int, int]]:
        content = self.get_content_rect(44, 34)
        header_height = 140
        header_rect = pygame.Rect(content.left, content.top, content.width, header_height)
        cards_top = header_rect.bottom + 30
        card_height = min(230, max(196, int(content.height * 0.42)))
        card_gap = max(20, min(34, content.width // 28))
        card_width = max(220, min(300, (content.width - card_gap * 2) // 3))
        total_cards_width = card_width * 3 + card_gap * 2
        cards_left = content.centerx - total_cards_width // 2

        quiz_card = pygame.Rect(cards_left, cards_top, card_width, card_height)
        analytics_card = pygame.Rect(quiz_card.right + card_gap, cards_top, card_width, card_height)
        algorithm_card = pygame.Rect(analytics_card.right + card_gap, cards_top, card_width, card_height)

        button_strip_width = min(720, max(500, content.width - 180))
        button_strip_height = 88
        button_strip = pygame.Rect(content.centerx - button_strip_width // 2, content.bottom - 110, button_strip_width, button_strip_height)
        button_gap = 16
        secondary_width = 170
        lesson_width = 150
        logout_width = 150
        has_admin = self.app.current_user is not None and self.app.current_user.role == "admin"
        total_button_width = lesson_width + logout_width + button_gap
        if has_admin:
            total_button_width += secondary_width + button_gap
        buttons_left = button_strip.centerx - total_button_width // 2
        lesson_button = pygame.Rect(buttons_left, button_strip.top + 22, lesson_width, 44)
        if has_admin:
            admin_button = pygame.Rect(lesson_button.right + button_gap, button_strip.top + 22, secondary_width, 44)
            logout_button = pygame.Rect(admin_button.right + button_gap, button_strip.top + 22, logout_width, 44)
        else:
            admin_button = pygame.Rect(0, 0, 0, 0)
            logout_button = pygame.Rect(lesson_button.right + button_gap, button_strip.top + 22, logout_width, 44)

        return {
            "header_rect": header_rect,
            "title_center": (content.centerx, header_rect.centery - 20),
            "subtitle_center": (content.centerx, header_rect.centery + 20),
            "quiz_card": quiz_card,
            "analytics_card": analytics_card,
            "algorithm_card": algorithm_card,
            "button_strip": button_strip,
            "lesson_button": lesson_button,
            "admin_button": admin_button,
            "logout_button": logout_button,
            "notice_rect": pygame.Rect(content.centerx - 380, button_strip.bottom + 10, 760, 38),
        }

    def on_logout(self) -> None:
        self.app.home_notice_message = ""
        self.app.home_notice_kind = "info"
