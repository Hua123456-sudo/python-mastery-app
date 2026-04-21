from __future__ import annotations

import hashlib
from pathlib import Path

from src.models.user import User
from src.storage.json_store import JSONStore
from src.utils.safe_data import safe_dict, safe_list


class AuthService:
    """Handles sign-in, registration, and default admin initialization."""

    DEFAULT_ADMIN_USERNAME = "admin"
    DEFAULT_ADMIN_PASSWORD = "admin123"

    def __init__(self, data_dir: str | Path) -> None:
        self.store = JSONStore(
            Path(data_dir) / "users.json",
            {"users": []},
            validator=lambda data: isinstance(data.get("users"), list),
        )
        self._ensure_default_admin()

    def login(self, username: str, password: str) -> tuple[bool, str, User | None]:
        normalized_username = username.strip()
        if not normalized_username:
            return False, "Username cannot be empty.", None
        if not password:
            return False, "Password cannot be empty.", None

        user = self.get_user_by_username(normalized_username)
        if user is None or user.password_hash != self.hash_password(password):
            return False, "Invalid username or password.", None
        return True, f"Login successful. Welcome back, {user.username}.", user

    def register(self, username: str, password: str, role: str = "student") -> tuple[bool, str, User | None]:
        normalized_username = username.strip()
        if not normalized_username:
            return False, "Username cannot be empty.", None
        if self.get_user_by_username(normalized_username) is not None:
            return False, "This username already exists. Please choose another one.", None
        if not password:
            return False, "Password cannot be empty.", None
        if role not in {"student", "admin"}:
            return False, "Invalid user role.", None

        new_user = User(
            username=normalized_username,
            password_hash=self.hash_password(password),
            role=role,
        )
        data = self.store.read()
        users = safe_list(data.get("users"))
        users.append(new_user.to_dict())
        data["users"] = users
        self.store.write(data)
        return True, "Registration successful. Please sign in with the new account.", new_user

    def get_user_by_username(self, username: str) -> User | None:
        normalized_username = username.strip().lower()
        if not normalized_username:
            return None

        data = self.store.read()
        for user_data in safe_list(data.get("users")):
            user = User.from_dict(safe_dict(user_data))
            if not user.username.strip():
                continue
            if user.username.strip().lower() == normalized_username:
                return user
        return None

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _ensure_default_admin(self) -> None:
        if self.get_user_by_username(self.DEFAULT_ADMIN_USERNAME) is not None:
            return

        default_admin = User(
            username=self.DEFAULT_ADMIN_USERNAME,
            password_hash=self.hash_password(self.DEFAULT_ADMIN_PASSWORD),
            role="admin",
        )
        data = self.store.read()
        users = safe_list(data.get("users"))
        users.append(default_admin.to_dict())
        data["users"] = users
        self.store.write(data)
