from __future__ import annotations

import pygame
import pygame_gui

from src.config import ACCENT, UI_FONT_NAME
from src.ui.base_screen import BaseScreen


class LoginScreen(BaseScreen):
    """Login and registration screen."""

    def __init__(self, app) -> None:
        super().__init__(app, "login")
        self.mode = "login"
        self.username_input: pygame_gui.elements.UITextEntryLine | None = None
        self.password_input: pygame_gui.elements.UITextEntryLine | None = None
        self.login_mode_button: pygame_gui.elements.UIButton | None = None
        self.register_mode_button: pygame_gui.elements.UIButton | None = None
        self.submit_button: pygame_gui.elements.UIButton | None = None
        self.role_drop_down: pygame_gui.elements.UIDropDownMenu | None = None
        self.status_label: pygame_gui.elements.UILabel | None = None
        self.status_message = "Default admin account: admin / admin123"
        self.status_kind = "info"

    def enter(self) -> None:
        if self.app.pending_notice_message:
            self.status_message = self.app.pending_notice_message
            self.status_kind = self.app.pending_notice_kind
            self.app.pending_notice_message = ""
            self.app.pending_notice_kind = "info"
        super().enter()

    def rebuild_ui(self) -> None:
        self.clear_ui()
        center_x = self.app.window_size[0] // 2

        title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(center_x - 240, 138, 480, 50),
            text="Welcome to Python Mastery",
            manager=self.app.ui_manager,
            object_id="#screen_title",
        )
        subtitle = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(center_x - 420, 194, 840, 34),
            text="Sign in or create an account to access quizzes, analytics, admin tools, and algorithm demos.",
            manager=self.app.ui_manager,
            object_id="#screen_subtitle",
        )
        self.login_mode_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - 198, 286, 190, 48),
            text="Login Mode",
            manager=self.app.ui_manager,
            object_id=self._button_object_id("login"),
        )
        self.register_mode_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x + 8, 286, 190, 48),
            text="Register Mode",
            manager=self.app.ui_manager,
            object_id=self._button_object_id("register"),
        )
        self.username_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(center_x - 198, 384, 396, 52),
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.username_input.set_text_length_limit(24)

        self.password_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(center_x - 198, 462, 396, 52),
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.password_input.set_text_hidden(True)
        self.password_input.set_text_length_limit(32)

        self.role_drop_down = pygame_gui.elements.UIDropDownMenu(
            options_list=["student", "admin"],
            starting_option="student",
            relative_rect=pygame.Rect(center_x - 198, 540, 396, 48),
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.submit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(center_x - 198, 612, 396, 56),
            text=self._submit_text(),
            manager=self.app.ui_manager,
            object_id="#primary_button",
        )
        self.status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(center_x - 270, 684, 540, 30),
            text=self.status_message,
            manager=self.app.ui_manager,
            object_id=self._status_object_id(),
        )

        self.ui_elements.extend(
            [
                title,
                subtitle,
                self.login_mode_button,
                self.register_mode_button,
                self.username_input,
                self.password_input,
                self.role_drop_down,
                self.submit_button,
                self.status_label,
            ]
        )
        self._sync_mode_ui()

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return

        if event.ui_element == self.login_mode_button:
            self.mode = "login"
            self.status_message = "Default admin account: admin / admin123"
            self.status_kind = "info"
            self.rebuild_ui()
            return
        if event.ui_element == self.register_mode_button:
            self.mode = "register"
            self.status_message = "Choose a role when registering. For normal class use, student is recommended."
            self.status_kind = "info"
            self.rebuild_ui()
            return
        if event.ui_element == self.submit_button:
            self._handle_submit()

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)

        card = pygame.Rect(336, 248, 608, 486)
        side_panel = pygame.Rect(962, 248, 138, 486)
        self._draw_panel(
            surface,
            card,
            title="Unified Access",
            subtitle="This screen keeps the login and registration flow in one place with a clean card layout.",
            accent=ACCENT,
        )
        self._draw_panel(surface, side_panel, title="Mode", accent="#1E293B")

        label_font = pygame.font.SysFont(UI_FONT_NAME, 18, bold=True)
        body_font = pygame.font.SysFont(UI_FONT_NAME, 15)
        surface.blit(label_font.render("Username", True, pygame.Color("#E2E8F0")), (404, 350))
        surface.blit(label_font.render("Password", True, pygame.Color("#E2E8F0")), (404, 428))

        if self.mode == "register":
            surface.blit(label_font.render("Role", True, pygame.Color("#E2E8F0")), (404, 506))
            hint = "student is for learning and quizzes; admin keeps access to question management."
        else:
            hint = "You can sign in immediately with the default admin account for demonstration."

        for index, line in enumerate(self._wrap_text(hint, 16)[:6]):
            surface.blit(
                body_font.render(line, True, pygame.Color("#94A3B8")),
                (side_panel.left + 16, side_panel.top + 86 + index * 22),
            )

        self._draw_status_banner(
            surface,
            pygame.Rect(384, 548 if self.mode == "login" else 618, 420, 38),
            self.status_message,
            self.status_kind,
        )

    def _handle_submit(self) -> None:
        username = self.username_input.get_text() if self.username_input is not None else ""
        password = self.password_input.get_text() if self.password_input is not None else ""

        if self.mode == "login":
            success, message, user = self.app.auth_service.login(username, password)
            self._set_status(message, "success" if success else "error")
            if success and user is not None:
                self.app.set_current_user(user)
                self.app.router.navigate("home")
            return

        role = self.role_drop_down.selected_option[0] if self.role_drop_down is not None else "student"
        success, message, _ = self.app.auth_service.register(username, password, role)
        self._set_status(message, "success" if success else "error")
        if success:
            if self.password_input is not None:
                self.password_input.set_text("")
            self.mode = "login"
            self.status_message = message
            self.status_kind = "success"
            self.rebuild_ui()

    def _set_status(self, message: str, kind: str) -> None:
        self.status_message = message
        self.status_kind = kind
        if self.status_label is not None:
            self.status_label.set_text(message)
            self.status_label.change_object_id(self._status_object_id())

    def _sync_mode_ui(self) -> None:
        if self.role_drop_down is None or self.submit_button is None:
            return
        if self.mode == "login":
            self.role_drop_down.hide()
        else:
            self.role_drop_down.show()
        self.submit_button.set_text(self._submit_text())
        if self.status_label is not None:
            self.status_label.set_text(self.status_message)
            self.status_label.change_object_id(self._status_object_id())

    def _submit_text(self) -> str:
        return "Sign In" if self.mode == "login" else "Create Account"

    def _button_object_id(self, button_mode: str) -> str:
        return "#primary_button" if self.mode == button_mode else "#secondary_button"

    def _status_object_id(self) -> str:
        if self.status_kind == "success":
            return "#status_success"
        if self.status_kind == "error":
            return "#status_error"
        return "#status_info"
