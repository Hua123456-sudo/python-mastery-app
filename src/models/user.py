from __future__ import annotations

from dataclasses import asdict, dataclass

from src.utils.safe_data import safe_dict, safe_str


@dataclass(slots=True)
class User:
    """应用中的用户对象。"""

    username: str
    password_hash: str
    role: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "User":
        safe_data = safe_dict(data)
        return cls(
            username=safe_str(safe_data.get("username")),
            password_hash=safe_str(safe_data.get("password_hash")),
            role=safe_str(safe_data.get("role"), "student"),
        )
