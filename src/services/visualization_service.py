from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class VisualizationStep:
    """Single visualization step."""

    title: str
    message: str
    payload: dict[str, Any]


@dataclass(slots=True)
class VisualizationSession:
    """State container for one visualization run."""

    algorithm_key: str
    label: str
    description: str
    steps: list[VisualizationStep]
    current_step_index: int = 0
    is_playing: bool = False
    step_interval: float = 1.0
    accumulated_time: float = 0.0

    @property
    def current_step(self) -> VisualizationStep | None:
        if not self.steps:
            return None
        index = min(max(self.current_step_index, 0), len(self.steps) - 1)
        return self.steps[index]

    @property
    def progress_text(self) -> str:
        if not self.steps:
            return "0 / 0"
        index = min(max(self.current_step_index, 0), len(self.steps) - 1)
        return f"{index + 1} / {len(self.steps)}"


class VisualizationService:
    """Builds visualization steps and manages playback state."""

    def __init__(self) -> None:
        self._definitions = self._build_definitions()

    def get_algorithm_options(self) -> list[tuple[str, str]]:
        return [(key, value["label"]) for key, value in self._definitions.items()]

    def create_session(self, algorithm_key: str) -> VisualizationSession:
        definition = self._definitions.get(algorithm_key)
        if definition is None:
            return VisualizationSession(
                algorithm_key="invalid",
                label="Unavailable Demo",
                description="The selected visualization is not available.",
                steps=[],
            )

        return VisualizationSession(
            algorithm_key=algorithm_key,
            label=definition["label"],
            description=definition["description"],
            steps=deepcopy(definition["steps"]),
            step_interval=max(0.2, float(definition.get("step_interval", 1.0))),
        )

    def play(self, session: VisualizationSession) -> None:
        self._sanitize_session(session)
        if session.steps:
            session.is_playing = True

    def pause(self, session: VisualizationSession) -> None:
        self._sanitize_session(session)
        session.is_playing = False

    def reset(self, session: VisualizationSession) -> None:
        self._sanitize_session(session)
        session.current_step_index = 0
        session.accumulated_time = 0.0
        session.is_playing = False

    def next_step(self, session: VisualizationSession) -> bool:
        self._sanitize_session(session)
        if not session.steps:
            return False

        if session.current_step_index < len(session.steps) - 1:
            session.current_step_index += 1
            session.accumulated_time = 0.0
            return True

        session.current_step_index = len(session.steps) - 1
        session.is_playing = False
        return False

    def update(self, session: VisualizationSession, time_delta: float) -> bool:
        self._sanitize_session(session)
        if not session.is_playing or not session.steps or time_delta <= 0:
            return False

        session.accumulated_time += time_delta
        if session.accumulated_time < session.step_interval:
            return False

        session.accumulated_time = 0.0
        return self.next_step(session)

    def _sanitize_session(self, session: VisualizationSession) -> None:
        if not session.steps:
            session.current_step_index = 0
            session.is_playing = False
            session.accumulated_time = 0.0
            return
        session.current_step_index = min(max(session.current_step_index, 0), len(session.steps) - 1)
        if session.step_interval <= 0:
            session.step_interval = 1.0
        if session.accumulated_time < 0:
            session.accumulated_time = 0.0

    def _build_definitions(self) -> dict[str, dict[str, Any]]:
        return {
            "arrays": {
                "label": "Arrays",
                "description": "Linear Search",
                "step_interval": 0.9,
                "steps": self._build_array_steps(),
            },
            "lists": {
                "label": "Lists",
                "description": "Linked List Insertion",
                "step_interval": 1.0,
                "steps": self._build_list_steps(),
            },
            "trees": {
                "label": "Trees",
                "description": "Inorder Traversal",
                "step_interval": 0.95,
                "steps": self._build_tree_steps(),
            },
        }

    def _build_array_steps(self) -> list[VisualizationStep]:
        array = [12, 7, 19, 4, 11, 23]
        target = 11
        steps = [
            VisualizationStep(
                title="Initialize Search",
                message="Prepare the array and start scanning from left to right for target 11.",
                payload={"array": array, "target": target, "current_index": None, "checked_indices": [], "found_index": None},
            )
        ]

        checked: list[int] = []
        found_index: int | None = None
        for index, value in enumerate(array):
            steps.append(
                VisualizationStep(
                    title=f"Check Index {index}",
                    message=f"Compare value {value} at index {index} with target 11.",
                    payload={
                        "array": array,
                        "target": target,
                        "current_index": index,
                        "checked_indices": checked.copy(),
                        "found_index": None,
                    },
                )
            )
            checked.append(index)
            if value == target:
                found_index = index
                steps.append(
                    VisualizationStep(
                        title="Target Found",
                        message=f"Value 11 is found at index {index}. Linear search stops here.",
                        payload={
                            "array": array,
                            "target": target,
                            "current_index": index,
                            "checked_indices": checked.copy(),
                            "found_index": found_index,
                        },
                    )
                )
                break

        if found_index is None:
            steps.append(
                VisualizationStep(
                    title="Search Complete",
                    message="The target value does not exist in this array.",
                    payload={"array": array, "target": target, "current_index": None, "checked_indices": checked.copy(), "found_index": None},
                )
            )
        return steps

    def _build_list_steps(self) -> list[VisualizationStep]:
        base_nodes = [10, 20, 40]
        insert_value = 30
        insert_after_index = 1
        return [
            VisualizationStep(
                title="Original List",
                message="The current list is 10 -> 20 -> 40 before insertion begins.",
                payload={"nodes": base_nodes, "insert_value": insert_value, "insert_after_index": insert_after_index, "highlight_indices": [], "floating_node": None, "arrows": [(0, 1), (1, 2)]},
            ),
            VisualizationStep(
                title="Locate Position",
                message="Node 20 is the previous node. The new node will be inserted after it.",
                payload={"nodes": base_nodes, "insert_value": insert_value, "insert_after_index": insert_after_index, "highlight_indices": [1], "floating_node": None, "arrows": [(0, 1), (1, 2)]},
            ),
            VisualizationStep(
                title="Create New Node",
                message="Create a new node with value 30 and hold it above the list.",
                payload={"nodes": base_nodes, "insert_value": insert_value, "insert_after_index": insert_after_index, "highlight_indices": [1], "floating_node": {"value": insert_value, "position": (0, -1)}, "arrows": [(0, 1), (1, 2)]},
            ),
            VisualizationStep(
                title="Reconnect Links",
                message="Point the new node to 40, then connect node 20 to the new node.",
                payload={"nodes": [10, 20, 30, 40], "insert_value": insert_value, "insert_after_index": insert_after_index, "highlight_indices": [1, 2], "floating_node": None, "arrows": [(0, 1), (1, 2), (2, 3)]},
            ),
            VisualizationStep(
                title="Insertion Complete",
                message="The new list is now 10 -> 20 -> 30 -> 40.",
                payload={"nodes": [10, 20, 30, 40], "insert_value": insert_value, "insert_after_index": insert_after_index, "highlight_indices": [2], "floating_node": None, "arrows": [(0, 1), (1, 2), (2, 3)]},
            ),
        ]

    def _build_tree_steps(self) -> list[VisualizationStep]:
        nodes = {
            "A": {"value": 8, "left": "B", "right": "C"},
            "B": {"value": 3, "left": "D", "right": "E"},
            "C": {"value": 10, "left": None, "right": "F"},
            "D": {"value": 1, "left": None, "right": None},
            "E": {"value": 6, "left": None, "right": None},
            "F": {"value": 14, "left": None, "right": None},
        }
        traversal_order = ["D", "B", "E", "A", "C", "F"]
        visited: list[str] = []
        steps = [
            VisualizationStep(
                title="Traversal Ready",
                message="Inorder traversal visits left subtree, root node, then right subtree.",
                payload={"nodes": nodes, "visited": [], "current_node": None, "order_values": []},
            )
        ]
        explanations = {
            "D": "Move to the leftmost node first and visit node 1.",
            "B": "Return to node 3 after its left subtree is finished.",
            "E": "Visit the right child of node 3, which is node 6.",
            "A": "The full left subtree is complete, so visit root node 8.",
            "C": "Enter the right subtree and visit node 10 first.",
            "F": "Visit node 14 and finish the inorder traversal.",
        }

        for node_key in traversal_order:
            visited.append(node_key)
            steps.append(
                VisualizationStep(
                    title=f"Visit Node {nodes[node_key]['value']}",
                    message=explanations[node_key],
                    payload={
                        "nodes": nodes,
                        "visited": visited.copy(),
                        "current_node": node_key,
                        "order_values": [nodes[key]["value"] for key in visited],
                    },
                )
            )
        return steps
