from bcrypt import checkpw
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.utils.response_handler import response
from app.schemas.user_schema import UserSchema, UserResponse
from app.models.user import User
from app.utils.jwt_token import encode_token
from app.utils.jwt_guard import get_current_user
from bcrypt import hashpw, gensalt
from app.utils.limiter import limiter

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserSchema, db: Session = Depends(get_db)):
    """
    Register a new user with email and password.
    - **email**: Must be unique
    - **password**: Must be at least 8 characters
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        return response(success=False, status_code=400, message="User already exists")
    
    # HASH THE PASSWORD (Industry Standard)
    hashed_password = hashpw(user_data.password.encode(), gensalt()).decode()
    
    new_user = User(
        email=user_data.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)    
    return response(success=True, status_code=201, message="User created successfully", data={
        "user": UserResponse.from_orm(new_user)
    })


@router.post("/login")
@limiter.limit("5/minute")
async def login_user(
    request: Request,
    user_data: UserSchema, db: Session = Depends(get_db)):
    """
    Authenticate user and return a JWT access token.
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if not existing_user:
        return response(success=False, status_code=404, message="User not exist. Please register first.")

    if not checkpw(user_data.password.encode(), existing_user.password.encode()):
        return response(success=False, status_code=400, message="Invalid password")
    
    token = encode_token(existing_user.id, existing_user.email)
    return response(success=True, status_code=200, message="Login successful", data={
        "user": UserResponse.from_orm(existing_user),
        "token": token
    })


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the current logged-in user profile.
    """
    return response(success=True, status_code=200, message="User profile fetched", data={
        "user": UserResponse.from_orm(current_user)
    })
        