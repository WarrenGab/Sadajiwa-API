from jose import JWTError, jwt
from fastapi import (FastAPI, Depends, HTTPException, status)
from passlib.context import CryptContext
from models import *

SECRET_KEY = "47d5c0eb62865599b9364d51551a6a98f65485ecf8828c8265f30c51ff890f69"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(username: str, password: str):
    user = await User.get(username = username)

    if user  and verify_password(password, user.password):
        return user

    return False

async def token_generator(username: str, password: str):
    user = await authenticate_user(username, password)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {
        "id" : user.id,
        "username" : user.username
    }

    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token
