from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src import config
from src.ui import ui_text

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

    def draw_background(self, surface: pygame.Surface) -> None:
        top_color = pygame.Color(config.BACKGROUND_TOP)
        bottom_color = pygame.Color(config.BACKGROUND_BOTTOM)
        width, height = surface.get_size()

        for y in range(height):
            blend = y / max(height - 1, 1)
            color = (
                int(top_color.r + (bottom_color.r - top_color.r) * blend),
                int(top_color.g + (bottom_color.g - top_color.g) * blend),
                int(top_color.b + (bottom_color.b - top_color.b) * blend),
            )
            pygame.draw.line(surface, color, (0, y), (width, y))

        glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (56, 189, 248, 26), (width - 180, 110), 180)
        pygame.draw.circle(glow_surface, (14, 165, 233, 20), (140, height - 120), 140)
        surface.blit(glow_surface, (0, 0))

        panel_rect = pygame.Rect(132, 82, width - 264, height - 164)
        shadow_rect = panel_rect.move(0, 10)
        pygame.draw.rect(surface, (7, 11, 23), shadow_rect, border_radius=32)
        pygame.draw.rect(surface, pygame.Color(config.PANEL_SOFT), panel_rect, border_radius=32)
        pygame.draw.rect(surface, pygame.Color(config.CARD_BORDER), panel_rect, width=1, border_radius=32)
        header_line = pygame.Rect(panel_rect.left + 24, panel_rect.top + 24, 140, 6)
        pygame.draw.rect(surface, pygame.Color(config.ACCENT), header_line, border_radius=8)

    def _draw_panel(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        title: str | None = None,
        subtitle: str | None = None,
        accent: str | None = None,
    ) -> None:
        shadow_rect = rect.move(0, 8)
        pygame.draw.rect(surface, (6, 10, 20), shadow_rect, border_radius=24)
        pygame.draw.rect(surface, pygame.Color(config.CARD_BACKGROUND), rect, border_radius=24)
        pygame.draw.rect(surface, pygame.Color(config.CARD_BORDER), rect, width=1, border_radius=24)

        if accent is not None:
            accent_rect = pygame.Rect(rect.left + 18, rect.top + 18, max(72, rect.width // 5), 6)
            pygame.draw.rect(surface, pygame.Color(accent), accent_rect, border_radius=8)

        if title is not None:
            title_font = pygame.font.SysFont(config.UI_FONT_NAME, 22, bold=True)
            surface.blit(title_font.render(title, True, pygame.Color(config.TEXT_PRIMARY)), (rect.left + 20, rect.top + 22))

        if subtitle is not None:
            body_font = pygame.font.SysFont(config.UI_FONT_NAME, 15)
            for index, line in enumerate(self._wrap_text(subtitle, 34)):
                surface.blit(body_font.render(line, True, pygame.Color(config.TEXT_MUTED)), (rect.left + 20, rect.top + 54 + index * 18))

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
        dot_color = pygame.Color(accent_color or config.ACCENT)
        pygame.draw.circle(surface, dot_color, (rect.left + 24, rect.top + 28), 7)

        label_font = pygame.font.SysFont(config.UI_FONT_NAME, 16, bold=True)
        value_font = pygame.font.SysFont(config.UI_FONT_NAME, 31, bold=True)
        hint_font = pygame.font.SysFont(config.UI_FONT_NAME, 14)

        surface.blit(label_font.render(label, True, pygame.Color(config.TEXT_MUTED)), (rect.left + 40, rect.top + 18))
        surface.blit(value_font.render(value, True, pygame.Color(config.TEXT_PRIMARY)), (rect.left + 20, rect.top + 50))
        if hint:
            surface.blit(hint_font.render(hint, True, pygame.Color(config.TEXT_FAINT)), (rect.left + 20, rect.bottom - 28))

    def _draw_status_banner(self, surface: pygame.Surface, rect: pygame.Rect, message: str, kind: str = "info") -> None:
        colors = {
            "info": (config.PANEL_DEEP, config.CARD_BORDER, config.TEXT_MUTED),
            "success": ("#0E2230", "#14532D", config.SUCCESS),
            "error": ("#2A1319", "#7F1D1D", config.ERROR),
            "warning": ("#2B1D12", "#92400E", config.WARNING),
        }
        bg, border, text_color = colors.get(kind, colors["info"])
        pygame.draw.rect(surface, pygame.Color(bg), rect, border_radius=16)
        pygame.draw.rect(surface, pygame.Color(border), rect, width=1, border_radius=16)
        pygame.draw.circle(surface, pygame.Color(text_color), (rect.left + 18, rect.centery), 6)

        font = pygame.font.SysFont(config.UI_FONT_NAME, 15, bold=True)
        lines = self._wrap_text(message or "--", max(18, (rect.width - 42) // 10))
        for index, line in enumerate(lines[:2]):
            surface.blit(font.render(line, True, pygame.Color(text_color)), (rect.left + 32, rect.top + 10 + index * 16))

    def _draw_empty_state(self, surface: pygame.Surface, rect: pygame.Rect, title: str, body: str) -> None:
        self._draw_panel(surface, rect, accent=config.ACCENT)
        title_font = pygame.font.SysFont(config.UI_FONT_NAME, 30, bold=True)
        body_font = pygame.font.SysFont(config.UI_FONT_NAME, 18)
        title_surface = title_font.render(title, True, pygame.Color(config.TEXT_PRIMARY))
        surface.blit(title_surface, title_surface.get_rect(center=(rect.centerx, rect.centery - 24)))
        for index, line in enumerate(self._wrap_text(body, 42)):
            line_surface = body_font.render(line, True, pygame.Color(config.TEXT_MUTED))
            surface.blit(line_surface, line_surface.get_rect(center=(rect.centerx, rect.centery + 18 + index * 22)))

    def _draw_progress_bar(self, surface: pygame.Surface, rect: pygame.Rect, progress: float, label: str | None = None) -> None:
        progress = max(0.0, min(1.0, progress))
        pygame.draw.rect(surface, pygame.Color(config.PANEL_DEEP), rect, border_radius=12)
        pygame.draw.rect(surface, pygame.Color(config.CARD_BORDER), rect, width=1, border_radius=12)
        fill_width = max(0, int((rect.width - 4) * progress))
        if fill_width > 0:
            fill_rect = pygame.Rect(rect.left + 2, rect.top + 2, fill_width, rect.height - 4)
            pygame.draw.rect(surface, pygame.Color(config.ACCENT), fill_rect, border_radius=10)
        if label:
            font = pygame.font.SysFont(config.UI_FONT_NAME, 14, bold=True)
            surface.blit(font.render(label, True, pygame.Color(config.TEXT_MUTED)), (rect.left, rect.bottom + 8))

    def _draw_chip(self, surface: pygame.Surface, rect: pygame.Rect, text: str, kind: str = "info") -> None:
        colors = {
            "easy": (config.SUCCESS, "#08111F"),
            "medium": (config.ACCENT, "#08111F"),
            "hard": (config.WARNING, "#08111F"),
            "info": (config.CARD_MUTED, config.TEXT_PRIMARY),
        }
        bg, fg = colors.get(kind, colors["info"])
        pygame.draw.rect(surface, pygame.Color(bg), rect, border_radius=14)
        font = pygame.font.SysFont(config.UI_FONT_NAME, 13, bold=True)
        text_surface = font.render(text, True, pygame.Color(fg))
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
        key_font = pygame.font.SysFont(config.UI_FONT_NAME, 16, bold=True)
        value_font = pygame.font.SysFont(config.UI_FONT_NAME, 16)
        for index, (key, value) in enumerate(items):
            y = start_y + index * line_gap
            surface.blit(key_font.render(key, True, pygame.Color(config.TEXT_FAINT)), (start_x, y))
            surface.blit(value_font.render(value, True, pygame.Color(value_color or config.TEXT_PRIMARY)), (start_x + 108, y))

    def _wrap_text(self, text: str, limit: int) -> list[str]:
        lines: list[str] = []
        for raw_line in (text or "").splitlines() or [""]:
            remaining = raw_line
            while len(remaining) > limit:
                lines.append(remaining[:limit])
                remaining = remaining[limit:]
            lines.append(remaining)
        return lines
