

from pydantic import EmailStr
from pydantic import BaseModel
class UserSchema(BaseModel):
    email: EmailStr
    password: str