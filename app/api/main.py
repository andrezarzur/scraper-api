from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import mysql.connector
from app.db.database import get_db_connection
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError


SECRET_KEY = 'i3RuRpJG:&9-gn.Kp=5:bz#NPSAm#z'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class User(BaseModel):
    name: str
    password: str
    email: str
    created_at: datetime or None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str or None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@app.get('/')
def root():
    return {"hello": "world"}


@app.get('/user/{user_id}', response_model=User)
def get_user(username: str) -> User:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True, buffered=True)
            cursor.execute(
                "SELECT name, email, created_at, password FROM users WHERE name = %s",
                (username,)
            )
            user = cursor.fetchone()
            cursor.close()
            if user:
                return user
            else:
                raise HTTPException(status_code=404, detail="User not found")
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")


@app.post('/user')
def create_user(user: User):
    try:
        hashed_password = pwd_context.hash(user.password)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, password, email, created_at) VALUES (%s, %s, %s, %s)",
                (user.name, hashed_password, user.email, datetime.now())
            )
            conn.commit()  # Commit changes to the database
            return {"message": "User created successfully!"}
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")


@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],) -> Token:
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['name']}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


# @app.post('/items')
# def create_item(item: Item):
#     items.append(item)
#     return items
#
#
# @app.get('/items', response_model=list[Item])
# def list_items(limit: int = 10):
#     return items[0:limit]
#
#
# @app.get('/items/{item_id}', response_model=Item)
# def get_item(item_id: int) -> Item:
#     if item_id >= len(items):
#         raise HTTPException(status_code=404, detail="Item not found")
#     item = items[item_id]
#     return item
