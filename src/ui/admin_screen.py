from __future__ import annotations

from html import escape

import pygame
import pygame_gui

from src.config import ACCENT, CARD_BORDER, TEXT_MUTED, TEXT_PRIMARY, UI_FONT_NAME
from src.models.question import Question
from src.ui import ui_text
from src.ui.base_screen import BaseScreen


class AdminScreen(BaseScreen):
    """Admin question bank management screen."""

    def __init__(self, app) -> None:
        super().__init__(app, "admin")
        self.status_message = "Select a question to preview or edit."
        self.status_kind = "info"
        self.current_mode = "edit"
        self.original_question_id: str | None = None
        self.selected_question_id: str | None = None
        self.delete_confirmation_required = False
        self.filtered_questions: list[Question] = []
        self.visible_question_rows: list[tuple[pygame.Rect, str]] = []
        self.current_page = 0
        self.page_size = 7
        self._form_snapshot: dict[str, object] | None = None

        self.back_button: pygame_gui.elements.UIButton | None = None
        self.apply_button: pygame_gui.elements.UIButton | None = None
        self.reset_filter_button: pygame_gui.elements.UIButton | None = None
        self.prev_page_button: pygame_gui.elements.UIButton | None = None
        self.next_page_button: pygame_gui.elements.UIButton | None = None
        self.new_button: pygame_gui.elements.UIButton | None = None
        self.save_button: pygame_gui.elements.UIButton | None = None
        self.delete_button: pygame_gui.elements.UIButton | None = None
        self.confirm_delete_button: pygame_gui.elements.UIButton | None = None

        self.search_input: pygame_gui.elements.UITextEntryLine | None = None
        self.type_filter_dropdown: pygame_gui.elements.UIDropDownMenu | None = None
        self.difficulty_filter_dropdown: pygame_gui.elements.UIDropDownMenu | None = None
        self.category_filter_dropdown: pygame_gui.elements.UIDropDownMenu | None = None

        self.id_input: pygame_gui.elements.UITextEntryLine | None = None
        self.type_dropdown: pygame_gui.elements.UIDropDownMenu | None = None
        self.category_input: pygame_gui.elements.UITextEntryLine | None = None
        self.difficulty_dropdown: pygame_gui.elements.UIDropDownMenu | None = None
        self.source_input: pygame_gui.elements.UITextEntryLine | None = None
        self.question_box: pygame_gui.elements.UITextEntryBox | None = None
        self.options_box: pygame_gui.elements.UITextEntryBox | None = None
        self.answer_box: pygame_gui.elements.UITextEntryBox | None = None
        self.explanation_box: pygame_gui.elements.UITextEntryBox | None = None
        self.status_label: pygame_gui.elements.UILabel | None = None

        self.keyword_value = ""
        self.type_filter_value = "all"
        self.difficulty_filter_value = "all"
        self.category_filter_value = "all"

    def enter(self) -> None:
        if not self._is_admin():
            self.app.home_notice_message = ui_text.ADMIN_ONLY_NOTICE
            self.app.home_notice_kind = "error"
            self.app.router.navigate("home")
            return

        self._refresh_filtered_questions()
        if self.selected_question_id is None and self.filtered_questions:
            self._load_question_into_form(self.filtered_questions[0])
        super().enter()

    def rebuild_ui(self) -> None:
        self.clear_ui()
        self.visible_question_rows.clear()

        category_options = self.app.question_service.get_category_options()
        if self.category_filter_value not in category_options:
            self.category_filter_value = "all"

        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(180, 116, 120, 44),
            text=ui_text.BACK_HOME,
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(250, 118, 380, 44),
            text=ui_text.ADMIN_PANEL,
            manager=self.app.ui_manager,
            object_id="#screen_title",
        )
        subtitle = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(250, 160, 640, 28),
            text="Search, filter, create, edit, and delete questions stored in questions.json.",
            manager=self.app.ui_manager,
            object_id="#screen_subtitle",
        )

        self.search_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(200, 254, 250, 42),
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.search_input.set_text(self.keyword_value)
        self.type_filter_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.app.question_service.get_type_options(),
            starting_option=self.type_filter_value,
            relative_rect=pygame.Rect(200, 306, 120, 40),
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.difficulty_filter_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.app.question_service.get_difficulty_options(),
            starting_option=self.difficulty_filter_value,
            relative_rect=pygame.Rect(330, 306, 120, 40),
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.category_filter_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=category_options,
            starting_option=self.category_filter_value,
            relative_rect=pygame.Rect(200, 356, 250, 40),
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.apply_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(200, 408, 120, 40),
            text="Apply",
            manager=self.app.ui_manager,
            object_id="#primary_button",
        )
        self.reset_filter_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(330, 408, 120, 40),
            text="Reset",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        self.prev_page_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(200, 710, 110, 38),
            text="Previous",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        self.next_page_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(340, 710, 110, 38),
            text="Next",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )

        type_options = [option for option in self.app.question_service.get_type_options() if option != "all"]
        difficulty_options = [option for option in self.app.question_service.get_difficulty_options() if option != "all"]
        preview_question = self._read_form_question()
        starting_type = preview_question.type if preview_question.type in type_options else type_options[0]
        starting_difficulty = preview_question.difficulty if preview_question.difficulty in difficulty_options else difficulty_options[0]

        self.id_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(540, 252, 120, 40),
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.id_input.set_text(preview_question.id)
        self.type_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=type_options,
            starting_option=starting_type,
            relative_rect=pygame.Rect(670, 252, 100, 40),
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.difficulty_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=difficulty_options,
            starting_option=starting_difficulty,
            relative_rect=pygame.Rect(780, 252, 100, 40),
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.category_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(540, 304, 170, 40),
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.category_input.set_text(preview_question.category)
        self.source_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(720, 304, 160, 40),
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.source_input.set_text(preview_question.source)
        self.question_box = pygame_gui.elements.UITextEntryBox(
            initial_text=preview_question.question,
            relative_rect=pygame.Rect(540, 370, 340, 82),
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.options_box = pygame_gui.elements.UITextEntryBox(
            initial_text="\n".join(preview_question.options),
            relative_rect=pygame.Rect(540, 474, 340, 68),
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.answer_box = pygame_gui.elements.UITextEntryBox(
            initial_text=preview_question.answer,
            relative_rect=pygame.Rect(540, 564, 340, 54),
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.explanation_box = pygame_gui.elements.UITextEntryBox(
            initial_text=preview_question.explanation,
            relative_rect=pygame.Rect(540, 640, 340, 78),
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.new_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(540, 728, 80, 34),
            text="New",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(630, 728, 80, 34),
            text="Save",
            manager=self.app.ui_manager,
            object_id="#primary_button",
        )
        self.delete_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(720, 728, 80, 34),
            text="Delete",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        self.confirm_delete_button = None
        if self.delete_confirmation_required and self.current_mode == "edit":
            self.confirm_delete_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(810, 728, 70, 34),
                text="Confirm",
                manager=self.app.ui_manager,
                object_id="#primary_button",
            )
        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(540, 764, 340, 24),
            text=self.status_message,
            manager=self.app.ui_manager,
            object_id=self._status_object_id(),
        )

        elements = [
            self.back_button,
            title,
            subtitle,
            self.search_input,
            self.type_filter_dropdown,
            self.difficulty_filter_dropdown,
            self.category_filter_dropdown,
            self.apply_button,
            self.reset_filter_button,
            self.prev_page_button,
            self.next_page_button,
            self.id_input,
            self.type_dropdown,
            self.difficulty_dropdown,
            self.category_input,
            self.source_input,
            self.question_box,
            self.options_box,
            self.answer_box,
            self.explanation_box,
            self.new_button,
            self.save_button,
            self.delete_button,
            self.status_label,
        ]
        if self.confirm_delete_button is not None:
            elements.append(self.confirm_delete_button)

        self.ui_elements.extend(elements)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._handle_list_click(event.pos):
                return

        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return

        if event.ui_element == self.back_button:
            self.app.router.navigate("home")
            return
        if event.ui_element == self.apply_button:
            self._apply_filters()
            return
        if event.ui_element == self.reset_filter_button:
            self._reset_filters()
            return
        if event.ui_element == self.prev_page_button:
            self.current_page = max(0, self.current_page - 1)
            self.rebuild_ui()
            return
        if event.ui_element == self.next_page_button:
            total_pages = max(1, (len(self.filtered_questions) + self.page_size - 1) // self.page_size)
            self.current_page = min(total_pages - 1, self.current_page + 1)
            self.rebuild_ui()
            return
        if event.ui_element == self.new_button:
            self._start_new_question()
            return
        if event.ui_element == self.save_button:
            self._save_form()
            return
        if event.ui_element == self.delete_button:
            self._prepare_delete()
            return
        if event.ui_element == self.confirm_delete_button:
            self._delete_selected_question()

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)

        left_panel = pygame.Rect(180, 220, 300, 560)
        center_panel = pygame.Rect(520, 220, 380, 560)
        right_panel = pygame.Rect(920, 220, 180, 560)

        self._draw_panel(surface, left_panel, title="Question List", subtitle="Search, filter, and browse the question bank.", accent="#38BDF8")
        self._draw_panel(surface, center_panel, title="Edit Form", subtitle="Keep the existing CRUD flow with clearer labels and spacing.", accent="#A78BFA")
        self._draw_panel(surface, right_panel, title="Preview", subtitle="Check the summary before saving any change.", accent="#F59E0B")

        font_title = pygame.font.SysFont(UI_FONT_NAME, 20, bold=True)
        font_body = pygame.font.SysFont(UI_FONT_NAME, 16)
        font_small = pygame.font.SysFont(UI_FONT_NAME, 14)

        surface.blit(font_title.render("Question List", True, pygame.Color(TEXT_PRIMARY)), (left_panel.left + 20, left_panel.top + 16))
        surface.blit(font_title.render("Edit Form", True, pygame.Color(TEXT_PRIMARY)), (center_panel.left + 20, center_panel.top + 16))
        surface.blit(font_title.render("Preview", True, pygame.Color(TEXT_PRIMARY)), (right_panel.left + 20, right_panel.top + 16))

        self._draw_list_rows(surface, left_panel)
        self._draw_form_labels(surface, center_panel, font_body)
        self._draw_preview(surface, right_panel, font_body, font_small)

    def _draw_list_rows(self, surface: pygame.Surface, panel: pygame.Rect) -> None:
        self.visible_question_rows.clear()
        font_body = pygame.font.SysFont(UI_FONT_NAME, 14)
        font_small = pygame.font.SysFont(UI_FONT_NAME, 12)

        if not self.filtered_questions:
            empty_surface = font_body.render("No questions match the current filters.", True, pygame.Color(TEXT_MUTED))
            surface.blit(empty_surface, (panel.left + 20, panel.top + 250))
            return

        start = self.current_page * self.page_size
        end = start + self.page_size
        visible = self.filtered_questions[start:end]

        for index, question in enumerate(visible):
            row_rect = pygame.Rect(panel.left + 14, panel.top + 250 + index * 58, panel.width - 28, 50)
            is_selected = question.id == self.selected_question_id
            bg_color = pygame.Color("#20304B") if is_selected else pygame.Color("#141D2E")
            pygame.draw.rect(surface, bg_color, row_rect, border_radius=14)
            pygame.draw.rect(surface, pygame.Color(CARD_BORDER), row_rect, width=1, border_radius=14)

            header_text = f"{question.id}  {question.type}  {question.category}"
            surface.blit(font_body.render(header_text[:34], True, pygame.Color(TEXT_PRIMARY)), (row_rect.left + 12, row_rect.top + 8))
            summary = question.question.replace("\n", " ")
            surface.blit(font_small.render(summary[:40], True, pygame.Color(TEXT_MUTED)), (row_rect.left + 12, row_rect.top + 28))

            tag_rect = pygame.Rect(row_rect.right - 72, row_rect.top + 12, 58, 22)
            pygame.draw.rect(surface, self._difficulty_color(question.difficulty), tag_rect, border_radius=11)
            tag_surface = font_small.render(question.difficulty, True, pygame.Color("#08111F"))
            surface.blit(tag_surface, tag_surface.get_rect(center=tag_rect.center))

            self.visible_question_rows.append((row_rect, question.id))

        page_count = max(1, (len(self.filtered_questions) + self.page_size - 1) // self.page_size)
        footer_font = pygame.font.SysFont(UI_FONT_NAME, 13)
        footer = f"Page {self.current_page + 1} / {page_count}   Total {len(self.filtered_questions)}"
        surface.blit(footer_font.render(footer, True, pygame.Color(TEXT_MUTED)), (panel.left + 20, panel.bottom - 26))

    def _draw_form_labels(self, surface: pygame.Surface, panel: pygame.Rect, font: pygame.font.Font) -> None:
        labels = [
            ("ID", (panel.left + 20, panel.top + 32)),
            ("Type", (panel.left + 150, panel.top + 32)),
            ("Difficulty", (panel.left + 258, panel.top + 32)),
            ("Category", (panel.left + 20, panel.top + 84)),
            ("Source", (panel.left + 200, panel.top + 84)),
            ("Question", (panel.left + 20, panel.top + 150)),
            ("Options (one option per line for MCQ)", (panel.left + 20, panel.top + 254)),
            ("Answer", (panel.left + 20, panel.top + 344)),
            ("Explanation", (panel.left + 20, panel.top + 420)),
        ]
        for text, pos in labels:
            surface.blit(font.render(text, True, pygame.Color(TEXT_MUTED)), pos)

    def _draw_preview(self, surface: pygame.Surface, panel: pygame.Rect, font_body: pygame.font.Font, font_small: pygame.font.Font) -> None:
        question = self._read_form_question()

        header_lines = [
            f"Mode: {'New Question' if self.current_mode == 'new' else 'Edit Question'}",
            f"ID: {question.id or '--'}",
            f"Type: {question.type}",
            f"Category: {question.category or '--'}",
            f"Source: {question.source or '--'}",
        ]
        for index, line in enumerate(header_lines):
            surface.blit(font_small.render(line, True, pygame.Color(TEXT_MUTED)), (panel.left + 16, panel.top + 52 + index * 22))

        tag_rect = pygame.Rect(panel.left + 16, panel.top + 164, 80, 24)
        pygame.draw.rect(surface, self._difficulty_color(question.difficulty), tag_rect, border_radius=12)
        tag_surface = font_small.render(question.difficulty, True, pygame.Color("#08111F"))
        surface.blit(tag_surface, tag_surface.get_rect(center=tag_rect.center))

        preview_lines = [
            ("Question", question.question),
            ("Options", "\n".join(question.options) if question.options else "None"),
            ("Answer", question.answer),
            ("Explanation", question.explanation),
        ]

        y = panel.top + 208
        for title, content in preview_lines:
            surface.blit(font_body.render(title, True, pygame.Color(TEXT_PRIMARY)), (panel.left + 16, y))
            y += 24
            for line in self._wrap_preview_text(content or "--", 19):
                surface.blit(font_small.render(line, True, pygame.Color(TEXT_MUTED)), (panel.left + 16, y))
                y += 18
            y += 10

    def _handle_list_click(self, position: tuple[int, int]) -> bool:
        for rect, question_id in self.visible_question_rows:
            if rect.collidepoint(position):
                question = self.app.question_service.get_question_by_id(question_id)
                if question is not None:
                    self._load_question_into_form(question)
                    self.rebuild_ui()
                return True
        return False

    def _apply_filters(self) -> None:
        self.keyword_value = self.search_input.get_text() if self.search_input is not None else ""
        self.type_filter_value = self._dropdown_value(self.type_filter_dropdown, "all")
        self.difficulty_filter_value = self._dropdown_value(self.difficulty_filter_dropdown, "all")
        self.category_filter_value = self._dropdown_value(self.category_filter_dropdown, "all")

        self._refresh_filtered_questions()
        self.status_message = f"{len(self.filtered_questions)} questions match the current filters."
        self.status_kind = "info"
        self.rebuild_ui()

    def _reset_filters(self) -> None:
        self.keyword_value = ""
        self.type_filter_value = "all"
        self.difficulty_filter_value = "all"
        self.category_filter_value = "all"
        self._refresh_filtered_questions()
        self.status_message = "All filters have been reset."
        self.status_kind = "info"
        self.rebuild_ui()

    def _refresh_filtered_questions(self) -> None:
        self.filtered_questions = self.app.question_service.search_questions(
            keyword=self.keyword_value,
            question_type=self.type_filter_value,
            difficulty=self.difficulty_filter_value,
            category=self.category_filter_value,
        )
        total_pages = max(1, (len(self.filtered_questions) + self.page_size - 1) // self.page_size)
        self.current_page = min(self.current_page, total_pages - 1)

    def _start_new_question(self) -> None:
        self.current_mode = "new"
        self.original_question_id = None
        self.selected_question_id = None
        self.delete_confirmation_required = False
        new_question = Question(
            id=self.app.question_service.generate_unique_id(),
            type="mcq",
            category="New Category",
            difficulty="easy",
            question="",
            options=["Option A", "Option B"],
            answer="",
            explanation="",
            source="admin",
        )
        self._set_form_from_question(new_question)
        self.status_message = "A new question draft is ready. Fill in the fields and click Save."
        self.status_kind = "info"
        self.rebuild_ui()

    def _save_form(self) -> None:
        try:
            form_question = self._read_form_question()
            if self.current_mode == "new":
                saved_question = self.app.question_service.add_question(form_question)
                self.current_mode = "edit"
                self.original_question_id = saved_question.id
                self.selected_question_id = saved_question.id
                if saved_question.id != form_question.id.strip():
                    self.status_message = f"Question created. A unique id was generated automatically: {saved_question.id}"
                else:
                    self.status_message = f"Question created: {saved_question.id}"
            else:
                original_id = self.original_question_id or form_question.id
                saved_question = self.app.question_service.update_question(original_id, form_question)
                self.original_question_id = saved_question.id
                self.selected_question_id = saved_question.id
                self.status_message = f"Question saved: {saved_question.id}"

            self.status_kind = "success"
            self.delete_confirmation_required = False
            self._refresh_filtered_questions()
            self._set_form_from_question(saved_question)
            self.rebuild_ui()
        except ValueError as error:
            self.status_message = str(error)
            self.status_kind = "error"
            self.delete_confirmation_required = False
            self.rebuild_ui()

    def _prepare_delete(self) -> None:
        if self.current_mode != "edit" or not self.original_question_id:
            self.status_message = "The current form is a new draft, so there is nothing to delete yet."
            self.status_kind = "error"
            self.rebuild_ui()
            return

        self.delete_confirmation_required = True
        self.status_message = "Click Confirm to delete this question and avoid accidental removal."
        self.status_kind = "error"
        self.rebuild_ui()

    def _delete_selected_question(self) -> None:
        if not self.original_question_id:
            return

        self.app.question_service.delete_question(self.original_question_id)
        self.status_message = f"Question deleted: {self.original_question_id}"
        self.status_kind = "success"
        self.delete_confirmation_required = False
        self._refresh_filtered_questions()

        if self.filtered_questions:
            self._load_question_into_form(self.filtered_questions[0])
        else:
            self.current_mode = "new"
            self.original_question_id = None
            self.selected_question_id = None
            self._set_form_from_question(
                Question(
                    id=self.app.question_service.generate_unique_id(),
                    type="mcq",
                    category="",
                    difficulty="easy",
                    question="",
                    options=["Option A", "Option B"],
                    answer="",
                    explanation="",
                    source="admin",
                )
            )
        self.rebuild_ui()

    def _load_question_into_form(self, question: Question) -> None:
        self.current_mode = "edit"
        self.original_question_id = question.id
        self.selected_question_id = question.id
        self.delete_confirmation_required = False
        self._set_form_from_question(question)

    def _set_form_from_question(self, question: Question) -> None:
        self._form_snapshot = {
            "id": question.id,
            "type": question.type,
            "category": question.category,
            "difficulty": question.difficulty,
            "question": question.question,
            "options": list(question.options),
            "answer": question.answer,
            "explanation": question.explanation,
            "source": question.source,
        }

    def _read_form_question(self) -> Question:
        snapshot = self._form_snapshot

        if self.id_input is None:
            if snapshot is not None:
                return Question(
                    id=str(snapshot["id"]),
                    type=str(snapshot["type"]),
                    category=str(snapshot["category"]),
                    difficulty=str(snapshot["difficulty"]),
                    question=str(snapshot["question"]),
                    options=list(snapshot["options"]),
                    answer=str(snapshot["answer"]),
                    explanation=str(snapshot["explanation"]),
                    source=str(snapshot["source"]),
                )
            return Question(
                id=self.app.question_service.generate_unique_id(),
                type="mcq",
                category="",
                difficulty="easy",
                question="",
                options=[],
                answer="",
                explanation="",
                source="",
            )

        options_text = self.options_box.get_text() if self.options_box is not None else ""
        options = [line.strip() for line in options_text.splitlines() if line.strip()]

        return Question(
            id=self.id_input.get_text(),
            type=self._dropdown_value(self.type_dropdown, "mcq"),
            category=self.category_input.get_text() if self.category_input is not None else "",
            difficulty=self._dropdown_value(self.difficulty_dropdown, "easy"),
            question=self.question_box.get_text() if self.question_box is not None else "",
            options=options,
            answer=self.answer_box.get_text() if self.answer_box is not None else "",
            explanation=self.explanation_box.get_text() if self.explanation_box is not None else "",
            source=self.source_input.get_text() if self.source_input is not None else "",
        )

    def _dropdown_value(self, dropdown: pygame_gui.elements.UIDropDownMenu | None, default_value: str) -> str:
        if dropdown is None:
            return default_value
        selected = dropdown.selected_option
        return selected[0] if isinstance(selected, tuple) else str(selected)

    def _difficulty_color(self, difficulty: str) -> pygame.Color:
        mapping = {
            "easy": pygame.Color("#34D399"),
            "medium": pygame.Color("#38BDF8"),
            "hard": pygame.Color("#F59E0B"),
        }
        return mapping.get(difficulty, pygame.Color(ACCENT))

    def _wrap_preview_text(self, text: str, limit: int) -> list[str]:
        plain_text = escape(text).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        lines: list[str] = []
        for raw_line in plain_text.splitlines() or [""]:
            remaining = raw_line
            while len(remaining) > limit:
                lines.append(remaining[:limit])
                remaining = remaining[limit:]
            lines.append(remaining)
        return lines[:12]

    def _status_object_id(self) -> str:
        if self.status_kind == "success":
            return "#status_success"
        if self.status_kind == "error":
            return "#status_error"
        return "#status_info"

    def _is_admin(self) -> bool:
        return getattr(self.app.current_user, "role", "") == "admin"
