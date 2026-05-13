from bcrypt import checkpw
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.utils.response_handler import response
from app.schemas.user_schema import UserSchema
from app.models.user import User
from app.utils.jwt_token import encode_token
from bcrypt import hashpw, gensalt

router = APIRouter()
security = HTTPBearer()

@router.post("/register")
async def create_user(user_data:UserSchema,db:Session = Depends(get_db)):
    if not user_data.email or not user_data.password:
        return response(success=False,status_code=400,message="Please provide email and password")
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        return response(success=False,status_code=400,message="User already exists")
    
    # HASH THE PASSWORD (Industry Standard)
    hashed_password = hashpw(user_data.password.encode(), gensalt()).decode()
    
    new_user = User(
        email=user_data.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)    
    return response(success=True,status_code=201,message="User created successfully",data={
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "created_at": new_user.created_at
        }
    })


@router.post("/login")
async def login_user(user_data:UserSchema,db:Session = Depends(get_db)):
    """
    Login user and generate JWT token
    """

    if not user_data.email or not user_data.password:
        return response(success=False,status_code=400,message="Please provide email and password")
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if not existing_user:
        return response(success=False,status_code=404,message="User not exist. Please register first.")

    if not checkpw(user_data.password.encode(), existing_user.password.encode()):
        return response(success=False,status_code=400,message="Invalid password")
    
    token = encode_token(existing_user.id, existing_user.email)
    return response(success=True,status_code=200,message="Login successful",data={
        "user": {
            "id": existing_user.id,
            "email": existing_user.email,
        },
        "token":token
        })



@router.get("/protected", dependencies=[Depends(security)])
async def protected_route(auth: HTTPAuthorizationCredentials = Depends(security)):
    return response(success=True,status_code=200,message="Protected route accessed successfully")
        