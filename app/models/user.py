from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.author import Author
    from app.models.category import Category

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    #  for relationship
    books: Mapped[List["Book"]] = relationship(back_populates="owner")
    authors: Mapped[List["Author"]] = relationship(back_populates="owner")
    categories: Mapped[List["Category"]] = relationship(back_populates="owner")