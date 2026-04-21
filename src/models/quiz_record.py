from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from src.utils.safe_data import safe_dict, safe_float, safe_int, safe_list, safe_str


@dataclass(slots=True)
class WrongQuestionRecord:
    """答错题目记录。"""

    question_id: str
    user_answer: str
    correct_answer: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WrongQuestionRecord":
        safe_data = safe_dict(data)
        return cls(
            question_id=safe_str(safe_data.get("question_id")),
            user_answer=safe_str(safe_data.get("user_answer")),
            correct_answer=safe_str(safe_data.get("correct_answer")),
        )


@dataclass(slots=True)
class QuestionResultRecord:
    """单题结果摘要，用于后续统计分析。"""

    question_id: str
    category: str
    difficulty: str
    is_correct: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuestionResultRecord":
        safe_data = safe_dict(data)
        return cls(
            question_id=safe_str(safe_data.get("question_id")),
            category=safe_str(safe_data.get("category"), "unknown"),
            difficulty=safe_str(safe_data.get("difficulty"), "unknown"),
            is_correct=bool(safe_data.get("is_correct", False)),
        )


@dataclass(slots=True)
class QuizRecord:
    """持久化保存的一次测验记录。"""

    record_id: str
    username: str
    quiz_date: str
    score: int
    correct_count: int
    total_questions: int
    accuracy: float
    time_spent: int
    difficulty: str
    category: str
    wrong_questions: list[WrongQuestionRecord] = field(default_factory=list)
    question_results: list[QuestionResultRecord] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "username": self.username,
            "quiz_date": self.quiz_date,
            "score": self.score,
            "correct_count": self.correct_count,
            "total_questions": self.total_questions,
            "accuracy": self.accuracy,
            "time_spent": self.time_spent,
            "difficulty": self.difficulty,
            "category": self.category,
            "wrong_questions": [item.to_dict() for item in self.wrong_questions],
            "question_results": [item.to_dict() for item in self.question_results],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QuizRecord":
        safe_data = safe_dict(data)
        return cls(
            record_id=safe_str(safe_data.get("record_id")),
            username=safe_str(safe_data.get("username")),
            quiz_date=safe_str(safe_data.get("quiz_date")),
            score=safe_int(safe_data.get("score")),
            correct_count=safe_int(safe_data.get("correct_count")),
            total_questions=max(0, safe_int(safe_data.get("total_questions"))),
            accuracy=safe_float(safe_data.get("accuracy")),
            time_spent=max(0, safe_int(safe_data.get("time_spent"))),
            difficulty=safe_str(safe_data.get("difficulty"), "all"),
            category=safe_str(safe_data.get("category"), "all"),
            wrong_questions=[
                WrongQuestionRecord.from_dict(item)
                for item in safe_list(safe_data.get("wrong_questions"))
            ],
            question_results=[
                QuestionResultRecord.from_dict(item)
                for item in safe_list(safe_data.get("question_results"))
            ],
        )
