from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Draft(Base):
    __tablename__ = "drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    job_description: Mapped[str] = mapped_column(Text)
    candidate_profile: Mapped[str] = mapped_column(Text)
    backend_used: Mapped[str] = mapped_column(String(50))
    resume_text: Mapped[str] = mapped_column(Text)
    cover_letter_text: Mapped[str] = mapped_column(Text)
    infographic_svg: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
