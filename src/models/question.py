from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from src.utils.safe_data import safe_dict, safe_list, safe_str


QUESTION_TYPES = {"mcq", "blank", "output"}


@dataclass(slots=True)
class Question:
    """题目数据模型。"""

    id: str
    type: str
    category: str
    difficulty: str
    question: str
    options: list[str] = field(default_factory=list)
    answer: str = ""
    explanation: str = ""
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Question":
        safe_data = safe_dict(data)
        return cls(
            id=safe_str(safe_data.get("id")),
            type=safe_str(safe_data.get("type")),
            category=safe_str(safe_data.get("category")),
            difficulty=safe_str(safe_data.get("difficulty")),
            question=safe_str(safe_data.get("question")),
            options=[safe_str(item) for item in safe_list(safe_data.get("options"))],
            answer=safe_str(safe_data.get("answer")),
            explanation=safe_str(safe_data.get("explanation")),
            source=safe_str(safe_data.get("source")),
        )

    def is_valid(self) -> bool:
        return (
            bool(self.id.strip())
            and self.type in QUESTION_TYPES
            and bool(self.category.strip())
            and bool(self.difficulty.strip())
            and bool(self.question.strip())
            and bool(self.answer.strip())
        )
