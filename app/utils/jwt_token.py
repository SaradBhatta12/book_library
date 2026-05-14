import datetime
from app.config.config import settings
from jose import JWTError , jwt

SECRET = settings.SECRET_KEY


def encode_token(id:int,email:str):
    now = datetime.datetime.now(datetime.UTC)
    payload = {
        "sub": str(id),
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + datetime.timedelta(days=24)).timestamp())
    }
    encoded_jwt = jwt.encode(payload, SECRET, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token:str):
    try:
        payload = jwt.decode(token,SECRET,algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None