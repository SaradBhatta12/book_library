from pydantic import BaseModel, Field
from typing import Optional

class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    bio: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    bio: Optional[str] = None

class AuthorSchema(AuthorBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
