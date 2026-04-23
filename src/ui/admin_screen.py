from __future__ import annotations

import pygame
import pygame_gui

from src.models.question import Question
from src.ui import ui_text
from src.ui.base_screen import BaseScreen
from src.ui.theme import (
    ACCENT,
    ALGORITHM_ACCENT,
    ANALYTICS_ACCENT,
    CARD_BG_SELECTED,
    CARD_BORDER,
    CARD_MUTED,
    CHIP_TEXT_DARK,
    QUIZ_ACCENT,
    SUCCESS,
    TEXT_MUTED,
    TEXT_PRIMARY,
    UI_FONT_NAME,
)


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
        self.page_size = 5
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

        self.form_scroll: pygame_gui.elements.UIScrollingContainer | None = None
        self.id_input: pygame_gui.elements.UITextEntryLine | None = None
        self.type_dropdown: pygame_gui.elements.UIDropDownMenu | None = None
        self.category_input: pygame_gui.elements.UITextEntryLine | None = None
        self.difficulty_dropdown: pygame_gui.elements.UIDropDownMenu | None = None
        self.source_input: pygame_gui.elements.UITextEntryLine | None = None
        self.question_box: pygame_gui.elements.UITextEntryBox | None = None
        self.options_box: pygame_gui.elements.UITextEntryBox | None = None
        self.answer_box: pygame_gui.elements.UITextEntryBox | None = None
        self.explanation_box: pygame_gui.elements.UITextEntryBox | None = None

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
        layout = self._get_layout()

        category_options = self.app.question_service.get_category_options()
        if self.category_filter_value not in category_options:
            self.category_filter_value = "all"

        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=layout["back_button"],
            text=ui_text.BACK_HOME,
            manager=self.app.ui_manager,
            object_id="#back_home_button",
        )
        title = pygame_gui.elements.UILabel(
            relative_rect=layout["title_rect"],
            text=ui_text.ADMIN_PANEL,
            manager=self.app.ui_manager,
            object_id="#screen_title",
        )

        self.search_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=layout["search_input"],
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.search_input.set_text(self.keyword_value)
        self.type_filter_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.app.question_service.get_type_options(),
            starting_option=self.type_filter_value,
            relative_rect=layout["type_filter"],
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.difficulty_filter_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=self.app.question_service.get_difficulty_options(),
            starting_option=self.difficulty_filter_value,
            relative_rect=layout["difficulty_filter"],
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.category_filter_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=category_options,
            starting_option=self.category_filter_value,
            relative_rect=layout["category_filter"],
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.apply_button = pygame_gui.elements.UIButton(
            relative_rect=layout["apply_button"],
            text="Apply",
            manager=self.app.ui_manager,
            object_id="#primary_button",
        )
        self.reset_filter_button = pygame_gui.elements.UIButton(
            relative_rect=layout["reset_button"],
            text="Reset",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        self.prev_page_button = pygame_gui.elements.UIButton(
            relative_rect=layout["prev_button"],
            text="Previous",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        self.next_page_button = pygame_gui.elements.UIButton(
            relative_rect=layout["next_button"],
            text="Next",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )

        self.form_scroll = pygame_gui.elements.UIScrollingContainer(
            relative_rect=layout["form_scroll"],
            manager=self.app.ui_manager,
            allow_scroll_x=False,
            allow_scroll_y=True,
        )
        form_container = self.form_scroll.get_container()

        type_options = [item for item in self.app.question_service.get_type_options() if item != "all"]
        difficulty_options = [item for item in self.app.question_service.get_difficulty_options() if item != "all"]
        preview_question = self._read_form_question()
        starting_type = preview_question.type if preview_question.type in type_options else type_options[0]
        starting_difficulty = (
            preview_question.difficulty
            if preview_question.difficulty in difficulty_options
            else difficulty_options[0]
        )

        form_layout = self._get_form_content_layout(layout)

        self._build_form_labels(form_container, form_layout)

        self.id_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=form_layout["id_input"],
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#text_entry",
        )
        self.id_input.set_text(preview_question.id)
        self.type_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=type_options,
            starting_option=starting_type,
            relative_rect=form_layout["type_input"],
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#dropdown",
        )
        self.difficulty_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=difficulty_options,
            starting_option=starting_difficulty,
            relative_rect=form_layout["difficulty_input"],
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#dropdown",
        )
        self.category_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=form_layout["category_input"],
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#text_entry",
        )
        self.category_input.set_text(preview_question.category)
        self.source_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=form_layout["source_input"],
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#text_entry",
        )
        self.source_input.set_text(preview_question.source)

        self.question_box = pygame_gui.elements.UITextEntryBox(
            initial_text=preview_question.question,
            relative_rect=form_layout["question_box"],
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#text_entry",
        )
        self.options_box = pygame_gui.elements.UITextEntryBox(
            initial_text="\n".join(preview_question.options),
            relative_rect=form_layout["options_box"],
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#text_entry",
        )
        self.answer_box = pygame_gui.elements.UITextEntryBox(
            initial_text=preview_question.answer,
            relative_rect=form_layout["answer_box"],
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#text_entry",
        )
        self.explanation_box = pygame_gui.elements.UITextEntryBox(
            initial_text=preview_question.explanation,
            relative_rect=form_layout["explanation_box"],
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#text_entry",
        )

        self.new_button = pygame_gui.elements.UIButton(
            relative_rect=form_layout["new_button"],
            text="New",
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#secondary_button",
        )
        self.save_button = pygame_gui.elements.UIButton(
            relative_rect=form_layout["save_button"],
            text="Save",
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#primary_button",
        )
        self.delete_button = pygame_gui.elements.UIButton(
            relative_rect=form_layout["delete_button"],
            text="Delete",
            manager=self.app.ui_manager,
            container=form_container,
            object_id="#secondary_button",
        )
        self.confirm_delete_button = None
        if self.delete_confirmation_required and self.current_mode == "edit":
            self.confirm_delete_button = pygame_gui.elements.UIButton(
                relative_rect=form_layout["confirm_button"],
                text="Confirm",
                manager=self.app.ui_manager,
                container=form_container,
                object_id="#primary_button",
            )

        self.form_scroll.set_scrollable_area_dimensions(
            (form_layout["content_width"], form_layout["content_height"])
        )

        elements = [
            self.back_button,
            title,
            self.search_input,
            self.type_filter_dropdown,
            self.difficulty_filter_dropdown,
            self.category_filter_dropdown,
            self.apply_button,
            self.reset_filter_button,
            self.prev_page_button,
            self.next_page_button,
            self.form_scroll,
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
        ]
        if self.confirm_delete_button is not None:
            elements.append(self.confirm_delete_button)
        self.ui_elements.extend(elements)

    def _build_form_labels(
        self,
        form_container: pygame_gui.core.interfaces.IContainerLikeInterface,
        form_layout: dict[str, object],
    ) -> None:
        labels = [
            ("Basic Info", form_layout["basic_heading"], "#screen_caption"),
            ("ID", form_layout["id_label"], "#screen_caption"),
            ("Type", form_layout["type_label"], "#screen_caption"),
            ("Difficulty", form_layout["difficulty_label"], "#screen_caption"),
            ("Category", form_layout["category_label"], "#screen_caption"),
            ("Source", form_layout["source_label"], "#screen_caption"),
            ("Question Text", form_layout["question_heading"], "#screen_caption"),
            ("Question", form_layout["question_label"], "#screen_caption"),
            ("Options", form_layout["options_heading"], "#screen_caption"),
            ("Options", form_layout["options_label"], "#screen_caption"),
            ("Answer", form_layout["answer_heading"], "#screen_caption"),
            ("Answer", form_layout["answer_label"], "#screen_caption"),
            ("Explanation", form_layout["explanation_heading"], "#screen_caption"),
            ("Explanation", form_layout["explanation_label"], "#screen_caption"),
            ("Actions", form_layout["actions_heading"], "#screen_caption"),
        ]
        for text, rect, object_id in labels:
            label = pygame_gui.elements.UILabel(
                relative_rect=rect,
                text=text,
                manager=self.app.ui_manager,
                container=form_container,
                object_id=object_id,
            )
            self.ui_elements.append(label)

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
        layout = self._get_layout()

        self._draw_panel(surface, layout["header_rect"], accent=ACCENT)
        self._draw_panel(surface, layout["left_panel"], title="Question List", accent=QUIZ_ACCENT)
        self._draw_panel(surface, layout["center_panel"], title="Edit Form", accent=ANALYTICS_ACCENT)
        self._draw_panel(surface, layout["right_panel"], title="Preview", accent=ALGORITHM_ACCENT)

        title_font = pygame.font.SysFont(UI_FONT_NAME, 18, bold=True)
        body_font = pygame.font.SysFont(UI_FONT_NAME, 16)
        small_font = pygame.font.SysFont(UI_FONT_NAME, 14)

        self._draw_group_heading(surface, "Search and Filters", layout["left_group_heading"], title_font)
        self._draw_group_heading(surface, "Question Preview", layout["preview_group_heading"], title_font)
        self._draw_list_rows(surface, layout)
        self._draw_preview(surface, layout, body_font, small_font)
        self._draw_pagination_footer(surface, layout, small_font)
        self._draw_status_banner(surface, layout["status_rect"], self.status_message, self.status_kind)

    def _draw_group_heading(
        self,
        surface: pygame.Surface,
        text: str,
        position: tuple[int, int],
        font: pygame.font.Font,
    ) -> None:
        surface.blit(font.render(text, True, pygame.Color(TEXT_PRIMARY)), position)

    def _draw_list_rows(self, surface: pygame.Surface, layout: dict[str, object]) -> None:
        self.visible_question_rows.clear()
        list_area: pygame.Rect = layout["list_area"]  # type: ignore[assignment]
        row_height: int = layout["row_height"]  # type: ignore[assignment]
        row_gap: int = layout["row_gap"]  # type: ignore[assignment]
        font_body = pygame.font.SysFont(UI_FONT_NAME, 15, bold=True)
        font_small = pygame.font.SysFont(UI_FONT_NAME, 13)

        if not self.filtered_questions:
            empty_surface = font_body.render(
                "No questions match the current filters.",
                True,
                pygame.Color(TEXT_MUTED),
            )
            surface.blit(empty_surface, (list_area.left, list_area.top + 12))
            return

        start = self.current_page * self.page_size
        end = start + self.page_size
        visible = self.filtered_questions[start:end]

        for index, question in enumerate(visible):
            row_rect = pygame.Rect(
                list_area.left,
                list_area.top + index * (row_height + row_gap),
                list_area.width,
                row_height,
            )
            is_selected = question.id == self.selected_question_id
            bg_color = pygame.Color(CARD_BG_SELECTED) if is_selected else pygame.Color(CARD_MUTED)
            pygame.draw.rect(surface, bg_color, row_rect, border_radius=14)
            pygame.draw.rect(surface, pygame.Color(CARD_BORDER), row_rect, width=1, border_radius=14)

            header_text = f"{question.id}  {question.type.upper()}  {question.category}"
            header_text = self._fit_text(font_body, header_text, row_rect.width - 102)
            surface.blit(
                font_body.render(header_text, True, pygame.Color(TEXT_PRIMARY)),
                (row_rect.left + 14, row_rect.top + 16),
            )

            tag_rect = pygame.Rect(row_rect.right - 74, row_rect.top + 14, 60, 24)
            pygame.draw.rect(surface, self._difficulty_color(question.difficulty), tag_rect, border_radius=12)
            tag_surface = font_small.render(question.difficulty, True, pygame.Color(CHIP_TEXT_DARK))
            surface.blit(tag_surface, tag_surface.get_rect(center=tag_rect.center))

            self.visible_question_rows.append((row_rect, question.id))

    def _draw_pagination_footer(
        self,
        surface: pygame.Surface,
        layout: dict[str, object],
        font: pygame.font.Font,
    ) -> None:
        footer_rect: pygame.Rect = layout["pagination_info_rect"]  # type: ignore[assignment]
        page_count = max(1, (len(self.filtered_questions) + self.page_size - 1) // self.page_size)
        footer = f"Page {self.current_page + 1} / {page_count}   Total {len(self.filtered_questions)}"
        footer_surface = font.render(footer, True, pygame.Color(TEXT_MUTED))
        surface.blit(footer_surface, (footer_rect.left, footer_rect.top))

    def _draw_preview(
        self,
        surface: pygame.Surface,
        layout: dict[str, object],
        font_body: pygame.font.Font,
        font_small: pygame.font.Font,
    ) -> None:
        question = self._read_form_question()

        meta_rect: pygame.Rect = layout["preview_meta"]  # type: ignore[assignment]
        self._draw_panel(surface, meta_rect)

        diff_chip = pygame.Rect(meta_rect.left + 16, meta_rect.top + 18, 82, 26)
        type_chip = pygame.Rect(meta_rect.left + 108, meta_rect.top + 18, 82, 26)
        pygame.draw.rect(surface, self._difficulty_color(question.difficulty), diff_chip, border_radius=13)
        pygame.draw.rect(surface, pygame.Color(CARD_MUTED), type_chip, border_radius=13)
        diff_text = font_small.render(question.difficulty, True, pygame.Color(CHIP_TEXT_DARK))
        type_text = font_small.render(question.type.upper(), True, pygame.Color(TEXT_PRIMARY))
        surface.blit(diff_text, diff_text.get_rect(center=diff_chip.center))
        surface.blit(type_text, type_text.get_rect(center=type_chip.center))

        preview_sections = [
            ("Question", question.question or "--", layout["preview_question"]),
            ("Options", "\n".join(question.options) if question.options else "--", layout["preview_options"]),
            ("Answer", question.answer or "--", layout["preview_answer"]),
            ("Explanation", question.explanation or "--", layout["preview_explanation"]),
        ]

        for heading, content, rect in preview_sections:
            section_rect: pygame.Rect = rect  # type: ignore[assignment]
            self._draw_panel(surface, section_rect)
            surface.blit(
                font_body.render(heading, True, pygame.Color(TEXT_PRIMARY)),
                (section_rect.left + 16, section_rect.top + 14),
            )
            lines = self._wrap_text_to_width(
                font_small,
                content,
                section_rect.width - 32,
                max_lines=max(2, (section_rect.height - 54) // 18),
            )
            for index, line in enumerate(lines):
                surface.blit(
                    font_small.render(line, True, pygame.Color(TEXT_MUTED)),
                    (section_rect.left + 16, section_rect.top + 46 + index * 18),
                )

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
                    self.status_message = (
                        f"Question created. A unique id was generated automatically: {saved_question.id}"
                    )
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

    def _dropdown_value(
        self,
        dropdown: pygame_gui.elements.UIDropDownMenu | None,
        default_value: str,
    ) -> str:
        if dropdown is None:
            return default_value
        selected = dropdown.selected_option
        return selected[0] if isinstance(selected, tuple) else str(selected)

    def _difficulty_color(self, difficulty: str) -> pygame.Color:
        mapping = {
            "easy": pygame.Color(SUCCESS),
            "medium": pygame.Color(QUIZ_ACCENT),
            "hard": pygame.Color(ALGORITHM_ACCENT),
        }
        return mapping.get(difficulty, pygame.Color(ACCENT))

    def _is_admin(self) -> bool:
        return getattr(self.app.current_user, "role", "") == "admin"

    def _get_layout(self) -> dict[str, object]:
        content = self.get_content_rect(32, 18)
        header_rect = pygame.Rect(content.left, content.top, content.width, 92)
        back_button = pygame.Rect(header_rect.left + 18, header_rect.top + 18, 132, 44)
        title_rect = pygame.Rect(header_rect.left + 180, header_rect.top + 16, header_rect.width - 220, 48)

        main_top = header_rect.bottom + 18
        panel_height = content.bottom - main_top - 8
        gap = 22

        left_width = max(300, min(340, int(content.width * 0.24)))
        right_width = max(300, min(330, int(content.width * 0.23)))
        center_width = content.width - left_width - right_width - gap * 2

        left_panel = pygame.Rect(content.left, main_top, left_width, panel_height)
        center_panel = pygame.Rect(left_panel.right + gap, main_top, center_width, panel_height)
        right_panel = pygame.Rect(center_panel.right + gap, main_top, right_width, panel_height)

        left_inner = left_panel.inflate(-32, -32)
        left_group_heading = (left_inner.left, left_panel.top + 76)
        search_input = pygame.Rect(left_inner.left, left_panel.top + 112, left_inner.width, 42)
        filter_gap = 14
        filter_half = (left_inner.width - filter_gap) // 2
        type_filter = pygame.Rect(left_inner.left, search_input.bottom + 14, filter_half, 40)
        difficulty_filter = pygame.Rect(type_filter.right + filter_gap, search_input.bottom + 14, filter_half, 40)
        category_filter = pygame.Rect(left_inner.left, type_filter.bottom + 14, left_inner.width, 40)
        apply_button = pygame.Rect(left_inner.left, category_filter.bottom + 18, filter_half, 40)
        reset_button = pygame.Rect(apply_button.right + filter_gap, category_filter.bottom + 18, filter_half, 40)

        footer_height = 104
        pagination_top = left_panel.bottom - footer_height - 20
        list_area_top = apply_button.bottom + 20
        list_area = pygame.Rect(left_inner.left, list_area_top, left_inner.width, pagination_top - list_area_top)
        row_height = 56
        row_gap = 10
        available_rows = max(1, (list_area.height + row_gap) // (row_height + row_gap))
        self.page_size = max(3, min(4, available_rows))

        prev_button = pygame.Rect(left_inner.left, pagination_top + 12, 120, 38)
        next_button = pygame.Rect(left_inner.right - 120, pagination_top + 12, 120, 38)
        pagination_info_rect = pygame.Rect(left_inner.left, pagination_top + 62, left_inner.width, 18)

        center_inner = center_panel.inflate(-28, -28)
        status_rect = pygame.Rect(center_inner.left, center_panel.bottom - 50, center_inner.width, 34)
        form_scroll = pygame.Rect(
            center_inner.left,
            center_panel.top + 76,
            center_inner.width,
            status_rect.top - (center_panel.top + 76) - 18,
        )

        right_inner = right_panel.inflate(-30, -30)
        preview_group_heading = (right_inner.left, right_panel.top + 76)
        preview_meta = pygame.Rect(right_inner.left, right_panel.top + 112, right_inner.width, 76)
        preview_question = pygame.Rect(right_inner.left, preview_meta.bottom + 16, right_inner.width, 94)
        preview_options = pygame.Rect(right_inner.left, preview_question.bottom + 16, right_inner.width, 86)
        preview_answer = pygame.Rect(right_inner.left, preview_options.bottom + 16, right_inner.width, 68)
        preview_explanation = pygame.Rect(
            right_inner.left,
            preview_answer.bottom + 16,
            right_inner.width,
            right_panel.bottom - (preview_answer.bottom + 16) - 18,
        )

        return {
            "header_rect": header_rect,
            "back_button": back_button,
            "title_rect": title_rect,
            "left_panel": left_panel,
            "center_panel": center_panel,
            "right_panel": right_panel,
            "left_group_heading": left_group_heading,
            "search_input": search_input,
            "type_filter": type_filter,
            "difficulty_filter": difficulty_filter,
            "category_filter": category_filter,
            "apply_button": apply_button,
            "reset_button": reset_button,
            "list_area": list_area,
            "row_height": row_height,
            "row_gap": row_gap,
            "prev_button": prev_button,
            "next_button": next_button,
            "pagination_info_rect": pagination_info_rect,
            "form_scroll": form_scroll,
            "status_rect": status_rect,
            "preview_group_heading": preview_group_heading,
            "preview_meta": preview_meta,
            "preview_question": preview_question,
            "preview_options": preview_options,
            "preview_answer": preview_answer,
            "preview_explanation": preview_explanation,
        }

    def _get_form_content_layout(self, layout: dict[str, object]) -> dict[str, object]:
        scroll_rect: pygame.Rect = layout["form_scroll"]  # type: ignore[assignment]
        content_width = scroll_rect.width - 24
        left = 0
        top = 0
        gap_x = 16
        gap_y = 12
        input_h = 40
        label_h = 22

        third = (content_width - gap_x * 2) // 3
        half = (content_width - gap_x) // 2

        basic_heading = pygame.Rect(left, top, content_width, 26)
        row1_label_y = basic_heading.bottom + 12
        id_label = pygame.Rect(left, row1_label_y, third, label_h)
        type_label = pygame.Rect(left + third + gap_x, row1_label_y, third, label_h)
        difficulty_label = pygame.Rect(left + (third + gap_x) * 2, row1_label_y, content_width - (third + gap_x) * 2, label_h)
        id_input = pygame.Rect(left, id_label.bottom + 6, third, input_h)
        type_input = pygame.Rect(left + third + gap_x, id_input.top, third, input_h)
        difficulty_input = pygame.Rect(left + (third + gap_x) * 2, id_input.top, content_width - (third + gap_x) * 2, input_h)

        row2_label_y = id_input.bottom + gap_y
        category_label = pygame.Rect(left, row2_label_y, half, label_h)
        source_label = pygame.Rect(left + half + gap_x, row2_label_y, content_width - half - gap_x, label_h)
        category_input = pygame.Rect(left, category_label.bottom + 6, half, input_h)
        source_input = pygame.Rect(left + half + gap_x, category_input.top, content_width - half - gap_x, input_h)

        question_heading = pygame.Rect(left, category_input.bottom + 18, content_width, 26)
        question_label = pygame.Rect(left, question_heading.bottom + 10, content_width, label_h)
        question_box = pygame.Rect(left, question_label.bottom + 6, content_width, 132)

        options_heading = pygame.Rect(left, question_box.bottom + 18, content_width, 26)
        options_label = pygame.Rect(left, options_heading.bottom + 10, content_width, label_h)
        options_box = pygame.Rect(left, options_label.bottom + 6, content_width, 156)

        answer_heading = pygame.Rect(left, options_box.bottom + 18, content_width, 26)
        answer_label = pygame.Rect(left, answer_heading.bottom + 10, content_width, label_h)
        answer_box = pygame.Rect(left, answer_label.bottom + 6, content_width, 76)

        explanation_heading = pygame.Rect(left, answer_box.bottom + 18, content_width, 26)
        explanation_label = pygame.Rect(left, explanation_heading.bottom + 10, content_width, label_h)
        explanation_box = pygame.Rect(left, explanation_label.bottom + 6, content_width, 168)

        actions_heading = pygame.Rect(left, explanation_box.bottom + 20, content_width, 26)
        action_y = actions_heading.bottom + 20
        button_gap = 12
        button_width = (content_width - button_gap * 2) // 3
        new_button = pygame.Rect(left, action_y, button_width, 40)
        save_button = pygame.Rect(left + button_width + button_gap, action_y, button_width, 40)
        delete_button = pygame.Rect(left + (button_width + button_gap) * 2, action_y, button_width, 40)
        confirm_button = pygame.Rect(left + (button_width + button_gap) * 2, action_y + 50, button_width, 40)

        content_height = action_y + 40 + 28

        return {
            "content_width": content_width,
            "content_height": content_height,
            "basic_heading": basic_heading,
            "id_label": id_label,
            "type_label": type_label,
            "difficulty_label": difficulty_label,
            "id_input": id_input,
            "type_input": type_input,
            "difficulty_input": difficulty_input,
            "category_label": category_label,
            "source_label": source_label,
            "category_input": category_input,
            "source_input": source_input,
            "question_heading": question_heading,
            "question_label": question_label,
            "question_box": question_box,
            "options_heading": options_heading,
            "options_label": options_label,
            "options_box": options_box,
            "answer_heading": answer_heading,
            "answer_label": answer_label,
            "answer_box": answer_box,
            "explanation_heading": explanation_heading,
            "explanation_label": explanation_label,
            "explanation_box": explanation_box,
            "actions_heading": actions_heading,
            "new_button": new_button,
            "save_button": save_button,
            "delete_button": delete_button,
            "confirm_button": confirm_button,
        }

    def _fit_text(self, font: pygame.font.Font, text: str, max_width: int) -> str:
        plain = (text or "").replace("\n", " ")
        if font.size(plain)[0] <= max_width:
            return plain
        trimmed = plain
        while trimmed and font.size(trimmed + "...")[0] > max_width:
            trimmed = trimmed[:-1]
        return (trimmed.rstrip() + "...") if trimmed else "..."

    def _wrap_text_to_width(
        self,
        font: pygame.font.Font,
        text: str,
        max_width: int,
        max_lines: int = 6,
    ) -> list[str]:
        words = (text or "--").replace("\r", "").split()
        if not words:
            return ["--"]

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
            if len(lines) >= max_lines - 1:
                break

        if current and len(lines) < max_lines:
            lines.append(current)

        consumed = len(" ".join(lines).split())
        if len(lines) == max_lines and consumed < len(words):
            lines[-1] = self._fit_text(font, lines[-1], max_width)

        return lines[:max_lines]
