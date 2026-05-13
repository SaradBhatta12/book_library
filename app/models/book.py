from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from app.database.database import Base, TimestampMixin
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.category import Category
    from app.models.author import Author



class Book(Base , TimestampMixin):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    published_year: Mapped[int] = mapped_column(nullable=True)  
    notes: Mapped[str] = mapped_column(nullable=True)

    #  for relationship
    owner: Mapped["User"] = relationship(back_populates="books")
    category: Mapped["Category"] = relationship(back_populates="books")
    author: Mapped["Author"] = relationship(back_populates="books")