from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    name: str
    title: str | None = None
    source: str | None = None
    source_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    role: str | None = None
    introduction: str | None = None
    tech_stack: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    raw_text: str | None = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str | None = None
    title: str | None = None
    source: str | None = None
    source_url: str | None = None
    tags: list[str] | None = None
    role: str | None = None
    introduction: str | None = None
    tech_stack: list[str] | None = None
    interests: list[str] | None = None
    raw_text: str | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
