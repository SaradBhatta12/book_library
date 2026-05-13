import datetime
from app.config.config import settings
from jose import JWTError , jwt

SECRET = settings.SECRET_KEY


def encode_token(id:int,email:str):
    payload = {
        "sub":id,
        "email":email,  ## feel like id is too less and its a integer so i added email too 
        "iat":datetime.datetime.now(datetime.UTC),
        "exp":datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=24)
    }
    encoded_jwt = jwt.encode(payload,SECRET,algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token:str):
    try:
        payload = jwt.decode(token,SECRET,algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None