from __future__ import annotations

from pathlib import Path

import pygame
import pygame_gui

from src.config import APP_TITLE, FPS, THEME_PATH, WINDOW_HEIGHT, WINDOW_WIDTH
from src.router import Router
from src.services.analytics_service import AnalyticsService
from src.services.auth_service import AuthService
from src.services.question_service import QuestionService
from src.services.quiz_history_service import QuizHistoryService
from src.services.quiz_service import QuizService
from src.services.visualization_service import VisualizationService
from src.ui.admin_screen import AdminScreen
from src.ui.algorithm_screen import AlgorithmScreen
from src.ui.analytics_screen import AnalyticsScreen
from src.ui.home_screen import HomeScreen
from src.ui.lesson_screen import LessonScreen
from src.ui.login_screen import LoginScreen
from src.ui.quiz_screen import QuizScreen
from src.ui.result_screen import ResultScreen


class App:
    """应用主控制器。"""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(APP_TITLE)

        self.window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode(self.window_size)
        self.clock = pygame.time.Clock()
        self.is_running = True

        data_dir = Path(__file__).resolve().parent.parent / "data"
        self.auth_service = AuthService(data_dir)
        self.question_service = QuestionService(data_dir)
        self.quiz_service = QuizService(self.question_service)
        self.quiz_history_service = QuizHistoryService(data_dir)
        self.analytics_service = AnalyticsService(self.quiz_history_service)
        self.visualization_service = VisualizationService()

        self.current_user = None
        self.latest_quiz_result = None
        self.latest_quiz_record = None
        self.latest_quiz_save_message = ""
        self.home_notice_message = ""
        self.home_notice_kind = "info"
        self.pending_notice_message = ""
        self.pending_notice_kind = "info"

        self.ui_manager = pygame_gui.UIManager(self.window_size, THEME_PATH)
        self.router = Router(self)
        self._register_screens()
        self.router.navigate("login")

    def _register_screens(self) -> None:
        self.router.register("login", LoginScreen(self))
        self.router.register("home", HomeScreen(self))
        self.router.register("lesson", LessonScreen(self))
        self.router.register("quiz", QuizScreen(self))
        self.router.register("result", ResultScreen(self))
        self.router.register("analytics", AnalyticsScreen(self))
        self.router.register("admin", AdminScreen(self))
        self.router.register("algorithm", AlgorithmScreen(self))

    def run(self) -> None:
        while self.is_running:
            time_delta = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                    continue

                self.ui_manager.process_events(event)
                current_screen = self.router.current_screen
                if current_screen is not None:
                    current_screen.process_event(event)

            current_screen = self.router.current_screen
            if current_screen is not None:
                current_screen.update(time_delta)

            self.ui_manager.update(time_delta)
            self._draw()

        pygame.quit()

    def _draw(self) -> None:
        current_screen = self.router.current_screen
        if current_screen is not None:
            current_screen.draw(self.screen)

        self.ui_manager.draw_ui(self.screen)
        pygame.display.flip()

    def set_current_user(self, user) -> None:
        self.current_user = user

    def logout(self) -> None:
        for screen in self.router.screens.values():
            screen.on_logout()
        self.current_user = None
        self.latest_quiz_result = None
        self.latest_quiz_record = None
        self.latest_quiz_save_message = ""
        self.home_notice_message = ""
        self.home_notice_kind = "info"
        self.pending_notice_message = ""
        self.pending_notice_kind = "info"
        self.router.navigate("login")
