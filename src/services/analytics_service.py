from __future__ import annotations

from dataclasses import dataclass

from src.models.quiz_record import QuizRecord
from src.services.quiz_history_service import QuizHistoryService


@dataclass(slots=True)
class TrendPoint:
    label: str
    score: float
    accuracy: float


@dataclass(slots=True)
class CategoryAccuracy:
    category: str
    correct: int
    total: int
    accuracy: float


@dataclass(slots=True)
class DifficultyDistribution:
    difficulty: str
    count: int


@dataclass(slots=True)
class AnalyticsSummary:
    average_score: float
    best_score: int
    total_quizzes: int
    last_result: QuizRecord | None
    records: list[QuizRecord]
    trend_points: list[TrendPoint]
    category_accuracy: list[CategoryAccuracy]
    difficulty_distribution: list[DifficultyDistribution]


class AnalyticsService:
    """Builds summary statistics for a user's quiz history."""

    def __init__(self, quiz_history_service: QuizHistoryService) -> None:
        self.quiz_history_service = quiz_history_service

    def build_user_summary(self, username: str) -> AnalyticsSummary:
        records = self.quiz_history_service.get_records_for_user(username)
        if not records:
            return AnalyticsSummary(0.0, 0, 0, None, [], [], [], [])

        average_score = sum(max(0, record.score) for record in records) / len(records)
        best_score = max(max(0, record.score) for record in records)
        last_result = records[-1]

        return AnalyticsSummary(
            average_score=average_score,
            best_score=best_score,
            total_quizzes=len(records),
            last_result=last_result,
            records=list(reversed(records)),
            trend_points=self._build_trend_points(records),
            category_accuracy=self._build_category_accuracy(records),
            difficulty_distribution=self._build_difficulty_distribution(records),
        )

    def _build_trend_points(self, records: list[QuizRecord]) -> list[TrendPoint]:
        return [
            TrendPoint(
                label=f"{index + 1}",
                score=max(0, record.score),
                accuracy=max(0.0, min(100.0, record.accuracy)),
            )
            for index, record in enumerate(records)
        ]

    def _build_category_accuracy(self, records: list[QuizRecord]) -> list[CategoryAccuracy]:
        bucket: dict[str, dict[str, int]] = {}
        for record in records:
            if record.question_results:
                for item in record.question_results:
                    category = item.category or "Unknown Category"
                    bucket.setdefault(category, {"correct": 0, "total": 0})
                    bucket[category]["total"] += 1
                    if item.is_correct:
                        bucket[category]["correct"] += 1
                continue

            category = record.category if record.category != "all" else "Mixed"
            bucket.setdefault(category, {"correct": 0, "total": 0})
            bucket[category]["correct"] += max(0, record.correct_count)
            bucket[category]["total"] += max(record.total_questions, 0)

        results: list[CategoryAccuracy] = []
        for category, values in bucket.items():
            total = max(0, values["total"])
            correct = max(0, values["correct"])
            accuracy = (correct / total * 100.0) if total else 0.0
            results.append(CategoryAccuracy(category=category, correct=correct, total=total, accuracy=accuracy))
        return sorted(results, key=lambda item: item.accuracy, reverse=True)

    def _build_difficulty_distribution(self, records: list[QuizRecord]) -> list[DifficultyDistribution]:
        counts: dict[str, int] = {"easy": 0, "medium": 0, "hard": 0, "all": 0}
        for record in records:
            if record.question_results:
                for item in record.question_results:
                    difficulty = item.difficulty if item.difficulty in counts else "all"
                    counts[difficulty] += 1
                continue

            difficulty = record.difficulty if record.difficulty in counts else "all"
            counts[difficulty] += max(record.total_questions, 1)

        return [DifficultyDistribution(difficulty=key, count=value) for key, value in counts.items() if value > 0]
