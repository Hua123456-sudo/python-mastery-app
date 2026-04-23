from __future__ import annotations

from html import escape

import pygame
import pygame_gui

from src.ui.theme import (
    ANALYTICS_ACCENT,
    QUIZ_ACCENT,
    SUCCESS,
    TEXT_MUTED,
    TEXT_PRIMARY,
    UI_FONT_NAME,
)
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
        self.question_box: pygame_gui.elements.UITextBox | None = None
        self.feedback_box: pygame_gui.elements.UITextBox | None = None
        self.option_buttons: list[tuple[str, pygame_gui.elements.UIButton]] = []

        self.pending_question_count = "2"
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

        header = self._get_header_layout()
        self._draw_panel(
            surface,
            header["header_panel"],
            accent=QUIZ_ACCENT,
        )

        if self.session is None:
            self._draw_setup_panels(surface)
        else:
            self._draw_quiz_panels(surface)

    # ----------------------------
    # UI build
    # ----------------------------
    def _build_header(self) -> None:
        layout = self._get_header_layout()

        title = pygame_gui.elements.UILabel(
            relative_rect=layout["title_rect"],
            text="Python Mastery Quiz",
            manager=self.app.ui_manager,
            object_id="#screen_title",
        )
        subtitle = pygame_gui.elements.UILabel(
            relative_rect=layout["subtitle_rect"],
            text="Set up your quiz, then answer one question at a time.",
            manager=self.app.ui_manager,
            object_id="#screen_subtitle",
        )
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=layout["back_button_rect"],
            text=ui_text.BACK_HOME,
            manager=self.app.ui_manager,
            object_id="#back_home_button",
        )

        self.ui_elements.extend([title, subtitle, self.back_button])

    def _build_setup_ui(self) -> None:
        layout = self._get_setup_layout()
        category_options = self.app.quiz_service.get_category_options()
        if self.pending_category not in category_options:
            self.pending_category = "all"

        labels = [
            ("Question Count", layout["count_label"]),
            ("Difficulty", layout["difficulty_label"]),
            ("Category", layout["category_label"]),
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
            options_list=["2", "5", "10"],
            starting_option=self.pending_question_count,
            relative_rect=layout["count_dropdown"],
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.difficulty_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=["all", "easy", "medium", "hard"],
            starting_option=self.pending_difficulty,
            relative_rect=layout["difficulty_dropdown"],
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.category_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=category_options,
            starting_option=self.pending_category,
            relative_rect=layout["category_dropdown"],
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=layout["start_button"],
            text=ui_text.START_QUIZ,
            manager=self.app.ui_manager,
            object_id="#primary_button",
        )

        self.ui_elements.extend(
            [
                self.count_dropdown,
                self.difficulty_dropdown,
                self.category_dropdown,
                self.start_button,
            ]
        )

        if len(category_options) <= 1 and self.start_button is not None:
            self.status_message = (
                "No question data is available yet. Please add questions to "
                "questions.json before starting a quiz."
            )
            self.status_kind = "error"
            self.start_button.disable()

    def _build_quiz_ui(self) -> None:
        question = self.session.current_question if self.session is not None else None
        if question is None:
            self._reset_quiz_state("No active question is available.")
            self.app.router.navigate("home")
            return

        layout = self._get_quiz_layout(question.type, self.session.last_submission is not None)

        self.question_box = pygame_gui.elements.UITextBox(
            html_text=self._html_text(question.question),
            relative_rect=layout["question_box"],
            manager=self.app.ui_manager,
        )
        self.ui_elements.append(self.question_box)

        if question.type == "mcq":
            if self.session.last_submission is None:
                self._build_mcq_options(question.options, layout["mcq_option_rects"])
        elif question.type == "blank":
            self.answer_entry_line = pygame_gui.elements.UITextEntryLine(
                relative_rect=layout["blank_input"],
                manager=self.app.ui_manager,
                object_id="#text_entry",
            )
            self.answer_entry_line.set_text(self.current_text_answer)
            self.ui_elements.append(self.answer_entry_line)
        else:
            self.answer_entry_box = pygame_gui.elements.UITextEntryBox(
                initial_text=self.current_text_answer,
                relative_rect=layout["output_input"],
                manager=self.app.ui_manager,
                object_id="#text_entry",
            )
            self.ui_elements.append(self.answer_entry_box)

        if self.session.last_submission is None:
            self.submit_button = pygame_gui.elements.UIButton(
                relative_rect=layout["action_button"],
                text="Submit Answer",
                manager=self.app.ui_manager,
                object_id="#primary_button",
            )
            self.ui_elements.append(self.submit_button)
        else:
            self.feedback_box = pygame_gui.elements.UITextBox(
                html_text=self._build_feedback_html(self.session.last_submission),
                relative_rect=layout["feedback_box"],
                manager=self.app.ui_manager,
            )
            button_text = (
                "Next Question"
                if self.session.current_index < self.session.total_questions - 1
                else "View Results"
            )
            self.next_button = pygame_gui.elements.UIButton(
                relative_rect=layout["action_button"],
                text=button_text,
                manager=self.app.ui_manager,
                object_id="#primary_button",
            )
            self.ui_elements.extend([self.feedback_box, self.next_button])
            self._lock_answer_controls()

    def _build_mcq_options(self, options: list[str], rects: list[pygame.Rect]) -> None:
        for index, option in enumerate(options[:4]):
            rect = rects[index]
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

    # ----------------------------
    # quiz logic
    # ----------------------------
    def _start_quiz(self) -> None:
        self.pending_question_count = self._selected_dropdown_value(self.count_dropdown, "2")
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
        save_success, save_message, record = self.app.quiz_history_service.save_result(
            self.app.current_user,
            result,
        )
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

    # ----------------------------
    # draw helpers
    # ----------------------------
    def _draw_setup_panels(self, surface: pygame.Surface) -> None:
        layout = self._get_setup_layout()
        setup_rect = layout["setup_card"]
        info_rect = layout["info_card"]

        self._draw_panel(
            surface,
            setup_rect,
            title="Quiz Setup",
            subtitle="Choose amount, level, and category.",
            accent=QUIZ_ACCENT,
        )
        self._draw_panel(
            surface,
            info_rect,
            title="How It Works",
            subtitle="A quick guide before you begin.",
            accent=ANALYTICS_ACCENT,
        )

        notes = [
            "Questions match your selected filters.",
            "Only one question appears at a time.",
            "Submit once to see instant feedback.",
            "Final results are saved to history.",
        ]

        body_font = pygame.font.SysFont(UI_FONT_NAME, 17)
        note_top = info_rect.top + 110
        line_gap = 54

        for index, note in enumerate(notes):
            lines = self._wrap_by_words(
                body_font,
                f"{index + 1}. {note}",
                info_rect.width - 48,
                max_lines=2,
            )
            for offset, line in enumerate(lines):
                surface.blit(
                    body_font.render(line, True, pygame.Color(TEXT_MUTED)),
                    (info_rect.left + 22, note_top + index * line_gap + offset * 20),
                )

        total_questions = len(self.app.question_service.load_questions())
        self._draw_available_questions_card(surface, layout["questions_card"], total_questions)

    def _draw_quiz_panels(self, surface: pygame.Surface) -> None:
        if self.session is None or self.session.current_question is None:
            return

        layout = self._get_quiz_layout(
            self.session.current_question.type,
            self.session.last_submission is not None,
        )
        question_rect = layout["question_card"]
        info_rect = layout["info_card"]

        self._draw_panel(
            surface,
            question_rect,
            title=f"Question {self.session.current_index + 1} / {self.session.total_questions}",
            accent=QUIZ_ACCENT,
        )
        self._draw_panel(
            surface,
            info_rect,
            title="Quiz Status",
            accent=ANALYTICS_ACCENT,
        )

        self._draw_progress_bar(
            surface,
            pygame.Rect(info_rect.left + 20, info_rect.top + 74, info_rect.width - 40, 18),
            self.session.progress_ratio,
            f"Progress: {self.session.answered_count} / {self.session.total_questions}",
        )

        self._draw_score_card(
            surface,
            pygame.Rect(info_rect.left + 20, info_rect.top + 118, info_rect.width - 40, 86),
            str(self.session.correct_count),
        )

        self._draw_chip(
            surface,
            pygame.Rect(info_rect.left + 20, info_rect.top + 222, 92, 28),
            self.session.current_question.difficulty,
            self.session.current_question.difficulty,
        )
        self._draw_chip(
            surface,
            pygame.Rect(info_rect.left + 124, info_rect.top + 222, 116, 28),
            self._type_name(self.session.current_question.type),
            "info",
        )

        self._draw_key_value_lines(
            surface,
            info_rect.left + 20,
            info_rect.top + 268,
            [
                ("Category", self.session.current_question.category),
                ("Time", self.app.quiz_service.format_duration(self.session.elapsed_seconds)),
                ("State", "Waiting" if self.session.last_submission is None else "Submitted"),
            ],
            line_gap=34,
        )

        self._draw_status_banner(
            surface,
            layout["status_bar"],
            self.status_message,
            self.status_kind,
        )

        label_font = pygame.font.SysFont(UI_FONT_NAME, 19, bold=True)
        surface.blit(
            label_font.render("Answer Area", True, pygame.Color(TEXT_PRIMARY)),
            layout["answer_label"],
        )

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

    def _selected_dropdown_value(
        self,
        dropdown: pygame_gui.elements.UIDropDownMenu | None,
        default_value: str,
    ) -> str:
        if dropdown is None:
            return default_value
        selected = dropdown.selected_option
        return selected[0] if isinstance(selected, tuple) else str(selected)

    def _type_name(self, question_type: str) -> str:
        return {"mcq": "MCQ", "blank": "Blank", "output": "Output"}.get(question_type, question_type)

    # ----------------------------
    # layout
    # ----------------------------
    def _get_header_layout(self) -> dict[str, pygame.Rect]:
        content = self.get_content_rect(48, 28)
        header_top = content.top + 6
        header_height = 86

        header_panel = pygame.Rect(content.left, header_top, content.width, header_height)
        back_button_rect = pygame.Rect(content.left + 12, header_top + 12, 136, 44)

        return {
            "content_rect": content,
            "header_panel": header_panel,
            "back_button_rect": back_button_rect,
            "title_rect": pygame.Rect(content.left + 180, header_top + 4, content.width - 220, 52),
            "subtitle_rect": pygame.Rect(content.left + 180, header_top + 50, content.width - 220, 30),
            "main_top": header_top + header_height + 22,
        }

    def _get_setup_layout(self) -> dict[str, pygame.Rect]:
        header = self._get_header_layout()
        content = header["content_rect"]
        main_top = header["main_top"]

        gutter = 28
        bottom_margin = 24
        cards_height = content.bottom - main_top - bottom_margin

        left_width = max(560, min(640, int(content.width * 0.58)))
        right_width = content.width - left_width - gutter
        if right_width < 380:
            right_width = 380
            left_width = content.width - right_width - gutter

        setup_card = pygame.Rect(content.left, main_top, left_width, cards_height)
        info_card = pygame.Rect(setup_card.right + gutter, main_top, right_width, cards_height)

        form_left = setup_card.left + 32
        form_width = setup_card.width - 64

        label_h = 24
        dropdown_h = 44
        dropdown_offset = 30
        block_gap = 82
        first_block_top = setup_card.top + 126

        count_label_y = first_block_top
        difficulty_label_y = count_label_y + block_gap
        category_label_y = difficulty_label_y + block_gap
        start_button_y = min(
            category_label_y + dropdown_offset + dropdown_h + 54,
            setup_card.bottom - 86,
        )

        return {
            "setup_card": setup_card,
            "info_card": info_card,

            "count_label": pygame.Rect(form_left, count_label_y, 220, label_h),
            "count_dropdown": pygame.Rect(form_left, count_label_y + dropdown_offset, form_width, dropdown_h),

            "difficulty_label": pygame.Rect(form_left, difficulty_label_y, 220, label_h),
            "difficulty_dropdown": pygame.Rect(form_left, difficulty_label_y + dropdown_offset, form_width, dropdown_h),

            "category_label": pygame.Rect(form_left, category_label_y, 220, label_h),
            "category_dropdown": pygame.Rect(form_left, category_label_y + dropdown_offset, form_width, dropdown_h),

            "start_button": pygame.Rect(setup_card.left + 24, start_button_y, 230, 50),

            "questions_card": pygame.Rect(
                info_card.left + 20,
                info_card.bottom - 140,
                info_card.width - 40,
                132,
            ),
        }

    def _get_quiz_layout(
        self,
        question_type: str,
        has_submission: bool,
    ) -> dict[str, pygame.Rect | tuple[int, int] | list[pygame.Rect]]:
        header = self._get_header_layout()
        content = header["content_rect"]
        main_top = header["main_top"]

        gutter = 28
        left_width = max(620, min(760, int(content.width * 0.67)))
        right_width = content.width - left_width - gutter
        if right_width < 300:
            right_width = 300
            left_width = content.width - right_width - gutter

        card_height = content.bottom - main_top - 6

        question_card = pygame.Rect(content.left, main_top, left_width, card_height)
        info_card = pygame.Rect(question_card.right + gutter, main_top, right_width, card_height)

        pad_x = 26
        inner_left = question_card.left + pad_x
        inner_width = question_card.width - pad_x * 2

        question_box = pygame.Rect(inner_left, question_card.top + 96, inner_width, 112)
        question_box = pygame.Rect(inner_left, question_card.top + 74, inner_width, 112)
        answer_label_pos = (inner_left, question_box.bottom + 18)

        status_bar = pygame.Rect(info_card.left + 18, info_card.bottom - 72, info_card.width - 36, 42)

        rects: dict[str, pygame.Rect | tuple[int, int] | list[pygame.Rect]] = {
            "question_card": question_card,
            "info_card": info_card,
            "question_box": question_box,
            "answer_label": answer_label_pos,
            "status_bar": status_bar,
        }

        if question_type == "mcq":
            option_height = 40
            option_gap = 12
            options_top = question_box.bottom + 62
            option_rects = [
                pygame.Rect(
                    inner_left,
                    options_top + index * (option_height + option_gap),
                    inner_width,
                    option_height,
                )
                for index in range(4)
            ]
            rects["mcq_option_rects"] = option_rects
            action_y = option_rects[-1].bottom + 24

            if has_submission:
                feedback_box = pygame.Rect(
                    inner_left,
                    question_box.bottom + 62,
                    inner_width,
                    118,
                )
                rects["feedback_box"] = feedback_box
                action_y = feedback_box.bottom + 24

        elif question_type == "blank":
            blank_input = pygame.Rect(inner_left, question_box.bottom + 62, inner_width, 50)
            rects["blank_input"] = blank_input
            action_y = blank_input.bottom + 24
            if has_submission:
                feedback_box = pygame.Rect(
                    inner_left,
                    question_box.bottom + 130,
                    inner_width,
                    118,
                )
                rects["feedback_box"] = feedback_box
                action_y = feedback_box.bottom + 24
        else:
            output_input = pygame.Rect(inner_left, question_box.bottom + 62, inner_width, 108)
            rects["output_input"] = output_input
            action_y = output_input.bottom + 24
            if has_submission:
                feedback_box = pygame.Rect(
                    inner_left,
                    question_box.bottom + 186,
                    inner_width,
                    118,
                )
                rects["feedback_box"] = feedback_box
                action_y = feedback_box.bottom + 24

        rects["action_button"] = pygame.Rect(question_card.left + 20, action_y, 200, 46)

        return rects

    # ----------------------------
    # small drawing utilities
    # ----------------------------
    def _draw_available_questions_card(self, surface: pygame.Surface, rect: pygame.Rect, total_questions: int) -> None:
        self._draw_panel(surface, rect)

        title_font = pygame.font.SysFont(UI_FONT_NAME, 17, bold=True)
        value_font = pygame.font.SysFont(UI_FONT_NAME, 42, bold=True)
        body_font = pygame.font.SysFont(UI_FONT_NAME, 16)

        title_surface = title_font.render("Available Questions", True, pygame.Color(TEXT_PRIMARY))
        value_surface = value_font.render(str(total_questions), True, pygame.Color(TEXT_PRIMARY))
        body_surface = body_font.render("Ready for this quiz.", True, pygame.Color(TEXT_MUTED))

        surface.blit(title_surface, (rect.left + 18, rect.top + 14))
        value_x = rect.right - value_surface.get_width() - 22
        surface.blit(value_surface, (value_x, rect.top + 46))
        surface.blit(body_surface, (rect.left + 18, rect.top + 96))

    def _draw_score_card(self, surface: pygame.Surface, rect: pygame.Rect, score_value: str) -> None:
        self._draw_panel(surface, rect)
        dot_rect_x = rect.left + 24
        pygame.draw.circle(surface, pygame.Color(SUCCESS), (dot_rect_x, rect.top + 28), 7)

        label_font = pygame.font.SysFont(UI_FONT_NAME, 17, bold=True)
        value_font = pygame.font.SysFont(UI_FONT_NAME, 42, bold=True)

        label_surface = label_font.render("Current Score", True, pygame.Color(TEXT_PRIMARY))
        surface.blit(label_surface, (rect.left + 40, rect.top + 18))

        value_surface = value_font.render(score_value, True, pygame.Color(TEXT_PRIMARY))
        value_x = rect.right - value_surface.get_width() - 22
        surface.blit(value_surface, (value_x, rect.top + 34))

    def _wrap_by_words(
        self,
        font: pygame.font.Font,
        text: str,
        max_width: int,
        max_lines: int = 2,
    ) -> list[str]:
        words = (text or "").split()
        if not words:
            return [""]

        lines: list[str] = []
        current = ""

        for word in words:
            candidate = word if not current else f"{current} {word}"
            if font.size(candidate)[0] <= max_width:
                current = candidate
                continue

            if current:
                lines.append(current)
            current = word
            if len(lines) == max_lines - 1:
                break

        remaining_index = len(" ".join(lines + ([current] if current else [])).split())
        remaining_words = words[remaining_index:]
        final_line = current
        if remaining_words:
            final_line = f"{final_line} {' '.join(remaining_words)}".strip()

        if final_line:
            trimmed = final_line
            while trimmed and font.size(trimmed)[0] > max_width:
                trimmed = trimmed[:-1]
            if trimmed != final_line and len(trimmed) > 3:
                trimmed = trimmed[:-3].rstrip() + "..."
            lines.append(trimmed or "...")

        return lines[:max_lines]

    def on_logout(self) -> None:
        self.session = None
        self.selected_option = ""
        self.current_text_answer = ""
        self.status_message = ui_text.QUIZ_SETUP_HINT
        self.status_kind = "info"

