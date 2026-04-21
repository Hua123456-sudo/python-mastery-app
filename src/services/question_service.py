from __future__ import annotations

import json
import random
from pathlib import Path

from src.models.question import QUESTION_TYPES, Question
from src.storage.json_store import JSONStore
from src.utils.safe_data import safe_dict, safe_list, safe_str


def _load_seed_questions() -> list[dict[str, object]]:
    project_root = Path(__file__).resolve().parents[2]
    candidate_paths = [
        project_root / "data" / "questions_seed.json",
        project_root / "data" / "questions.json",
    ]
    for seed_path in candidate_paths:
        try:
            raw_text = seed_path.read_text(encoding="utf-8").strip()
            if not raw_text:
                continue
            data = json.loads(raw_text)
            questions = safe_list(safe_dict(data).get("questions"))
            if questions:
                return questions
        except (FileNotFoundError, OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
            continue
    return []


DEFAULT_QUESTIONS = _load_seed_questions()


class QuestionService:
    """Handles question loading, filtering, and management."""

    DIFFICULTY_OPTIONS = ("easy", "medium", "hard")

    def __init__(self, data_dir: str | Path) -> None:
        self.store = JSONStore(
            Path(data_dir) / "questions.json",
            {"questions": DEFAULT_QUESTIONS},
            validator=lambda data: isinstance(data.get("questions"), list),
        )
        self._ensure_seed_questions()

    def load_questions(self) -> list[Question]:
        data = self.store.read()
        questions: list[Question] = []
        for item in safe_list(data.get("questions")):
            question = Question.from_dict(safe_dict(item))
            if question.is_valid():
                questions.append(question)
        return sorted(questions, key=lambda question: question.id)

    def save_questions(self, questions: list[Question]) -> None:
        valid_questions = [question.to_dict() for question in questions if question.is_valid()]
        self.store.write({"questions": valid_questions})

    def get_question_by_id(self, question_id: str) -> Question | None:
        normalized_id = question_id.strip()
        for question in self.load_questions():
            if question.id == normalized_id:
                return question
        return None

    def filter_questions(
        self,
        *,
        question_type: str | None = None,
        category: str | None = None,
        difficulty: str | None = None,
    ) -> list[Question]:
        questions = self.load_questions()
        if question_type is not None:
            questions = [question for question in questions if question.type == question_type]
        if category is not None:
            questions = [question for question in questions if question.category == category]
        if difficulty is not None:
            questions = [question for question in questions if question.difficulty == difficulty]
        return questions

    def search_questions(
        self,
        *,
        keyword: str = "",
        question_type: str = "all",
        difficulty: str = "all",
        category: str = "all",
    ) -> list[Question]:
        filtered = self.filter_questions(
            question_type=None if question_type == "all" else question_type,
            difficulty=None if difficulty == "all" else difficulty,
            category=None if category == "all" else category,
        )

        normalized_keyword = keyword.strip().lower()
        if not normalized_keyword:
            return filtered

        return [
            question
            for question in filtered
            if normalized_keyword in question.id.lower()
            or normalized_keyword in question.question.lower()
            or normalized_keyword in question.category.lower()
            or normalized_keyword in question.source.lower()
            or normalized_keyword in question.answer.lower()
        ]

    def get_random_questions(
        self,
        count: int = 5,
        *,
        question_type: str | None = None,
        category: str | None = None,
        difficulty: str | None = None,
    ) -> list[Question]:
        filtered_questions = self.filter_questions(
            question_type=question_type,
            category=category,
            difficulty=difficulty,
        )
        if not filtered_questions:
            return []
        sample_size = min(max(count, 0), len(filtered_questions))
        return random.sample(filtered_questions, sample_size)

    def add_question(self, question: Question) -> Question:
        normalized_question = self._normalize_question(question)
        final_id = normalized_question.id
        if not final_id or self.get_question_by_id(final_id) is not None:
            final_id = self.generate_unique_id()
            normalized_question = Question(
                id=final_id,
                type=normalized_question.type,
                category=normalized_question.category,
                difficulty=normalized_question.difficulty,
                question=normalized_question.question,
                options=normalized_question.options,
                answer=normalized_question.answer,
                explanation=normalized_question.explanation,
                source=normalized_question.source,
            )

        questions = self.load_questions()
        questions.append(normalized_question)
        self.save_questions(questions)
        return normalized_question

    def update_question(self, original_id: str, updated_question: Question) -> Question:
        normalized_original_id = original_id.strip()
        normalized_question = self._normalize_question(updated_question)
        if not normalized_question.id:
            normalized_question = Question(
                id=normalized_original_id,
                type=normalized_question.type,
                category=normalized_question.category,
                difficulty=normalized_question.difficulty,
                question=normalized_question.question,
                options=normalized_question.options,
                answer=normalized_question.answer,
                explanation=normalized_question.explanation,
                source=normalized_question.source,
            )

        questions = self.load_questions()
        for index, question in enumerate(questions):
            if question.id != normalized_original_id:
                continue

            duplicate = self.get_question_by_id(normalized_question.id)
            if duplicate is not None and duplicate.id != normalized_original_id:
                raise ValueError(f"Question id '{normalized_question.id}' already exists. Please use a different id.")

            questions[index] = normalized_question
            self.save_questions(questions)
            return normalized_question

        raise ValueError(f"No question with id '{normalized_original_id}' was found.")

    def delete_question(self, question_id: str) -> None:
        normalized_id = question_id.strip()
        questions = [question for question in self.load_questions() if question.id != normalized_id]
        self.save_questions(questions)

    def generate_unique_id(self) -> str:
        max_number = 0
        for question in self.load_questions():
            digits = "".join(char for char in question.id if char.isdigit())
            if digits:
                max_number = max(max_number, int(digits))
        return f"q{max_number + 1:03d}"

    def get_type_options(self) -> list[str]:
        return ["all", *sorted(QUESTION_TYPES)]

    def get_difficulty_options(self) -> list[str]:
        return ["all", *list(self.DIFFICULTY_OPTIONS)]

    def get_category_options(self) -> list[str]:
        categories = sorted({question.category for question in self.load_questions() if question.category.strip()})
        return ["all", *categories]

    def _normalize_question(self, question: Question) -> Question:
        normalized_id = question.id.strip()
        normalized_type = question.type.strip()
        normalized_category = question.category.strip()
        normalized_difficulty = question.difficulty.strip()
        normalized_text = question.question.strip()
        normalized_options = [option.strip() for option in question.options if safe_str(option).strip()]
        normalized_answer = question.answer.strip()
        normalized_explanation = question.explanation.strip() or "No explanation provided."
        normalized_source = question.source.strip() or "admin"

        if normalized_type not in QUESTION_TYPES:
            raise ValueError("Question type must be mcq, blank, or output.")
        if normalized_difficulty not in self.DIFFICULTY_OPTIONS:
            raise ValueError("Difficulty must be easy, medium, or hard.")
        if not normalized_category:
            raise ValueError("Category cannot be empty.")
        if not normalized_text:
            raise ValueError("Question text cannot be empty.")
        if not normalized_answer:
            raise ValueError("Answer cannot be empty.")
        if normalized_type == "mcq":
            if len(normalized_options) < 2:
                raise ValueError("MCQ questions need at least two options.")
            if normalized_answer not in normalized_options:
                raise ValueError("The MCQ answer must exactly match one of the options.")
        else:
            normalized_options = []

        return Question(
            id=normalized_id,
            type=normalized_type,
            category=normalized_category,
            difficulty=normalized_difficulty,
            question=normalized_text,
            options=normalized_options,
            answer=normalized_answer,
            explanation=normalized_explanation,
            source=normalized_source,
        )

    def _ensure_seed_questions(self) -> None:
        if self.load_questions():
            return
        if DEFAULT_QUESTIONS:
            self.store.write({"questions": DEFAULT_QUESTIONS})
