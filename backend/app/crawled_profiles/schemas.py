from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CrawledProfileBase(BaseModel):
    source: str
    external_key: str | None = None
    source_url: str | None = None
    title: str
    raw_text: str
    parsed_json: dict[str, Any] | None = None
    embedded_data: list[float] | None = None


class CrawledProfileCreate(CrawledProfileBase):
    pass


class CrawledProfileImportItem(BaseModel):
    title: str | None = None
    name: str | None = None
    tags: list[str] = Field(default_factory=list)
    raw_text: str
    source: str = "json-import"
    source_url: str | None = None
    external_key: str | None = None
    parsed_json: dict[str, Any] | None = None


class CrawledProfileRead(CrawledProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class CrawledProfileListResponse(BaseModel):
    crawled_profiles: list[CrawledProfileRead]
    page: int
    size: int
    total: int
    has_next: bool


class CrawledProfileImportResult(BaseModel):
    imported_count: int
    skipped_count: int


class CrawledProfileConvertToUsersResult(BaseModel):
    converted_count: int
    skipped_count: int
