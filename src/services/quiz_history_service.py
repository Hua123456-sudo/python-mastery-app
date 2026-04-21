from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from src.models.quiz_record import QuestionResultRecord, QuizRecord, WrongQuestionRecord
from src.services.quiz_service import QuizResult
from src.storage.json_store import JSONStore
from src.utils.safe_data import safe_dict, safe_list


class QuizHistoryService:
    """Handles quiz history loading, filtering, and persistence."""

    def __init__(self, data_dir: str | Path) -> None:
        self.store = JSONStore(
            Path(data_dir) / "quiz_history.json",
            {"records": []},
            validator=lambda data: isinstance(data.get("records"), list),
        )

    def load_records(self) -> list[QuizRecord]:
        data = self.store.read()
        records: list[QuizRecord] = []
        for item in safe_list(data.get("records")):
            record = QuizRecord.from_dict(safe_dict(item))
            if record.record_id.strip() and record.username.strip():
                records.append(record)
        return records

    def get_records_for_user(self, username: str) -> list[QuizRecord]:
        normalized_username = username.strip().lower()
        if not normalized_username:
            return []

        records = [
            record
            for record in self.load_records()
            if record.username.strip().lower() == normalized_username
        ]
        return sorted(records, key=lambda item: item.quiz_date)

    def save_result(self, user, result: QuizResult) -> tuple[bool, str, QuizRecord | None]:
        if user is None or not getattr(user, "username", "").strip():
            return False, "The current user session is invalid, so the quiz result was not saved.", None

        record = QuizRecord(
            record_id=self._generate_record_id(),
            username=user.username,
            quiz_date=datetime.now().isoformat(timespec="seconds"),
            score=max(0, result.score),
            correct_count=max(0, result.correct_count),
            total_questions=max(0, result.total_questions),
            accuracy=round(max(0.0, result.accuracy), 2),
            time_spent=max(0, result.elapsed_seconds),
            difficulty=result.config.difficulty,
            category=result.config.category,
            wrong_questions=[
                WrongQuestionRecord(
                    question_id=answer.question_id,
                    user_answer=answer.user_answer,
                    correct_answer=answer.correct_answer,
                )
                for answer in result.answers
                if not answer.is_correct
            ],
            question_results=[
                QuestionResultRecord(
                    question_id=answer.question_id,
                    category=answer.category,
                    difficulty=answer.difficulty,
                    is_correct=answer.is_correct,
                )
                for answer in result.answers
            ],
        )

        data = self.store.read()
        records = safe_list(data.get("records"))
        records.append(record.to_dict())
        data["records"] = records
        self.store.write(data)
        return True, "This quiz result was saved successfully.", record

    def _generate_record_id(self) -> str:
        existing_ids = {record.record_id for record in self.load_records() if record.record_id.strip()}
        while True:
            candidate = f"qr_{uuid4().hex[:12]}"
            if candidate not in existing_ids:
                return candidate
