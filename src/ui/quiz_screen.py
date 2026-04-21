from __future__ import annotations

from html import escape

import pygame
import pygame_gui

from src.config import ACCENT, SUCCESS, UI_FONT_NAME, WARNING
from src.services.quiz_service import QuizSession, QuizSubmissionResult
from src.ui import ui_text
from src.ui.base_screen import BaseScreen


class QuizScreen(BaseScreen):
    """Quiz workflow screen."""

    def __init__(self, app) -> None:
        super().__init__(app, "quiz")
        self.session: QuizSession | None = None
        self.status_message = ui_text.QUIZ_SETUP_HINT
        self.status_kind = "info"
        self.selected_option = ""
        self.current_text_answer = ""

        self.back_button: pygame_gui.elements.UIButton | None = None
        self.start_button: pygame_gui.elements.UIButton | None = None
        self.submit_button: pygame_gui.elements.UIButton | None = None
        self.next_button: pygame_gui.elements.UIButton | None = None

        self.count_dropdown: pygame_gui.elements.UIDropDownMenu | None = None
        self.difficulty_dropdown: pygame_gui.elements.UIDropDownMenu | None = None
        self.category_dropdown: pygame_gui.elements.UIDropDownMenu | None = None

        self.answer_entry_line: pygame_gui.elements.UITextEntryLine | None = None
        self.answer_entry_box: pygame_gui.elements.UITextEntryBox | None = None
        self.status_label: pygame_gui.elements.UILabel | None = None
        self.question_box: pygame_gui.elements.UITextBox | None = None
        self.feedback_box: pygame_gui.elements.UITextBox | None = None
        self.option_buttons: list[tuple[str, pygame_gui.elements.UIButton]] = []

        self.pending_question_count = "10"
        self.pending_difficulty = "all"
        self.pending_category = "all"

    def enter(self) -> None:
        if not self.require_login():
            self.session = None
            return
        super().enter()

    def rebuild_ui(self) -> None:
        self.clear_ui()
        self.option_buttons.clear()
        self._build_header()
        if self.session is None:
            self._build_setup_ui()
        else:
            self._build_quiz_ui()

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return

        if event.ui_element == self.back_button:
            self._reset_quiz_state("Returned to Home.")
            self.app.router.navigate("home")
            return

        if self.session is None:
            if event.ui_element == self.start_button:
                self._start_quiz()
            return

        if event.ui_element == self.submit_button:
            self._submit_answer()
            return
        if event.ui_element == self.next_button:
            self._go_to_next_question()
            return

        if self.session.last_submission is None:
            for option, button in self.option_buttons:
                if event.ui_element == button:
                    self.selected_option = option
                    self.rebuild_ui()
                    break

    def update(self, time_delta: float) -> None:
        del time_delta

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)
        if self.session is None:
            self._draw_setup_panels(surface)
        else:
            self._draw_quiz_panels(surface)

    def _build_header(self) -> None:
        title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(250, 118, 380, 44),
            text="Python Mastery Quiz",
            manager=self.app.ui_manager,
            object_id="#screen_title",
        )
        subtitle = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(250, 160, 650, 28),
            text="Configure the quiz, answer one question at a time, and review instant feedback.",
            manager=self.app.ui_manager,
            object_id="#screen_subtitle",
        )
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(180, 116, 120, 44),
            text=ui_text.BACK_HOME,
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        self.ui_elements.extend([title, subtitle, self.back_button])

    def _build_setup_ui(self) -> None:
        category_options = self.app.quiz_service.get_category_options()
        if self.pending_category not in category_options:
            self.pending_category = "all"

        labels = [
            ("Question Count", pygame.Rect(256, 278, 160, 24)),
            ("Difficulty", pygame.Rect(256, 382, 140, 24)),
            ("Category", pygame.Rect(256, 486, 140, 24)),
        ]
        for text, rect in labels:
            label = pygame_gui.elements.UILabel(
                relative_rect=rect,
                text=text,
                manager=self.app.ui_manager,
                object_id="#screen_caption",
            )
            self.ui_elements.append(label)

        self.count_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["10", "20", "30"],
            starting_option=self.pending_question_count,
            relative_rect=pygame.Rect(256, 312, 300, 48),
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.difficulty_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["all", "easy", "medium", "hard"],
            starting_option=self.pending_difficulty,
            relative_rect=pygame.Rect(256, 416, 300, 48),
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.category_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=category_options,
            starting_option=self.pending_category,
            relative_rect=pygame.Rect(256, 520, 420, 48),
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(256, 610, 220, 54),
            text=ui_text.START_QUIZ,
            manager=self.app.ui_manager,
            object_id="#primary_button",
        )
        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(256, 676, 600, 28),
            text=self.status_message,
            manager=self.app.ui_manager,
            object_id=self._status_object_id(),
        )
        self.ui_elements.extend(
            [
                self.count_dropdown,
                self.difficulty_dropdown,
                self.category_dropdown,
                self.start_button,
                self.status_label,
            ]
        )

        if len(category_options) <= 1 and self.start_button is not None:
            self.status_message = "No question data is available yet. Please add questions to questions.json before starting a quiz."
            self.status_kind = "error"
            self.status_label.set_text(self.status_message)
            self.status_label.change_object_id(self._status_object_id())
            self.start_button.disable()

    def _build_quiz_ui(self) -> None:
        question = self.session.current_question if self.session is not None else None
        if question is None:
            self._reset_quiz_state("No active question is available.")
            self.app.router.navigate("home")
            return

        self.question_box = pygame_gui.elements.UITextBox(
            html_text=self._html_text(question.question),
            relative_rect=pygame.Rect(214, 264, 558, 146),
            manager=self.app.ui_manager,
        )
        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(834, 694, 250, 24),
            text=self.status_message,
            manager=self.app.ui_manager,
            object_id=self._status_object_id(),
        )
        self.ui_elements.extend([self.question_box, self.status_label])

        answer_top = 442
        if question.type == "mcq":
            self._build_mcq_options(question.options, answer_top)
            feedback_top = 632
        elif question.type == "blank":
            self.answer_entry_line = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect(214, answer_top, 558, 52),
                manager=self.app.ui_manager,
                object_id="#text_entry",
            )
            self.answer_entry_line.set_text(self.current_text_answer)
            self.ui_elements.append(self.answer_entry_line)
            feedback_top = 522
        else:
            self.answer_entry_box = pygame_gui.elements.UITextEntryBox(
                initial_text=self.current_text_answer,
                relative_rect=pygame.Rect(214, answer_top, 558, 110),
                manager=self.app.ui_manager,
                object_id="#text_entry",
            )
            self.ui_elements.append(self.answer_entry_box)
            feedback_top = 562

        if self.session.last_submission is None:
            self.submit_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(214, 686, 180, 44),
                text="Submit Answer",
                manager=self.app.ui_manager,
                object_id="#primary_button",
            )
            self.ui_elements.append(self.submit_button)
        else:
            self.feedback_box = pygame_gui.elements.UITextBox(
                html_text=self._build_feedback_html(self.session.last_submission),
                relative_rect=pygame.Rect(214, feedback_top, 558, 74),
                manager=self.app.ui_manager,
            )
            button_text = "Next Question" if self.session.current_index < self.session.total_questions - 1 else "View Results"
            self.next_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(214, 686, 180, 44),
                text=button_text,
                manager=self.app.ui_manager,
                object_id="#primary_button",
            )
            self.ui_elements.extend([self.feedback_box, self.next_button])
            self._lock_answer_controls()

    def _build_mcq_options(self, options: list[str], top: int) -> None:
        for index, option in enumerate(options[:4]):
            rect = pygame.Rect(214, top + index * 48, 558, 42)
            object_id = "#primary_button" if self.selected_option == option else "#secondary_button"
            button = pygame_gui.elements.UIButton(
                relative_rect=rect,
                text=option,
                manager=self.app.ui_manager,
                object_id=object_id,
            )
            self.option_buttons.append((option, button))
            self.ui_elements.append(button)

    def _lock_answer_controls(self) -> None:
        if self.answer_entry_line is not None:
            self.answer_entry_line.disable()
        if self.answer_entry_box is not None:
            self.answer_entry_box.disable()
        for _, button in self.option_buttons:
            button.disable()

    def _start_quiz(self) -> None:
        self.pending_question_count = self._selected_dropdown_value(self.count_dropdown, "10")
        self.pending_difficulty = self._selected_dropdown_value(self.difficulty_dropdown, "all")
        self.pending_category = self._selected_dropdown_value(self.category_dropdown, "all")

        session, message = self.app.quiz_service.create_session(
            question_count=int(self.pending_question_count),
            difficulty=self.pending_difficulty,
            category=self.pending_category,
        )
        self.status_message = message
        self.status_kind = "info" if session is not None else "error"

        if session is None:
            self.rebuild_ui()
            return

        self.session = session
        self.selected_option = ""
        self.current_text_answer = ""
        self.rebuild_ui()

    def _submit_answer(self) -> None:
        if self.session is None:
            return

        answer = self._read_current_answer()
        submission = self.app.quiz_service.submit_answer(self.session, answer)
        if not submission.accepted:
            self.status_message = submission.message
            self.status_kind = "error"
            self.rebuild_ui()
            return

        self.status_message = submission.message
        self.status_kind = "success" if submission.is_correct else "error"
        self.current_text_answer = submission.user_answer
        self.rebuild_ui()

    def _go_to_next_question(self) -> None:
        if self.session is None:
            return
        has_next = self.app.quiz_service.advance_to_next_question(self.session)
        if has_next:
            self.selected_option = ""
            self.current_text_answer = ""
            self.status_message = "Continue to the next question."
            self.status_kind = "info"
            self.rebuild_ui()
            return

        result = self.app.quiz_service.build_result(self.session)
        self.app.latest_quiz_result = result
        save_success, save_message, record = self.app.quiz_history_service.save_result(self.app.current_user, result)
        self.app.latest_quiz_record = record
        self.app.latest_quiz_save_message = save_message

        self.session = None
        self.selected_option = ""
        self.current_text_answer = ""
        self.status_message = save_message
        self.status_kind = "success" if save_success else "error"
        self.app.router.navigate("result")

    def _read_current_answer(self) -> str:
        if self.session is None or self.session.current_question is None:
            return ""
        question_type = self.session.current_question.type
        if question_type == "mcq":
            return self.selected_option
        if question_type == "blank" and self.answer_entry_line is not None:
            return self.answer_entry_line.get_text()
        if question_type == "output" and self.answer_entry_box is not None:
            return self.answer_entry_box.get_text()
        return ""

    def _reset_quiz_state(self, message: str) -> None:
        self.session = None
        self.selected_option = ""
        self.current_text_answer = ""
        self.status_message = message
        self.status_kind = "info"

    def _draw_setup_panels(self, surface: pygame.Surface) -> None:
        setup_rect = pygame.Rect(220, 230, 520, 500)
        info_rect = pygame.Rect(790, 230, 290, 500)
        self._draw_panel(
            surface,
            setup_rect,
            title="Quiz Setup",
            subtitle="Pick the question count, difficulty, and category before starting.",
            accent=ACCENT,
        )
        self._draw_panel(
            surface,
            info_rect,
            title="How It Works",
            subtitle="The quiz flow stays simple and clear for classroom demonstration.",
            accent="#A78BFA",
        )

        notes = [
            "Questions are sampled randomly by count, difficulty, and category.",
            "Only one question appears at a time.",
            "Feedback and explanation appear immediately after submission.",
            "Results are saved to quiz history after the quiz is finished.",
        ]
        body_font = pygame.font.SysFont(UI_FONT_NAME, 17)
        for index, note in enumerate(notes):
            for offset, line in enumerate(self._wrap_text(f"{index + 1}. {note}", 22)[:2]):
                surface.blit(body_font.render(line, True, pygame.Color("#94A3B8")), (info_rect.left + 22, info_rect.top + 94 + index * 64 + offset * 18))

        total_questions = len(self.app.question_service.load_questions())
        self._draw_metric_card(
            surface,
            pygame.Rect(info_rect.left + 20, info_rect.bottom - 150, info_rect.width - 40, 110),
            "Available Questions",
            str(total_questions),
            "A clear warning appears when the question bank is empty.",
            WARNING,
        )
        self._draw_status_banner(surface, pygame.Rect(256, 672, 420, 38), self.status_message, self.status_kind)

    def _draw_quiz_panels(self, surface: pygame.Surface) -> None:
        if self.session is None or self.session.current_question is None:
            return
        question_rect = pygame.Rect(180, 220, 620, 520)
        info_rect = pygame.Rect(830, 220, 270, 520)
        self._draw_panel(
            surface,
            question_rect,
            title=f"Question {self.session.current_index + 1} / {self.session.total_questions}",
            subtitle="Read the prompt, answer below, and review the feedback panel.",
            accent=ACCENT,
        )
        self._draw_panel(
            surface,
            info_rect,
            title="Quiz Status",
            subtitle="Track score, progress, filters, and elapsed time in real time.",
            accent="#A78BFA",
        )

        self._draw_progress_bar(
            surface,
            pygame.Rect(info_rect.left + 20, info_rect.top + 92, info_rect.width - 40, 18),
            self.session.progress_ratio,
            f"Progress: {self.session.answered_count} / {self.session.total_questions}",
        )

        self._draw_metric_card(
            surface,
            pygame.Rect(info_rect.left + 20, info_rect.top + 138, info_rect.width - 40, 86),
            "Current Score",
            str(self.session.correct_count),
            "Correct answers increase the score immediately.",
            SUCCESS,
        )
        self._draw_chip(surface, pygame.Rect(info_rect.left + 20, info_rect.top + 246, 86, 28), self.session.current_question.difficulty, self.session.current_question.difficulty)
        self._draw_chip(surface, pygame.Rect(info_rect.left + 116, info_rect.top + 246, 124, 28), self._type_name(self.session.current_question.type), "info")

        self._draw_key_value_lines(
            surface,
            info_rect.left + 20,
            info_rect.top + 294,
            [
                ("Category", self.session.current_question.category),
                ("Time", self.app.quiz_service.format_duration(self.session.elapsed_seconds)),
                ("State", "Waiting" if self.session.last_submission is None else "Submitted"),
            ],
            line_gap=34,
        )

        self._draw_status_banner(
            surface,
            pygame.Rect(info_rect.left + 20, info_rect.bottom - 74, info_rect.width - 40, 44),
            "Submit your answer to see Correct or Incorrect feedback with the explanation.",
            "info",
        )

        label_font = pygame.font.SysFont(UI_FONT_NAME, 18, bold=True)
        surface.blit(label_font.render("Answer Area", True, pygame.Color("#E2E8F0")), (question_rect.left + 24, question_rect.top + 198))

    def _build_feedback_html(self, submission: QuizSubmissionResult) -> str:
        tone = ui_text.CORRECT if submission.is_correct else ui_text.INCORRECT
        correct_answer = escape(submission.correct_answer).replace("\n", "<br>")
        explanation = escape(submission.explanation).replace("\n", "<br>")
        return (
            f"<b>{tone}</b><br>"
            f"<b>Correct Answer:</b> {correct_answer}<br>"
            f"<b>Explanation:</b> {explanation}"
        )

    def _html_text(self, text: str) -> str:
        return escape(text).replace("\n", "<br>")

    def _selected_dropdown_value(self, dropdown: pygame_gui.elements.UIDropDownMenu | None, default_value: str) -> str:
        if dropdown is None:
            return default_value
        selected = dropdown.selected_option
        return selected[0] if isinstance(selected, tuple) else str(selected)

    def _status_object_id(self) -> str:
        if self.status_kind == "success":
            return "#status_success"
        if self.status_kind == "error":
            return "#status_error"
        return "#status_info"

    def _type_name(self, question_type: str) -> str:
        return {"mcq": "MCQ", "blank": "Blank", "output": "Output"}.get(question_type, question_type)

    def on_logout(self) -> None:
        self.session = None
        self.selected_option = ""
        self.current_text_answer = ""
        self.status_message = ui_text.QUIZ_SETUP_HINT
        self.status_kind = "info"
