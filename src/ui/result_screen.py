from __future__ import annotations

import pygame
import pygame_gui

from src.ui.theme import ACCENT, ANALYTICS_ACCENT, CARD_MUTED, SUCCESS, TEXT_MUTED, TEXT_PRIMARY, UI_FONT_NAME, WARNING
from src.ui.base_screen import BaseScreen


class ResultScreen(BaseScreen):
    """Quiz result page."""

    def __init__(self, app) -> None:
        super().__init__(app, "result")
        self.home_button: pygame_gui.elements.UIButton | None = None
        self.retry_button: pygame_gui.elements.UIButton | None = None

    def enter(self) -> None:
        if self.app.current_user is None and self.app.latest_quiz_result is None:
            if not self.require_login():
                return
        super().enter()

    def rebuild_ui(self) -> None:
        self.clear_ui()
        layout = self._get_layout()
        self.home_button = pygame_gui.elements.UIButton(
            relative_rect=layout["home_button"],
            text="Back Home",
            manager=self.app.ui_manager,
            object_id="#back_home_button",
        )
        self.retry_button = pygame_gui.elements.UIButton(
            relative_rect=layout["retry_button"],
            text="Try Again",
            manager=self.app.ui_manager,
            object_id="#primary_button",
        )
        self.ui_elements.extend([self.home_button, self.retry_button])

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return
        if event.ui_element == self.home_button:
            self.app.router.navigate("home")
            return
        if event.ui_element == self.retry_button:
            self.app.router.navigate("quiz")

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        layout = self._get_layout()
        header_rect = layout["header_rect"]
        self._draw_panel(surface, header_rect, accent=ACCENT)
        self._draw_header_text(surface, layout)

        result = self.app.latest_quiz_result
        record = self.app.latest_quiz_record
        save_message = self.app.latest_quiz_save_message or "This quiz result has not been saved yet."

        if result is None:
            self._draw_empty_state(
                surface,
                layout["empty_rect"],
                "No Quiz Result Yet",
                "Please return to the home page and complete a quiz first. Your score summary will appear here afterward.",
            )
            return

        summary_rect = layout["summary_rect"]
        self._draw_panel(
            surface,
            summary_rect,
            title="Quiz Completed",
            accent=ACCENT,
        )

        metric_cards = [
            (layout["metric_cards"][0], "Score", f"{result.score}", "Points earned this round", ACCENT),
            (layout["metric_cards"][1], "Correct", f"{result.correct_count}", "Questions answered correctly", SUCCESS),
            (layout["metric_cards"][2], "Total", f"{result.total_questions}", "Questions in this quiz", ANALYTICS_ACCENT),
            (layout["metric_cards"][3], "Accuracy", f"{result.accuracy:.1f}%", "Useful for trend tracking", WARNING),
        ]
        for rect, label, value, hint, accent in metric_cards:
            self._draw_metric_card(surface, rect, label, value, hint, accent)

        time_text = self.app.quiz_service.format_duration(result.elapsed_seconds)
        wrong_count = len(record.wrong_questions) if record is not None else sum(1 for answer in result.answers if not answer.is_correct)

        left_info_rect = layout["left_info_rect"]
        right_info_rect = layout["right_info_rect"]
        self._draw_panel(surface, left_info_rect, title="Round Summary", accent=CARD_MUTED)
        self._draw_panel(surface, right_info_rect, title="Save Status", accent=CARD_MUTED)

        self._draw_key_value_lines(
            surface,
            left_info_rect.left + 20,
            left_info_rect.top + 64,
            [
                ("Time", time_text),
                ("Difficulty", result.config.difficulty),
                ("Category", result.config.category),
                ("Wrong", str(wrong_count)),
            ],
            line_gap=30,
        )

        save_kind = "success" if record is not None else "error"
        self._draw_status_banner(
            surface,
            layout["save_banner_rect"],
            save_message,
            save_kind,
        )
        if record is not None:
            info_font = pygame.font.SysFont(UI_FONT_NAME, 16)
            meta_lines = [
                self._fit_text(info_font, f"Record ID: {record.record_id}", right_info_rect.width - 36),
                self._fit_text(info_font, f"Saved at: {record.quiz_date}", right_info_rect.width - 36),
            ]
            for index, line in enumerate(meta_lines):
                surface.blit(
                    info_font.render(line, True, pygame.Color(TEXT_MUTED)),
                    (right_info_rect.left + 18, right_info_rect.top + 122 + index * 22),
                )
        else:
            info_font = pygame.font.SysFont(UI_FONT_NAME, 16)
            surface.blit(
                info_font.render("Complete another quiz to create a saved record.", True, pygame.Color(TEXT_MUTED)),
                (right_info_rect.left + 18, right_info_rect.top + 122),
            )

    def _build_encouragement(self, accuracy: float) -> str:
        if accuracy >= 90:
            return "Excellent performance. You handled this round with strong accuracy."
        if accuracy >= 75:
            return "A solid result. Review a few mistakes and aim even higher next time."
        if accuracy >= 60:
            return "You have built a good foundation. Focus on explanations to improve."
        return "Do not worry. Review the explanations and try another round step by step."

    def _get_layout(self) -> dict[str, pygame.Rect | list[pygame.Rect]]:
        content = self.get_content_rect(34, 26)
        header_rect = pygame.Rect(content.left, content.top + 6, content.width, 92)
        summary_rect = pygame.Rect(content.left, header_rect.bottom + 18, content.width, content.height - 174)

        metrics_top = summary_rect.top + 74
        metric_gap = 20
        metric_height = 146
        metric_width = (summary_rect.width - 60 - metric_gap * 3) // 4
        metrics_left = summary_rect.left + 30
        metric_cards = [
            pygame.Rect(metrics_left + index * (metric_width + metric_gap), metrics_top, metric_width, metric_height)
            for index in range(4)
        ]

        info_top = metrics_top + metric_height + 28
        info_height = 188
        left_width = (summary_rect.width - 72) // 2
        left_info_rect = pygame.Rect(summary_rect.left + 30, info_top, left_width, info_height)
        right_info_rect = pygame.Rect(left_info_rect.right + 24, info_top, summary_rect.width - left_width - 84, info_height)

        button_y = summary_rect.bottom + 20
        home_button = pygame.Rect(content.left + 30, button_y, 180, 52)
        retry_button = pygame.Rect(home_button.right + 24, button_y, 180, 52)

        return {
            "header_rect": header_rect,
            "summary_rect": summary_rect,
            "metric_cards": metric_cards,
            "left_info_rect": left_info_rect,
            "right_info_rect": right_info_rect,
            "save_banner_rect": pygame.Rect(right_info_rect.left + 18, right_info_rect.top + 68, right_info_rect.width - 36, 46),
            "home_button": home_button,
            "retry_button": retry_button,
            "empty_rect": pygame.Rect(content.left, header_rect.bottom + 20, content.width, content.height - 150),
        }

    def _draw_header_text(self, surface: pygame.Surface, layout: dict[str, pygame.Rect | list[pygame.Rect]]) -> None:
        header_rect: pygame.Rect = layout["header_rect"]  # type: ignore[assignment]
        title_font = pygame.font.SysFont(UI_FONT_NAME, 38, bold=False)
        subtitle_font = pygame.font.SysFont(UI_FONT_NAME, 17)
        title_surface = title_font.render("Quiz Result", True, pygame.Color(TEXT_PRIMARY))
        subtitle = "Review your score, accuracy, time spent, and save status."
        subtitle_surface = subtitle_font.render(subtitle, True, pygame.Color(TEXT_MUTED))
        surface.blit(title_surface, title_surface.get_rect(center=(header_rect.centerx, header_rect.top + 38)))
        surface.blit(subtitle_surface, subtitle_surface.get_rect(center=(header_rect.centerx, header_rect.top + 72)))

    def _fit_text(self, font: pygame.font.Font, text: str, max_width: int) -> str:
        plain = (text or "").replace("\n", " ")
        if font.size(plain)[0] <= max_width:
            return plain
        trimmed = plain
        while trimmed and font.size(trimmed + "...")[0] > max_width:
            trimmed = trimmed[:-1]
        return (trimmed.rstrip() + "...") if trimmed else "..."
