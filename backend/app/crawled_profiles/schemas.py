from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CrawledProfileBase(BaseModel):
    source: str
    external_key: str | None = None
    title: str
    raw_text: str
    parsed_json: dict[str, Any] | None = None


class CrawledProfileCreate(CrawledProfileBase):
    pass


class CrawledProfileRead(CrawledProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class CrawledProfileImportResult(BaseModel):
    imported_count: int
