
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app import App
    from src.ui.base_screen import BaseScreen


class Router:
    """Handles screen registration and navigation."""

    def __init__(self, app: "App") -> None:
        self.app = app
        self.screens: dict[str, "BaseScreen"] = {}
        self.current_screen: "BaseScreen | None" = None

    def register(self, name: str, screen: "BaseScreen") -> None:
        self.screens[name] = screen

    def navigate(self, name: str) -> None:
        if name not in self.screens:
            raise ValueError(f"Screen '{name}' is not registered.")

        if self.current_screen is not None:
            self.current_screen.exit()

        self.current_screen = self.screens[name]
        self.current_screen.enter()
