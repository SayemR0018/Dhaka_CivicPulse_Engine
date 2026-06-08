import os
from datetime import datetime, timedelta, timezone
from math import factorial

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

app = FastAPI()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-secret-key-for-local-testing")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash([BcryptHasher()])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "demo": {
        "username": "demo",
        "hashed_password": "$2b$12$AlFRIQaTnBtZdcHNOdRFr.8276Fb67Dk7/fGf4lSTx7P6SIF97bn.",
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str) -> dict | None:
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expires_at})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return user

@app.get("/")
def home() -> dict:
    return {"message": "Hello from Codex demo"}

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/add")
def add(a: int, b: int, current_user: dict = Depends(get_current_user)) -> dict:
    return {"result": a + b}

@app.get("/multiply")
def multiply(a: int, b: int, current_user: dict = Depends(get_current_user)) -> dict:
    return {"result": a * b}

@app.get("/power")
def power(a: int, b: int, current_user: dict = Depends(get_current_user)) -> dict:
    return {"result": a ** b}

@app.get("/factorial")
def calculate_factorial(n: int, current_user: dict = Depends(get_current_user)) -> dict:
    if n < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="n must be non-negative",
        )
    return {"result": factorial(n)}
