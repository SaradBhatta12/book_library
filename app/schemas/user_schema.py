

from pydantic import EmailStr, BaseModel, Field
from datetime import datetime

class UserSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True