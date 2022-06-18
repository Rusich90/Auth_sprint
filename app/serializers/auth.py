import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, validator


class UserBody(BaseModel):
    id: UUID
    login: str


class LoginBody(BaseModel):
    login: str
    password: str


class RegisterBody(LoginBody):
    @validator("password")
    def password_validate(cls, value):
        if not re.match(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
            value,
        ):
            raise ValueError(
                "Password must contains Minimum eight characters,"
                " at least one uppercase letter,"
                " one lowercase letter, one number and one special character"
            )
        return value


class ErrorBody(BaseModel):
    error: str


class OkBody(BaseModel):
    result: str


class TokenBody(BaseModel):
    access_token: str
    refresh_token: str


class RefreshBody(BaseModel):
    refresh_token: str


class HistoryBody(BaseModel):
    user_agent: str
    auth_date: datetime
