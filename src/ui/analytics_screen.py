from __future__ import annotations

from datetime import datetime

import pygame
import pygame_gui

from src.ui.theme import ACCENT, ANALYTICS_ACCENT, CARD_BORDER, CARD_MUTED, SUCCESS, TEXT_MUTED, TEXT_PRIMARY, UI_FONT_NAME, WARNING
from src.services.analytics_service import AnalyticsSummary
from src.ui.base_screen import BaseScreen


class AnalyticsScreen(BaseScreen):
    """Analytics page for quiz history."""

    def __init__(self, app) -> None:
        super().__init__(app, "analytics")
        self.back_button: pygame_gui.elements.UIButton | None = None
        self.summary: AnalyticsSummary | None = None

    def enter(self) -> None:
        if not self.require_login():
            self.summary = None
            return
        username = getattr(self.app.current_user, "username", "")
        self.summary = self.app.analytics_service.build_user_summary(username)
        super().enter()

    def on_logout(self) -> None:
        self.summary = None

    def rebuild_ui(self) -> None:
        self.clear_ui()
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(180, 116, 120, 44),
            text="Back Home",
            manager=self.app.ui_manager,
            object_id="#back_home_button",
        )
        self.ui_elements.append(self.back_button)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame_gui.UI_BUTTON_PRESSED and event.ui_element == self.back_button:
            self.app.router.navigate("home")

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        
        # Draw header panel
        header_rect = pygame.Rect(180, 110, 1000, 80)
        self._draw_panel(surface, header_rect, accent=ANALYTICS_ACCENT)
        title_font = pygame.font.SysFont(UI_FONT_NAME, 32)
        title_surface = title_font.render("Learning Analytics", True, pygame.Color(TEXT_PRIMARY))
        title_x = header_rect.centerx - title_surface.get_width() // 2
        title_y = header_rect.top + 18
        surface.blit(title_surface, (title_x, title_y))
        
        if self.summary is None or self.summary.total_quizzes == 0:
            self._draw_empty_state(
                surface,
                pygame.Rect(180, 230, 920, 470),
                "No Quiz History Yet",
                "Complete at least one quiz first. Then this page will display trends, category accuracy, and difficulty charts.",
            )
            return

        self._draw_summary_cards(surface)
        self._draw_trend_chart(surface)
        self._draw_category_chart(surface)
        self._draw_difficulty_chart(surface)
        self._draw_history_table(surface)

    def _draw_summary_cards(self, surface: pygame.Surface) -> None:
        assert self.summary is not None
        cards = [
            (pygame.Rect(180, 220, 215, 126), "Average Score", f"{self.summary.average_score:.1f}", "", ANALYTICS_ACCENT),
            (pygame.Rect(415, 220, 215, 126), "Best Score", f"{self.summary.best_score}", "", SUCCESS),
            (pygame.Rect(650, 220, 215, 126), "Total Quizzes", f"{self.summary.total_quizzes}", "", ANALYTICS_ACCENT),
            (pygame.Rect(885, 220, 215, 126), "Latest Result", self._last_result_text(), "", WARNING),
        ]
        for rect, label, value, hint, accent in cards:
            self._draw_metric_card(surface, rect, label, value, hint, accent)

    def _draw_trend_chart(self, surface: pygame.Surface) -> None:
        assert self.summary is not None
        panel = pygame.Rect(180, 368, 440, 250)
        self._draw_panel(surface, panel, title="Score Trend", accent=ANALYTICS_ACCENT)

        chart_rect = pygame.Rect(panel.left + 34, panel.top + 78, panel.width - 68, panel.height - 116)
        pygame.draw.line(surface, pygame.Color(CARD_BORDER), (chart_rect.left, chart_rect.bottom), (chart_rect.right, chart_rect.bottom), 2)
        pygame.draw.line(surface, pygame.Color(CARD_BORDER), (chart_rect.left, chart_rect.top), (chart_rect.left, chart_rect.bottom), 2)

        points = self.summary.trend_points[-8:]
        if not points:
            return

        plotted_points: list[tuple[int, int]] = []
        label_font = pygame.font.SysFont(UI_FONT_NAME, 13)
        for index, point in enumerate(points):
            ratio_x = index / max(len(points) - 1, 1)
            x = chart_rect.left + int(chart_rect.width * ratio_x)
            y = chart_rect.bottom - int(chart_rect.height * (point.accuracy / 100.0))
            plotted_points.append((x, y))
            surface.blit(label_font.render(point.label, True, pygame.Color(TEXT_MUTED)), (x - 10, chart_rect.bottom + 10))

        if len(plotted_points) >= 2:
            pygame.draw.lines(surface, pygame.Color(ANALYTICS_ACCENT), False, plotted_points, 3)
        for point in plotted_points:
            pygame.draw.circle(surface, pygame.Color(ANALYTICS_ACCENT), point, 5)

    def _draw_category_chart(self, surface: pygame.Surface) -> None:
        assert self.summary is not None
        panel = pygame.Rect(640, 368, 460, 250)
        self._draw_panel(surface, panel, title="Category Accuracy", accent=ANALYTICS_ACCENT)

        categories = self.summary.category_accuracy[:5]
        if not categories:
            self._draw_status_banner(surface, pygame.Rect(panel.left + 18, panel.top + 84, panel.width - 36, 40), "Not enough data to draw the category chart yet.", "info")
            return

        label_font = pygame.font.SysFont(UI_FONT_NAME, 14, bold=True)
        for index, item in enumerate(categories):
            y = panel.top + 92 + index * 28
            surface.blit(label_font.render(item.category[:12], True, pygame.Color(TEXT_MUTED)), (panel.left + 20, y))
            bar_rect = pygame.Rect(panel.left + 126, y + 2, panel.width - 190, 16)
            self._draw_progress_bar(surface, bar_rect, item.accuracy / 100.0)
            value = label_font.render(f"{item.accuracy:.1f}%", True, pygame.Color(TEXT_PRIMARY))
            surface.blit(value, (bar_rect.right + 8, y - 1))

    def _draw_difficulty_chart(self, surface: pygame.Surface) -> None:
        assert self.summary is not None
        panel = pygame.Rect(180, 640, 440, 120)
        self._draw_panel(surface, panel, title="Difficulty Distribution", accent=WARNING)

        distribution = self.summary.difficulty_distribution
        total = sum(item.count for item in distribution)
        if total == 0:
            self._draw_status_banner(surface, pygame.Rect(panel.left + 18, panel.top + 54, panel.width - 36, 36), "No difficulty data is available yet.", "info")
            return

        colors = {"easy": SUCCESS, "medium": ANALYTICS_ACCENT, "hard": WARNING, "all": CARD_MUTED}
        bar_rect = pygame.Rect(panel.left + 18, panel.top + 58, panel.width - 36, 22)
        current_x = bar_rect.left
        for item in distribution:
            width = int(bar_rect.width * (item.count / total))
            if width <= 0:
                continue
            rect = pygame.Rect(current_x, bar_rect.top, width, bar_rect.height)
            pygame.draw.rect(surface, pygame.Color(colors.get(item.difficulty, ANALYTICS_ACCENT)), rect, border_radius=10)
            current_x += width

        legend_font = pygame.font.SysFont(UI_FONT_NAME, 14)
        legend_x = panel.left + 18
        for item in distribution:
            pygame.draw.circle(surface, pygame.Color(colors.get(item.difficulty, ANALYTICS_ACCENT)), (legend_x + 6, panel.top + 102), 6)
            surface.blit(legend_font.render(f"{item.difficulty}: {item.count}", True, pygame.Color(TEXT_MUTED)), (legend_x + 18, panel.top + 94))
            legend_x += 104

    def _draw_history_table(self, surface: pygame.Surface) -> None:
        assert self.summary is not None
        panel = pygame.Rect(640, 640, 460, 120)
        self._draw_panel(surface, panel, accent=CARD_MUTED)

        title_font = pygame.font.SysFont(UI_FONT_NAME, 24, bold=True)
        title_surface = title_font.render("Recent History", True, pygame.Color(TEXT_PRIMARY))
        surface.blit(title_surface, (panel.left + 18, panel.top + 18))

        font = pygame.font.SysFont("Consolas", 16)

        for index, record in enumerate(self.summary.records[:3]):
            date_text = self._format_date(record.quiz_date)
            row = f"{date_text}   {record.score}/{record.total_questions}   {record.accuracy:.1f}%"
            surface.blit(font.render(row, True, pygame.Color(TEXT_PRIMARY)), (panel.left + 18, panel.top + 60 + index * 22))

    def _last_result_text(self) -> str:
        assert self.summary is not None
        if self.summary.last_result is None:
            return "--"
        return f"{self.summary.last_result.score}/{self.summary.last_result.total_questions}"

    def _format_date(self, value: str) -> str:
        try:
            return datetime.fromisoformat(value).strftime("%m-%d %H:%M")
        except ValueError:
            return value[:10]
