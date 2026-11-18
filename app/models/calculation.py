
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base


class Calculation(Base):
    """Store calculator operations and their results."""

    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    a: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    b: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    result: Mapped[float] = mapped_column(
        Float, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )
