from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CrawledProfile(Base):
    __tablename__ = "crawled_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    external_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    embedded_data: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
