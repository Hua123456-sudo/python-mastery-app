from __future__ import annotations

import pygame
import pygame_gui

from src.config import ACCENT, UI_FONT_NAME
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
        title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(220, 124, 360, 48),
            text="Quiz Result",
            manager=self.app.ui_manager,
            object_id="#screen_title",
        )
        subtitle = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(220, 172, 660, 28),
            text="Review your score, accuracy, time spent, and save status before moving into long-term analytics.",
            manager=self.app.ui_manager,
            object_id="#screen_subtitle",
        )
        self.home_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(220, 690, 180, 52),
            text="Back Home",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        self.retry_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(420, 690, 180, 52),
            text="Try Again",
            manager=self.app.ui_manager,
            object_id="#primary_button",
        )
        self.ui_elements.extend([title, subtitle, self.home_button, self.retry_button])

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

        result = self.app.latest_quiz_result
        record = self.app.latest_quiz_record
        save_message = self.app.latest_quiz_save_message or "This quiz result has not been saved yet."

        if result is None:
            self._draw_empty_state(
                surface,
                pygame.Rect(180, 240, 920, 380),
                "No Quiz Result Yet",
                "Please return to the home page and complete a quiz first. Your score summary will appear here afterward.",
            )
            return

        summary_rect = pygame.Rect(180, 230, 920, 440)
        self._draw_panel(
            surface,
            summary_rect,
            title="Quiz Completed",
            subtitle=self._build_encouragement(result.accuracy),
            accent=ACCENT,
        )

        metric_cards = [
            (pygame.Rect(210, 320, 180, 140), "Score", f"{result.score}", "Points earned in this round", ACCENT),
            (pygame.Rect(410, 320, 180, 140), "Correct", f"{result.correct_count}", "Questions answered correctly", "#34D399"),
            (pygame.Rect(610, 320, 180, 140), "Total", f"{result.total_questions}", "Randomly selected from the bank", "#A78BFA"),
            (pygame.Rect(810, 320, 210, 140), "Accuracy", f"{result.accuracy:.1f}%", "Useful for trend analysis", "#F59E0B"),
        ]
        for rect, label, value, hint, accent in metric_cards:
            self._draw_metric_card(surface, rect, label, value, hint, accent)

        time_text = self.app.quiz_service.format_duration(result.elapsed_seconds)
        wrong_count = len(record.wrong_questions) if record is not None else sum(1 for answer in result.answers if not answer.is_correct)

        left_info_rect = pygame.Rect(210, 492, 380, 140)
        right_info_rect = pygame.Rect(610, 492, 410, 140)
        self._draw_panel(surface, left_info_rect, title="Round Summary", accent="#1E293B")
        self._draw_panel(surface, right_info_rect, title="Save Status", accent="#1E293B")

        self._draw_key_value_lines(
            surface,
            left_info_rect.left + 20,
            left_info_rect.top + 54,
            [
                ("Time", time_text),
                ("Difficulty", result.config.difficulty),
                ("Category", result.config.category),
                ("Wrong", str(wrong_count)),
            ],
        )

        save_kind = "success" if record is not None else "error"
        self._draw_status_banner(
            surface,
            pygame.Rect(right_info_rect.left + 18, right_info_rect.top + 54, right_info_rect.width - 36, 40),
            save_message,
            save_kind,
        )
        if record is not None:
            info_font = pygame.font.SysFont(UI_FONT_NAME, 15)
            meta = f"Record ID: {record.record_id}    Time: {record.quiz_date}"
            surface.blit(info_font.render(meta[:64], True, pygame.Color("#94A3B8")), (right_info_rect.left + 18, right_info_rect.top + 104))

    def _build_encouragement(self, accuracy: float) -> str:
        if accuracy >= 90:
            return "Excellent performance. You have a very strong grasp of the material covered in this round."
        if accuracy >= 75:
            return "A solid result. Reviewing a few mistakes should help you score even higher next time."
        if accuracy >= 60:
            return "You have built a good foundation. Focus on the explanations and incorrect answers for improvement."
        return "Do not worry. Review the explanations carefully and try another round to improve step by step."
