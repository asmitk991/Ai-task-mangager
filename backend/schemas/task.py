from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"pending", "in_progress", "done"}


def normalize_required_string(value, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be empty.")
    return cleaned


def normalize_optional_string(value, field_name: str):
    if value is None:
        return value
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")
    cleaned = value.strip()
    return cleaned or None


def normalize_priority(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Priority must be a string.")
    normalized = value.strip().lower()
    if normalized not in VALID_PRIORITIES:
        raise ValueError(f"Priority must be one of: {', '.join(sorted(VALID_PRIORITIES))}.")
    return normalized


def normalize_status(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Status must be a string.")
    normalized = value.strip().lower()
    if normalized not in VALID_STATUSES:
        raise ValueError(f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}.")
    return normalized


class ParsedTaskSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    deadline: Optional[date] = None
    priority: str = Field(default="medium")
    category: str = Field(default="general", min_length=1, max_length=100)
    status: str = Field(default="pending")

    @field_validator("title", "category", mode="before")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        return normalize_required_string(value, "Value")

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value):
        return normalize_optional_string(value, "Description")

    @field_validator("priority", mode="before")
    @classmethod
    def validate_priority(cls, value: str) -> str:
        return normalize_priority(value)

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: str) -> str:
        return normalize_status(value)


class ParseTaskRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=5000)

    @field_validator("text", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        cleaned = normalize_required_string(value, "Input text")
        if len(cleaned) < 3:
            raise ValueError("Input text must contain at least 3 characters.")
        return cleaned


class ParseTaskResponse(BaseModel):
    tasks: List[ParsedTaskSchema]


class CreateTaskRequest(ParsedTaskSchema):
    raw_input: Optional[str] = Field(default=None, max_length=5000)


class CreateTasksBatchRequest(BaseModel):
    tasks: List[CreateTaskRequest] = Field(..., min_length=1)


class UpdateTaskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    deadline: Optional[date] = None
    priority: Optional[str] = None
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    status: Optional[str] = None
    raw_input: Optional[str] = Field(default=None, max_length=5000)

    @field_validator("title", "category", mode="before")
    @classmethod
    def strip_optional_text(cls, value):
        if value is None:
            return value
        return normalize_required_string(value, "Value")

    @field_validator("description", "raw_input", mode="before")
    @classmethod
    def strip_optional_long_text(cls, value):
        return normalize_optional_string(value, "Value")

    @field_validator("priority", mode="before")
    @classmethod
    def validate_optional_priority(cls, value):
        if value is None:
            return value
        return normalize_priority(value)

    @field_validator("status", mode="before")
    @classmethod
    def validate_optional_status(cls, value):
        if value is None:
            return value
        return normalize_status(value)


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    deadline: Optional[date]
    priority: str
    category: str
    status: str
    raw_input: Optional[str]


class TasksResponse(BaseModel):
    tasks: List[TaskResponse]
