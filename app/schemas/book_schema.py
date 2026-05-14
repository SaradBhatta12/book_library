from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.category_schema import CategorySchema
from app.schemas.author_schema import AuthorSchema

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=50)
    author_id: int
    category_id: int
    published_year: Optional[int] = None
    notes: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=50)
    author_id: Optional[int] = None
    category_id: Optional[int] = None
    published_year: Optional[int] = None
    notes: Optional[str] = None

class BookSchema(BookBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    # Nested schemas for better API responses
    author: Optional[AuthorSchema] = None
    category: Optional[CategorySchema] = None

    class Config:
        from_attributes = True
