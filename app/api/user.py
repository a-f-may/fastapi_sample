import os,sys
from fastapi import APIRouter, Depends, HTTPException
from typing import Union
from pydantic import BaseModel
from ORM.User import *
from passlib.context import CryptContext

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str
    age: int


router = APIRouter(
    prefix="/a1",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

def get_password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


@router.post("/sign-up")
async def register_user(request: SignUpRequest):
    hashed_password = get_password_hash(request.password)
    
    user_info = SampleTable(
        name = request.name,
        email = request.email,
        password = hashed_password,
        age = request.age
    )
    user_insert(user_info)
    
class UpdateRequest(BaseModel):
    email: str
    age: int

@router.post("/update")
async def update_user(request: UpdateRequest):
    hashed_password = get_password_hash(request.password)
    
    user_info = SampleTable(
        name = request.name,
        email = request.email,
        password = hashed_password,
        age = request.age
    )
    user_insert(user_info)