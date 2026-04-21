from __future__ import annotations

import pygame
import pygame_gui

from src.config import ACCENT, CARD_BORDER, SUCCESS, TEXT_FAINT, TEXT_MUTED, TEXT_PRIMARY, UI_FONT_NAME, WARNING
from src.ui.base_screen import BaseScreen


class AlgorithmScreen(BaseScreen):
    """Algorithm visualization page."""

    def __init__(self, app) -> None:
        super().__init__(app, "algorithm")
        self.selected_algorithm_key = "arrays"
        self.session = self.app.visualization_service.create_session(self.selected_algorithm_key)

        self.back_button: pygame_gui.elements.UIButton | None = None
        self.array_button: pygame_gui.elements.UIButton | None = None
        self.list_button: pygame_gui.elements.UIButton | None = None
        self.tree_button: pygame_gui.elements.UIButton | None = None
        self.play_button: pygame_gui.elements.UIButton | None = None
        self.pause_button: pygame_gui.elements.UIButton | None = None
        self.next_button: pygame_gui.elements.UIButton | None = None
        self.reset_button: pygame_gui.elements.UIButton | None = None

    def enter(self) -> None:
        if not self.require_login():
            return
        self.session = self.app.visualization_service.create_session(self.selected_algorithm_key)
        super().enter()

    def rebuild_ui(self) -> None:
        self.clear_ui()
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(178, 118, 124, 44),
            text="Back Home",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )

        self.array_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(190, 256, 150, 46),
            text="Arrays",
            manager=self.app.ui_manager,
            object_id=self._tab_object_id("arrays"),
        )
        self.list_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(190, 314, 150, 46),
            text="Lists",
            manager=self.app.ui_manager,
            object_id=self._tab_object_id("lists"),
        )
        self.tree_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(190, 372, 150, 46),
            text="Trees",
            manager=self.app.ui_manager,
            object_id=self._tab_object_id("trees"),
        )

        self.play_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(930, 546, 70, 42),
            text="Play",
            manager=self.app.ui_manager,
            object_id="#primary_button",
        )
        self.pause_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(1010, 546, 70, 42),
            text="Pause",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        self.next_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(930, 596, 70, 42),
            text="Next",
            manager=self.app.ui_manager,
            object_id="#secondary_button",
        )
        self.reset_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(1010, 596, 70, 42),
            text="Reset",
            manager=self.app.ui_manager,
            object_id="#ghost_button",
        )

        self.ui_elements.extend(
            [
                self.back_button,
                self.array_button,
                self.list_button,
                self.tree_button,
                self.play_button,
                self.pause_button,
                self.next_button,
                self.reset_button,
            ]
        )

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame_gui.UI_BUTTON_PRESSED:
            return
        if event.ui_element == self.back_button:
            self.app.router.navigate("home")
            return
        if event.ui_element == self.array_button:
            self._switch_algorithm("arrays")
            return
        if event.ui_element == self.list_button:
            self._switch_algorithm("lists")
            return
        if event.ui_element == self.tree_button:
            self._switch_algorithm("trees")
            return
        if event.ui_element == self.play_button:
            self.app.visualization_service.play(self.session)
            return
        if event.ui_element == self.pause_button:
            self.app.visualization_service.pause(self.session)
            return
        if event.ui_element == self.next_button:
            self.app.visualization_service.next_step(self.session)
            return
        if event.ui_element == self.reset_button:
            self.app.visualization_service.reset(self.session)

    def update(self, time_delta: float) -> None:
        self.app.visualization_service.update(self.session, time_delta)

    def draw(self, surface: pygame.Surface) -> None:
        super().draw(surface)

        left_panel = pygame.Rect(170, 190, 190, 540)
        center_panel = pygame.Rect(384, 190, 506, 540)
        right_panel = pygame.Rect(912, 190, 180, 540)

        title_font = pygame.font.SysFont(UI_FONT_NAME, 30, bold=True)
        subtitle_font = pygame.font.SysFont(UI_FONT_NAME, 17)
        surface.blit(title_font.render("Algorithm Visualization", True, pygame.Color(TEXT_PRIMARY)), (334, 118))
        surface.blit(subtitle_font.render("Pure pygame visuals for classroom demonstration.", True, pygame.Color(TEXT_MUTED)), (336, 154))

        self._draw_panel(surface, left_panel, title="Algorithms", accent="#1E293B")
        self._draw_panel(surface, center_panel, title=self.session.label, subtitle=self.session.description, accent=ACCENT)
        self._draw_panel(surface, right_panel, title="Control", accent="#A78BFA")

        self._draw_left_sidebar(surface, left_panel)
        self._draw_visualization(surface, center_panel)
        self._draw_right_sidebar(surface, right_panel)

    def _draw_left_sidebar(self, surface: pygame.Surface, panel: pygame.Rect) -> None:
        label_font = pygame.font.SysFont(UI_FONT_NAME, 15)
        hint_font = pygame.font.SysFont(UI_FONT_NAME, 14)
        surface.blit(label_font.render("Select one view", True, pygame.Color(TEXT_MUTED)), (panel.left + 20, panel.top + 84))
        surface.blit(hint_font.render("Buttons only", True, pygame.Color(TEXT_FAINT)), (panel.left + 20, panel.top + 108))

    def _draw_right_sidebar(self, surface: pygame.Surface, panel: pygame.Rect) -> None:
        session = self.session
        step = session.current_step
        state_value = "Playing" if session.is_playing else "Paused"
        step_title = step.title if step is not None else "No Step"
        step_message = step.message if step is not None else "No visualization data is available."

        label_font = pygame.font.SysFont(UI_FONT_NAME, 15, bold=True)
        value_font = pygame.font.SysFont(UI_FONT_NAME, 24, bold=True)
        body_font = pygame.font.SysFont(UI_FONT_NAME, 15)

        surface.blit(label_font.render("Current State", True, pygame.Color(TEXT_MUTED)), (panel.left + 20, panel.top + 84))
        surface.blit(value_font.render(state_value, True, pygame.Color(TEXT_PRIMARY)), (panel.left + 20, panel.top + 108))

        surface.blit(label_font.render("Step Progress", True, pygame.Color(TEXT_MUTED)), (panel.left + 20, panel.top + 158))
        surface.blit(value_font.render(session.progress_text, True, pygame.Color(TEXT_PRIMARY)), (panel.left + 20, panel.top + 182))

        self._draw_progress_bar(
            surface,
            pygame.Rect(panel.left + 20, panel.top + 226, panel.width - 40, 16),
            self._progress_ratio(),
        )

        surface.blit(label_font.render("Current Step", True, pygame.Color(TEXT_MUTED)), (panel.left + 20, panel.top + 274))
        surface.blit(body_font.render(step_title, True, pygame.Color(ACCENT)), (panel.left + 20, panel.top + 300))

        for index, line in enumerate(self._wrap_text(step_message, 19)[:2]):
            line_surface = body_font.render(line, True, pygame.Color(TEXT_MUTED))
            surface.blit(line_surface, (panel.left + 20, panel.top + 332 + index * 20))

    def _draw_visualization(self, surface: pygame.Surface, panel: pygame.Rect) -> None:
        step = self.session.current_step
        if step is None:
            self._draw_empty_state(
                surface,
                panel.inflate(-48, -120),
                "No Data",
                "Reset the session or switch to a different algorithm.",
            )
            return

        if self.session.algorithm_key == "arrays":
            self._draw_array_visualization(surface, panel, step.payload)
        elif self.session.algorithm_key == "lists":
            self._draw_list_visualization(surface, panel, step.payload)
        else:
            self._draw_tree_visualization(surface, panel, step.payload)

    def _draw_array_visualization(self, surface: pygame.Surface, panel: pygame.Rect, payload: dict) -> None:
        array = payload.get("array", [])
        target = payload.get("target")
        current_index = payload.get("current_index")
        checked_indices = set(payload.get("checked_indices", []))
        found_index = payload.get("found_index")

        info_font = pygame.font.SysFont(UI_FONT_NAME, 18, bold=True)
        detail_font = pygame.font.SysFont(UI_FONT_NAME, 15)
        surface.blit(info_font.render(f"Target Value: {target}", True, pygame.Color(TEXT_PRIMARY)), (panel.left + 24, panel.top + 88))
        surface.blit(detail_font.render("Current index is highlighted in blue. Found value turns green.", True, pygame.Color(TEXT_MUTED)), (panel.left + 24, panel.top + 116))

        box_w, box_h, spacing = 62, 62, 14
        total_width = len(array) * box_w + max(0, len(array) - 1) * spacing
        start_x = panel.left + max(24, (panel.width - total_width) // 2)
        y = panel.top + 245
        font_body = pygame.font.SysFont(UI_FONT_NAME, 22, bold=True)
        font_small = pygame.font.SysFont(UI_FONT_NAME, 13)

        for index, value in enumerate(array):
            rect = pygame.Rect(start_x + index * (box_w + spacing), y, box_w, box_h)
            color = pygame.Color("#20304B")
            if index in checked_indices:
                color = pygame.Color("#1E3A5F")
            if index == current_index:
                color = pygame.Color(ACCENT)
            if index == found_index:
                color = pygame.Color(SUCCESS)
            pygame.draw.rect(surface, color, rect, border_radius=16)
            pygame.draw.rect(surface, pygame.Color(CARD_BORDER), rect, width=1, border_radius=16)
            value_color = "#08111F" if index == current_index or index == found_index else TEXT_PRIMARY
            value_surface = font_body.render(str(value), True, pygame.Color(value_color))
            surface.blit(value_surface, value_surface.get_rect(center=rect.center))
            index_surface = font_small.render(str(index), True, pygame.Color(TEXT_MUTED))
            surface.blit(index_surface, index_surface.get_rect(center=(rect.centerx, rect.bottom + 14)))

    def _draw_list_visualization(self, surface: pygame.Surface, panel: pygame.Rect, payload: dict) -> None:
        nodes = payload.get("nodes", [])
        arrows = payload.get("arrows", [])
        highlight_indices = set(payload.get("highlight_indices", []))
        floating_node = payload.get("floating_node")

        info_font = pygame.font.SysFont(UI_FONT_NAME, 18, bold=True)
        detail_font = pygame.font.SysFont(UI_FONT_NAME, 15)
        surface.blit(info_font.render("Linked List Insertion", True, pygame.Color(TEXT_PRIMARY)), (panel.left + 24, panel.top + 88))
        surface.blit(detail_font.render("Highlighted nodes show the active reconnection step.", True, pygame.Color(TEXT_MUTED)), (panel.left + 24, panel.top + 116))

        node_w, node_h, spacing = 76, 50, 36
        total_width = len(nodes) * node_w + max(0, len(nodes) - 1) * spacing
        start_x = panel.left + max(24, (panel.width - total_width) // 2)
        y = panel.top + 270
        centers: list[tuple[int, int]] = []
        font_body = pygame.font.SysFont(UI_FONT_NAME, 21, bold=True)
        font_small = pygame.font.SysFont(UI_FONT_NAME, 15)

        for index, value in enumerate(nodes):
            rect = pygame.Rect(start_x + index * (node_w + spacing), y, node_w, node_h)
            color = pygame.Color(ACCENT if index in highlight_indices else "#20304B")
            if index in highlight_indices and index == len(nodes) - 1 and len(highlight_indices) > 1:
                color = pygame.Color(SUCCESS)
            pygame.draw.rect(surface, color, rect, border_radius=15)
            pygame.draw.rect(surface, pygame.Color(CARD_BORDER), rect, width=1, border_radius=15)
            value_color = "#08111F" if index in highlight_indices else TEXT_PRIMARY
            value_surface = font_body.render(str(value), True, pygame.Color(value_color))
            surface.blit(value_surface, value_surface.get_rect(center=rect.center))
            centers.append(rect.center)

        for start_index, end_index in arrows:
            if start_index >= len(centers) or end_index >= len(centers):
                continue
            start = (centers[start_index][0] + node_w // 2 - 10, centers[start_index][1])
            end = (centers[end_index][0] - node_w // 2 + 10, centers[end_index][1])
            pygame.draw.line(surface, pygame.Color(TEXT_MUTED), start, end, 3)
            pygame.draw.polygon(surface, pygame.Color(TEXT_MUTED), [(end[0], end[1]), (end[0] - 10, end[1] - 6), (end[0] - 10, end[1] + 6)])

        if floating_node is not None:
            floating_rect = pygame.Rect(panel.centerx - 38, panel.top + 176, node_w, node_h)
            pygame.draw.rect(surface, pygame.Color(WARNING), floating_rect, border_radius=15)
            pygame.draw.rect(surface, pygame.Color(CARD_BORDER), floating_rect, width=1, border_radius=15)
            value_surface = font_body.render(str(floating_node.get("value", "?")), True, pygame.Color("#08111F"))
            surface.blit(value_surface, value_surface.get_rect(center=floating_rect.center))
            note_surface = font_small.render("New node", True, pygame.Color(TEXT_MUTED))
            surface.blit(note_surface, note_surface.get_rect(center=(floating_rect.centerx, floating_rect.bottom + 18)))

    def _draw_tree_visualization(self, surface: pygame.Surface, panel: pygame.Rect, payload: dict) -> None:
        nodes = payload.get("nodes", {})
        visited = set(payload.get("visited", []))
        current_node = payload.get("current_node")
        order_values = payload.get("order_values", [])

        info_font = pygame.font.SysFont(UI_FONT_NAME, 18, bold=True)
        detail_font = pygame.font.SysFont(UI_FONT_NAME, 15)
        surface.blit(info_font.render("Inorder Traversal", True, pygame.Color(TEXT_PRIMARY)), (panel.left + 24, panel.top + 88))
        surface.blit(detail_font.render("Blue marks the active node. Green marks visited nodes.", True, pygame.Color(TEXT_MUTED)), (panel.left + 24, panel.top + 116))

        positions = {
            "A": (panel.centerx, panel.top + 170),
            "B": (panel.centerx - 110, panel.top + 265),
            "C": (panel.centerx + 110, panel.top + 265),
            "D": (panel.centerx - 170, panel.top + 360),
            "E": (panel.centerx - 50, panel.top + 360),
            "F": (panel.centerx + 170, panel.top + 360),
        }

        for key, node in nodes.items():
            parent = positions.get(key)
            if parent is None:
                continue
            for child_key in (node.get("left"), node.get("right")):
                if child_key is None or child_key not in positions:
                    continue
                pygame.draw.line(surface, pygame.Color(CARD_BORDER), parent, positions[child_key], 3)

        font_body = pygame.font.SysFont(UI_FONT_NAME, 20, bold=True)
        font_small = pygame.font.SysFont(UI_FONT_NAME, 15)
        for key, node in nodes.items():
            center = positions.get(key)
            if center is None:
                continue
            color = pygame.Color("#20304B")
            if key in visited:
                color = pygame.Color(SUCCESS)
            if key == current_node:
                color = pygame.Color(ACCENT)
            pygame.draw.circle(surface, color, center, 28)
            pygame.draw.circle(surface, pygame.Color(CARD_BORDER), center, 28, 2)
            text_color = "#08111F" if key in visited or key == current_node else TEXT_PRIMARY
            value_surface = font_body.render(str(node.get("value", "")), True, pygame.Color(text_color))
            surface.blit(value_surface, value_surface.get_rect(center=center))

        order_text = " -> ".join(str(value) for value in order_values) if order_values else "--"
        order_surface = font_small.render(f"Visited Order: {order_text}", True, pygame.Color(TEXT_MUTED))
        surface.blit(order_surface, (panel.left + 24, panel.bottom - 38))

    def _progress_ratio(self) -> float:
        if not self.session.steps:
            return 0.0
        return (self.session.current_step_index + 1) / len(self.session.steps)

    def _switch_algorithm(self, algorithm_key: str) -> None:
        self.selected_algorithm_key = algorithm_key
        self.session = self.app.visualization_service.create_session(algorithm_key)
        self.rebuild_ui()

    def _tab_object_id(self, algorithm_key: str) -> str:
        return "#primary_button" if self.selected_algorithm_key == algorithm_key else "#secondary_button"

    def on_logout(self) -> None:
        self.selected_algorithm_key = "arrays"
        self.session = self.app.visualization_service.create_session(self.selected_algorithm_key)
