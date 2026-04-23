from __future__ import annotations

import pygame
import pygame_gui

from src.ui.base_screen import BaseScreen
from src.ui.theme import (
    ACCENT,
    TEXT_PRIMARY,
    UI_FONT_NAME,
)


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
        layout = self._get_layout()

        self.login_mode_button = pygame_gui.elements.UIButton(
            relative_rect=layout["login_button_rect"],
            text="Login Mode",
            manager=self.app.ui_manager,
            object_id=self._button_object_id("login"),
        )
        self.register_mode_button = pygame_gui.elements.UIButton(
            relative_rect=layout["register_button_rect"],
            text="Register Mode",
            manager=self.app.ui_manager,
            object_id=self._button_object_id("register"),
        )

        self.username_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=layout["username_input_rect"],
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.username_input.set_text_length_limit(24)

        self.password_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=layout["password_input_rect"],
            manager=self.app.ui_manager,
            object_id="#text_entry",
        )
        self.password_input.set_text_hidden(True)
        self.password_input.set_text_length_limit(32)

        self.role_drop_down = pygame_gui.elements.UIDropDownMenu(
            options_list=["student", "admin"],
            starting_option="student",
            relative_rect=layout["role_input_rect"],
            manager=self.app.ui_manager,
            object_id="#dropdown",
        )
        self.submit_button = pygame_gui.elements.UIButton(
            relative_rect=layout["submit_button_rect"],
            text=self._submit_text(),
            manager=self.app.ui_manager,
            object_id="#primary_button",
        )

        self.ui_elements.extend(
            [
                self.login_mode_button,
                self.register_mode_button,
                self.username_input,
                self.password_input,
                self.role_drop_down,
                self.submit_button,
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
            self.status_message = "Create a new account and choose a role."
            self.status_kind = "info"
            self.rebuild_ui()
            return
        if event.ui_element == self.submit_button:
            self._handle_submit()

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_login_background(surface)
        layout = self._get_layout()
        card_rect = layout["card_rect"]

        title_font = pygame.font.SysFont(UI_FONT_NAME, 42, bold=True)
        subtitle_font = pygame.font.SysFont(UI_FONT_NAME, 20)
        self._draw_login_card(surface, card_rect)
        title_surface = title_font.render("Python Mastery", True, pygame.Color("#24364F"))
        subtitle_surface = subtitle_font.render("Sign in or create an account to continue.", True, pygame.Color("#5C6F86"))
        surface.blit(title_surface, title_surface.get_rect(center=layout["title_center"]))
        surface.blit(subtitle_surface, subtitle_surface.get_rect(center=layout["subtitle_center"]))

        label_font = pygame.font.SysFont(UI_FONT_NAME, 18, bold=True)
        label_color = pygame.Color("#24364F")
        surface.blit(label_font.render("Username", True, label_color), layout["username_label_pos"])
        surface.blit(label_font.render("Password", True, label_color), layout["password_label_pos"])
        if self.mode == "register":
            surface.blit(label_font.render("Role", True, label_color), layout["role_label_pos"])

        self._draw_status_banner(surface, layout["status_rect"], self.status_message, self.status_kind)

    def _draw_login_background(self, surface: pygame.Surface) -> None:
        width, height = surface.get_size()
        top = pygame.Color("#DCEBFA")
        bottom = pygame.Color("#EEF4FB")

        for y in range(height):
            blend = y / max(height - 1, 1)
            color = (
                int(top.r + (bottom.r - top.r) * blend),
                int(top.g + (bottom.g - top.g) * blend),
                int(top.b + (bottom.b - top.b) * blend),
            )
            pygame.draw.line(surface, color, (0, y), (width, y))

        circles = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.circle(circles, (120, 170, 230, 42), (190, 150), 170)
        pygame.draw.circle(circles, (150, 190, 240, 34), (width - 150, 130), 210)
        pygame.draw.circle(circles, (200, 220, 246, 38), (width // 2, height - 60), 220)
        surface.blit(circles, (0, 0))

    def _draw_login_card(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        shadow = pygame.Surface((rect.width + 10, rect.height + 12), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (79, 105, 138, 18), shadow.get_rect(), border_radius=28)
        surface.blit(shadow, (rect.left - 5, rect.top + 8))

        pygame.draw.rect(surface, pygame.Color("#F4F8FD"), rect, border_radius=26)
        pygame.draw.rect(surface, pygame.Color("#C7D9EB"), rect, width=1, border_radius=26)
        inner = rect.inflate(-18, -18)
        pygame.draw.rect(surface, (255, 255, 255, 120), inner, width=1, border_radius=22)

        accent_rect = pygame.Rect(rect.left + 36, rect.top + 26, 92, 6)
        pygame.draw.rect(surface, pygame.Color(ACCENT), accent_rect, border_radius=8)

    def _get_layout(self) -> dict[str, pygame.Rect | tuple[int, int] | int]:
        content_rect = self.get_content_rect(52, 26)
        card_width = max(500, min(620, int(content_rect.width * 0.52)))
        card_left = content_rect.centerx - card_width // 2
        card_top = content_rect.top + 138
        field_left = card_left + 40
        field_width = card_width - 80
        mode_gap = 12
        mode_width = (field_width - mode_gap) // 2

        mode_row_y = card_top + 36
        current_y = mode_row_y + 46 + 26

        username_label_y = current_y
        username_input_y = username_label_y + 30
        current_y = username_input_y + 48 + 22

        password_label_y = current_y
        password_input_y = password_label_y + 30
        current_y = password_input_y + 48 + 22

        role_label_y = current_y
        role_input_y = role_label_y + 30
        if self.mode == "register":
            current_y = role_input_y + 46 + 22

        submit_button_y = current_y
        status_y = submit_button_y + 52 + 18
        status_height = 40
        card_height = (status_y - card_top) + status_height + 32
        card_rect = pygame.Rect(card_left, card_top, card_width, card_height)

        field_left = card_rect.left + 40
        field_width = card_rect.width - 80
        status_rect = pygame.Rect(field_left, status_y, field_width, status_height)

        return {
            "title_center": (content_rect.centerx, content_rect.top + 30),
            "subtitle_center": (content_rect.centerx, content_rect.top + 76),
            "card_rect": card_rect,
            "field_left": field_left,
            "login_button_rect": pygame.Rect(field_left, card_rect.top + 36, mode_width, 46),
            "register_button_rect": pygame.Rect(field_left + mode_width + mode_gap, card_rect.top + 36, mode_width, 46),
            "username_label_pos": (field_left, username_label_y),
            "username_input_rect": pygame.Rect(field_left, username_input_y, field_width, 48),
            "password_label_pos": (field_left, password_label_y),
            "password_input_rect": pygame.Rect(field_left, password_input_y, field_width, 48),
            "role_label_pos": (field_left, role_label_y),
            "role_input_rect": pygame.Rect(field_left, role_input_y, field_width, 46),
            "submit_button_rect": pygame.Rect(field_left, submit_button_y, field_width, 52),
            "status_rect": status_rect,
        }

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

    def _sync_mode_ui(self) -> None:
        if self.role_drop_down is None or self.submit_button is None:
            return
        if self.mode == "login":
            self.role_drop_down.hide()
        else:
            self.role_drop_down.show()
        self.submit_button.set_text(self._submit_text())

    def _submit_text(self) -> str:
        return "Sign In" if self.mode == "login" else "Create Account"

    def _button_object_id(self, button_mode: str) -> str:
        return "#primary_button" if self.mode == button_mode else "#secondary_button"
