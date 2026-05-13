from datetime import datetime
from typing import List, TYPE_CHECKING
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from app.database.database import Base

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.user import User

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    #  for relationship
    books: Mapped[List["Book"]] = relationship(back_populates="category")
    owner: Mapped["User"] = relationship(back_populates="categories")
