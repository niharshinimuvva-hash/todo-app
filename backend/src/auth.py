from datetime import datetime, timedelta
from jose import JWTError, jwt

from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status

from fastapi.security import OAuth2PasswordBearer


# -----------------------------
# Configuration
# -----------------------------

SECRET_KEY = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# -----------------------------
# Password Hashing
# -----------------------------

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str):

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
):

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# -----------------------------
# JWT Creation
# -----------------------------

def create_access_token(data: dict):

    payload = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update(
        {
            "exp": expire
        }
    )

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return token


# -----------------------------
# OAuth2
# -----------------------------

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/login"
)


# -----------------------------
# Decode JWT
# -----------------------------

def decode_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return payload

    except JWTError:

        return None


# -----------------------------
# Current User Dependency
# -----------------------------

async def get_current_user(
    token: str = Depends(oauth2_scheme),
):

    payload = decode_access_token(token)

    if payload is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    email = payload.get("sub")

    if email is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    return email