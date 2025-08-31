from datetime import datetime, timedelta, timezone
from typing import Union
from starlette.middleware.cors import CORSMiddleware 
import ORM.User as orm

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, File, UploadFile, responses
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from api import user
from pathlib import Path
import shutil
import os

#公式ドキュメントの実装

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()
app.include_router(user.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def on_startup():
    orm.print_engine()
    return

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    user_info = orm.user_select(username)
    print("info:",user_info)
    if user_info:
        
        return UserInDB(
            username = user_info.name,
            email= user_info.email,
            full_name = user_info.name,
            disabled = False,
            hashed_password=user_info.password
            )


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
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
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    
    return current_user

class updateRequest(BaseModel):
    input_email: str
    input_age: int

@app.post("/users/me/update")
async def update_user_me(inputdata: updateRequest,current_user: User = Depends(get_current_active_user)):
    orm.user_update(
        current_user.username,
        inputdata.input_email,
        inputdata.input_age
    )

UPLOAD_DIR = Path(r"C:\Work\uploads")

@app.post("/upload")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        save_path = UPLOAD_DIR / file.filename
        
        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {"filename": file.filename, "save_path": str(save_path)}
    finally:
        file.file.close()
        


@app.get('/download')
async def download(item: str):
    return responses.FileResponse("C:/Work/uploads/"+item, filename='item')

@app.get('/play')
async def play(item: str):
    return responses.FileResponse("C:/Work/uploads/"+item, filename='item')

@app.get('/file-list')
async def file_list():
    dir_path = "C:/Work/uploads"

    files_file = [
        f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))
    ]
    print(files_file)
    return files_file