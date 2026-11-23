from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class SchoolModel(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    abbreviation: Mapped[str] = mapped_column(String(50))
    address: Mapped[str] = mapped_column(Text)
