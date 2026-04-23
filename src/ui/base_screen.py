from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.ui import ui_text
from src.ui import theme

if TYPE_CHECKING:
    from src.app import App


class BaseScreen:
    """Base contract for all application screens."""

    def __init__(self, app: "App", screen_id: str) -> None:
        self.app = app
        self.screen_id = screen_id
        self.ui_elements: list[object] = []

    def enter(self) -> None:
        self.rebuild_ui()

    def exit(self) -> None:
        self.clear_ui()

    def rebuild_ui(self) -> None:
        """Create the pygame_gui elements for this screen."""

    def clear_ui(self) -> None:
        for element in self.ui_elements:
            if hasattr(element, "kill"):
                element.kill()
        self.ui_elements.clear()

    def process_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events after UIManager processing."""

    def update(self, time_delta: float) -> None:
        """Update screen state."""

    def draw(self, surface: pygame.Surface) -> None:
        self.draw_background(surface)

    def on_logout(self) -> None:
        """Reset persistent state when the current user logs out."""

    def on_resize(self) -> None:
        self.rebuild_ui()

    def require_login(self, message: str = ui_text.REQUIRE_LOGIN) -> bool:
        if self.app.current_user is not None:
            return True
        self.app.pending_notice_message = message
        self.app.pending_notice_kind = "error"
        self.app.router.navigate("login")
        return False

    def redirect_home_notice(self, message: str, kind: str = "error") -> None:
        self.app.home_notice_message = message
        self.app.home_notice_kind = kind
        self.app.router.navigate("home")

    def get_panel_rect(self) -> pygame.Rect:
        width, height = self.app.window_size
        margin_x = max(56, min(132, width // 10))
        top_margin = max(10, min(24, height // 28))
        bottom_margin = max(16, min(34, height // 20))
        return pygame.Rect(
            margin_x,
            top_margin,
            width - margin_x * 2,
            height - top_margin - bottom_margin,
        )

    def get_content_rect(self, padding_x: int = 36, padding_y: int = 22) -> pygame.Rect:
        panel_rect = self.get_panel_rect()
        return pygame.Rect(
            panel_rect.left + padding_x,
            panel_rect.top + padding_y,
            panel_rect.width - padding_x * 2,
            panel_rect.height - padding_y * 2,
        )

    def draw_background(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        top_color = pygame.Color("#DCEBFA")
        bottom_color = pygame.Color("#EEF4FB")

        for y in range(height):
            blend = y / max(height - 1, 1)
            color = (
                int(top_color.r + (bottom_color.r - top_color.r) * blend),
                int(top_color.g + (bottom_color.g - top_color.g) * blend),
                int(top_color.b + (bottom_color.b - top_color.b) * blend),
            )
            pygame.draw.line(surface, color, (0, y), (width, y))

        glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (120, 170, 230, 42), (190, 150), 170)
        pygame.draw.circle(glow_surface, (150, 190, 240, 34), (width - 150, 130), 210)
        pygame.draw.circle(glow_surface, (200, 220, 246, 38), (width // 2, height - 60), 220)
        surface.blit(glow_surface, (0, 0))

        panel_rect = self.get_panel_rect()
        shadow_rect = panel_rect.move(0, 14)
        pygame.draw.rect(surface, (79, 105, 138, 18), shadow_rect, border_radius=28)
        pygame.draw.rect(surface, pygame.Color("#F4F8FD"), panel_rect, border_radius=32)
        pygame.draw.rect(surface, pygame.Color("#C7D9EB"), panel_rect, width=1, border_radius=32)
        glow_rect = panel_rect.inflate(2, 2)
        pygame.draw.rect(surface, (255, 255, 255, 120), glow_rect, width=1, border_radius=32)
        header_line = pygame.Rect(panel_rect.left + 24, panel_rect.top + 24, 140, 6)
        pygame.draw.rect(surface, theme.color(theme.PRIMARY), header_line, border_radius=8)

    def _draw_panel(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        title: str | None = None,
        subtitle: str | None = None,
        accent: str | None = None,
    ) -> None:
        shadow_rect = rect.move(0, 10)
        pygame.draw.rect(surface, (8, 13, 24), shadow_rect, border_radius=18)
        pygame.draw.rect(surface, theme.color(theme.CARD_BG), rect, border_radius=18)
        pygame.draw.rect(surface, theme.color(theme.CARD_BORDER), rect, width=1, border_radius=18)
        inner_line = pygame.Rect(rect.left + 1, rect.top + 1, rect.width - 2, rect.height - 2)
        pygame.draw.rect(surface, (*theme.color(theme.CARD_BORDER)[:3], 28), inner_line, width=1, border_radius=18)

        if accent is not None:
            accent_rect = pygame.Rect(rect.left + 18, rect.top + 18, max(72, rect.width // 5), 7)
            pygame.draw.rect(surface, theme.color(accent), accent_rect, border_radius=8)

        if title is not None:
            title_font = pygame.font.SysFont(theme.FONT_NAME, 26, bold=True)
            surface.blit(title_font.render(title, True, theme.color(theme.TEXT_PRIMARY)), (rect.left + 20, rect.top + 24))

        if subtitle is not None:
            body_font = pygame.font.SysFont(theme.FONT_NAME, 16)
            for index, line in enumerate(self._wrap_text(subtitle, 34)):
                surface.blit(body_font.render(line, True, theme.color(theme.TEXT_SECONDARY)), (rect.left + 20, rect.top + 60 + index * 21))

    def _draw_metric_card(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        value: str,
        hint: str = "",
        accent_color: str | None = None,
    ) -> None:
        self._draw_panel(surface, rect)
        dot_color = theme.color(accent_color or theme.PRIMARY)
        pygame.draw.circle(surface, dot_color, (rect.left + 24, rect.top + 28), 7)

        label_font = pygame.font.SysFont(theme.FONT_NAME, 17, bold=True)
        value_font = pygame.font.SysFont(theme.FONT_NAME, 33, bold=True)
        hint_font = pygame.font.SysFont(theme.FONT_NAME, 15)

        surface.blit(label_font.render(label, True, theme.color(theme.TEXT_SECONDARY)), (rect.left + 40, rect.top + 18))
        surface.blit(value_font.render(value, True, theme.color(theme.TEXT_PRIMARY)), (rect.left + 20, rect.top + 52))
        if hint:
            for index, line in enumerate(self._wrap_text(hint, max(18, (rect.width - 40) // 10))[:2]):
                surface.blit(hint_font.render(line, True, theme.color(theme.TEXT_MUTED)), (rect.left + 20, rect.bottom - 44 + index * 18))

    def _draw_status_banner(self, surface: pygame.Surface, rect: pygame.Rect, message: str, kind: str = "info") -> None:
        colors = {
            "info": (theme.PANEL_DEEP, theme.CARD_BORDER, theme.TEXT_SECONDARY),
            "success": (theme.STATUS_SUCCESS_BG, theme.STATUS_SUCCESS_BORDER, theme.SUCCESS),
            "error": (theme.STATUS_ERROR_BG, theme.STATUS_ERROR_BORDER, theme.ERROR),
            "warning": (theme.STATUS_WARNING_BG, theme.STATUS_WARNING_BORDER, theme.WARNING),
        }
        bg, border, text_color = colors.get(kind, colors["info"])
        pygame.draw.rect(surface, theme.color(bg), rect, border_radius=16)
        pygame.draw.rect(surface, theme.color(border), rect, width=1, border_radius=16)
        pygame.draw.circle(surface, theme.color(text_color), (rect.left + 18, rect.centery), 6)

        font = pygame.font.SysFont(theme.FONT_NAME, 16, bold=True)
        max_width = rect.width - 42  # 32px left margin + some right margin
        lines = []
        current_line = ""
        words = (message or "--").split()
        
        for word in words:
            if not current_line:
                current_line = word
            else:
                test_line = f"{current_line} {word}"
                if font.size(test_line)[0] <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
        if current_line:
            lines.append(current_line)
        
        for index, line in enumerate(lines[:2]):
            surface.blit(font.render(line, True, theme.color(text_color)), (rect.left + 32, rect.top + 9 + index * 18))

    def _draw_empty_state(self, surface: pygame.Surface, rect: pygame.Rect, title: str, body: str) -> None:
        self._draw_panel(surface, rect, accent=theme.PRIMARY)
        title_font = pygame.font.SysFont(theme.FONT_NAME, 34, bold=True)
        body_font = pygame.font.SysFont(theme.FONT_NAME, 19)
        title_surface = title_font.render(title, True, theme.color(theme.TEXT_PRIMARY))
        surface.blit(title_surface, title_surface.get_rect(center=(rect.centerx, rect.centery - 24)))
        for index, line in enumerate(self._wrap_text(body, 42)):
            line_surface = body_font.render(line, True, theme.color(theme.TEXT_SECONDARY))
            surface.blit(line_surface, line_surface.get_rect(center=(rect.centerx, rect.centery + 22 + index * 24)))

    def _draw_progress_bar(self, surface: pygame.Surface, rect: pygame.Rect, progress: float, label: str | None = None) -> None:
        progress = max(0.0, min(1.0, progress))
        pygame.draw.rect(surface, theme.color(theme.PANEL_DEEP), rect, border_radius=12)
        pygame.draw.rect(surface, theme.color(theme.CARD_BORDER), rect, width=1, border_radius=12)
        fill_width = max(0, int((rect.width - 4) * progress))
        if fill_width > 0:
            fill_rect = pygame.Rect(rect.left + 2, rect.top + 2, fill_width, rect.height - 4)
            pygame.draw.rect(surface, theme.color(theme.PRIMARY), fill_rect, border_radius=10)
        if label:
            font = pygame.font.SysFont(theme.FONT_NAME, 15, bold=True)
            surface.blit(font.render(label, True, theme.color(theme.TEXT_SECONDARY)), (rect.left, rect.bottom + 10))

    def _draw_chip(self, surface: pygame.Surface, rect: pygame.Rect, text: str, kind: str = "info") -> None:
        colors = {
            "easy": (theme.SUCCESS, theme.CHIP_TEXT_DARK),
            "medium": (theme.QUIZ, theme.CHIP_TEXT_DARK),
            "hard": (theme.WARNING, theme.CHIP_TEXT_DARK),
            "info": (theme.CARD_MUTED, theme.TEXT_PRIMARY),
        }
        bg, fg = colors.get(kind, colors["info"])
        pygame.draw.rect(surface, theme.color(bg), rect, border_radius=14)
        font = pygame.font.SysFont(theme.FONT_NAME, 14, bold=True)
        text_surface = font.render(text, True, theme.color(fg))
        surface.blit(text_surface, text_surface.get_rect(center=rect.center))

    def _draw_key_value_lines(
        self,
        surface: pygame.Surface,
        start_x: int,
        start_y: int,
        items: list[tuple[str, str]],
        value_color: str | None = None,
        line_gap: int = 30,
    ) -> None:
        key_font = pygame.font.SysFont(theme.FONT_NAME, 17, bold=True)
        value_font = pygame.font.SysFont(theme.FONT_NAME, 17)
        for index, (key, value) in enumerate(items):
            y = start_y + index * line_gap
            surface.blit(key_font.render(key, True, theme.color(theme.TEXT_MUTED)), (start_x, y))
            surface.blit(value_font.render(value, True, theme.color(value_color or theme.TEXT_PRIMARY)), (start_x + 108, y))

    def _wrap_text(self, text: str, limit: int) -> list[str]:
        lines: list[str] = []
        for raw_line in (text or "").splitlines() or [""]:
            remaining = raw_line
            while len(remaining) > limit:
                lines.append(remaining[:limit])
                remaining = remaining[limit:]
            lines.append(remaining)
        return lines
