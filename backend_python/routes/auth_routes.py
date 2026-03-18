from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(tags=["auth"])

users_db = {}


class SignupRequest(BaseModel):
    email: str
    password: str
    user_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/signup")
def signup(data: SignupRequest):

    if data.email in users_db:
        return {"message": "User already exists"}

    users_db[data.email] = {
        "password": hash_password(data.password),
        "user_name": data.user_name
    }

    return {"message": "User created successfully"}


@router.post("/login")
def login(data: LoginRequest):

    user = users_db.get(data.email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({"sub": data.email})

    return {
        "access_token": token,
        "email": data.email,
        "username": user["user_name"]
    }