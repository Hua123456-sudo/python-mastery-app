from __future__ import annotations

from dataclasses import dataclass, field
import random
import time

from src.models.question import Question
from src.services.question_service import QuestionService


@dataclass(slots=True)
class QuizConfig:
    """Quiz configuration."""

    question_count: int
    difficulty: str = "all"
    category: str = "all"


@dataclass(slots=True)
class QuizAnswerRecord:
    """One answered question inside a quiz session."""

    question_id: str
    question_text: str
    question_type: str
    category: str
    difficulty: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    explanation: str


@dataclass(slots=True)
class QuizSubmissionResult:
    """Immediate feedback after submitting an answer."""

    accepted: bool
    is_correct: bool = False
    message: str = ""
    explanation: str = ""
    correct_answer: str = ""
    user_answer: str = ""


@dataclass(slots=True)
class QuizResult:
    """Summary of one completed quiz."""

    score: int
    correct_count: int
    total_questions: int
    accuracy: float
    elapsed_seconds: int
    answers: list[QuizAnswerRecord]
    config: QuizConfig


@dataclass(slots=True)
class QuizSession:
    """Active quiz session."""

    questions: list[Question]
    config: QuizConfig
    current_index: int = 0
    correct_count: int = 0
    answers: list[QuizAnswerRecord] = field(default_factory=list)
    started_at: float = field(default_factory=time.monotonic)
    finished_at: float | None = None
    last_submission: QuizSubmissionResult | None = None

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def current_question(self) -> Question | None:
        if 0 <= self.current_index < self.total_questions:
            return self.questions[self.current_index]
        return None

    @property
    def answered_count(self) -> int:
        return len(self.answers)

    @property
    def progress_ratio(self) -> float:
        if self.total_questions == 0:
            return 0.0
        return self.answered_count / self.total_questions

    @property
    def elapsed_seconds(self) -> int:
        end_time = self.finished_at if self.finished_at is not None else time.monotonic()
        return max(0, int(end_time - self.started_at))

    @property
    def is_complete(self) -> bool:
        return self.current_index >= self.total_questions

    def finish(self) -> None:
        if self.finished_at is None:
            self.finished_at = time.monotonic()


class QuizService:
    """Handles quiz creation, scoring, and results."""

    QUESTION_COUNT_OPTIONS = (10, 20, 30)
    DIFFICULTY_OPTIONS = ("all", "easy", "medium", "hard")

    def __init__(self, question_service: QuestionService) -> None:
        self.question_service = question_service

    def get_category_options(self) -> list[str]:
        categories = sorted({question.category for question in self.question_service.load_questions()})
        return ["all", *categories]

    def create_session(
        self,
        *,
        question_count: int,
        difficulty: str,
        category: str,
    ) -> tuple[QuizSession | None, str]:
        if question_count not in self.QUESTION_COUNT_OPTIONS:
            return None, "Question count must be 10, 20, or 30."
        if difficulty not in self.DIFFICULTY_OPTIONS:
            return None, "Invalid difficulty setting."

        filtered_questions = self.question_service.filter_questions(
            category=None if category == "all" else category,
            difficulty=None if difficulty == "all" else difficulty,
        )
        if not filtered_questions:
            return None, "No questions match the current filters. Please adjust the difficulty or category."

        actual_count = min(question_count, len(filtered_questions))
        sampled_questions = random.sample(filtered_questions, actual_count)
        session = QuizSession(
            questions=sampled_questions,
            config=QuizConfig(
                question_count=actual_count,
                difficulty=difficulty,
                category=category,
            ),
        )

        if actual_count < question_count:
            return session, f"Only {actual_count} questions are available for this filter, so the quiz will start with all available questions."
        return session, f"Quiz started with {actual_count} questions."

    def submit_answer(self, session: QuizSession, raw_answer: str) -> QuizSubmissionResult:
        question = session.current_question
        if question is None:
            return QuizSubmissionResult(accepted=False, message="There is no active question to answer.")
        if session.last_submission is not None:
            return QuizSubmissionResult(accepted=False, message="This question has already been submitted. Please move to the next one.")

        normalized_user_answer = self._normalize_answer(question.type, raw_answer)
        if not normalized_user_answer:
            return QuizSubmissionResult(accepted=False, message="Please enter or select an answer before submitting.")

        normalized_correct_answer = self._normalize_answer(question.type, question.answer)
        is_correct = normalized_user_answer == normalized_correct_answer

        answer_record = QuizAnswerRecord(
            question_id=question.id,
            question_text=question.question,
            question_type=question.type,
            category=question.category,
            difficulty=question.difficulty,
            user_answer=raw_answer.strip(),
            correct_answer=question.answer,
            is_correct=is_correct,
            explanation=question.explanation,
        )
        session.answers.append(answer_record)

        if is_correct:
            session.correct_count += 1

        submission = QuizSubmissionResult(
            accepted=True,
            is_correct=is_correct,
            message="Correct answer." if is_correct else "Incorrect answer.",
            explanation=question.explanation,
            correct_answer=question.answer,
            user_answer=raw_answer.strip(),
        )
        session.last_submission = submission

        if session.answered_count == session.total_questions:
            session.finish()

        return submission

    def advance_to_next_question(self, session: QuizSession) -> bool:
        if session.last_submission is None:
            return True

        session.current_index += 1
        session.last_submission = None

        if session.is_complete:
            session.finish()
            return False
        return True

    def build_result(self, session: QuizSession) -> QuizResult:
        session.finish()
        total_questions = session.total_questions
        correct_count = session.correct_count
        accuracy = (correct_count / total_questions * 100.0) if total_questions else 0.0
        return QuizResult(
            score=correct_count,
            correct_count=correct_count,
            total_questions=total_questions,
            accuracy=accuracy,
            elapsed_seconds=session.elapsed_seconds,
            answers=list(session.answers),
            config=session.config,
        )

    @staticmethod
    def format_duration(seconds: int) -> str:
        minutes, remaining_seconds = divmod(max(0, seconds), 60)
        return f"{minutes:02d}:{remaining_seconds:02d}"

    def _normalize_answer(self, question_type: str, answer: str) -> str:
        normalized = answer.replace("\r\n", "\n").replace("\r", "\n")

        if question_type == "mcq":
            return normalized.strip()
        if question_type == "blank":
            return " ".join(normalized.split()).strip().lower()
        if question_type == "output":
            lines = [line.rstrip() for line in normalized.split("\n")]
            while lines and lines[0] == "":
                lines.pop(0)
            while lines and lines[-1] == "":
                lines.pop()
            return "\n".join(lines).strip()
        return normalized.strip()
