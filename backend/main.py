from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import uuid
from repositories import users as user_repo
from endpoints.products import router as products_router
from endpoints.profile import router as profile_router
from endpoints.cart import router as cart_router
from endpoints.admin_panel import router as admin_panel_router

app = FastAPI()
app.include_router(products_router)
app.include_router(profile_router)
app.include_router(cart_router)
app.include_router(admin_panel_router)

admin_emails = {"admin@example.com"}

class UserIn(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    user_id: str
    email: str
    balance: float = 0.0

class RegisterIn(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(user: UserIn):
    user_db = user_repo.get_user_by_email(user.email)
    if not user_db or user_db["password"] != user.password:
        raise HTTPException(status_code=401, detail="Неверная почта или пароль")
    token = str(uuid.uuid4())
    return {
        "token": token,
        "user": {"user_id": user_db["user_id"], "email": user_db["email"], "balance": user_db["balance"]},
        "is_admin": user_db["email"] in admin_emails
    }

@app.post("/register", status_code=201)
def register(user: RegisterIn):
    user_db = user_repo.get_user_by_email(user.email)
    if user_db:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    new_user = user_repo.create_user(user.email, user.password)
    return {"user_id": new_user["user_id"], "email": new_user["email"]}

@app.get("/user")
def get_user(email: str):
    user_db = user_repo.get_user_by_email(email)
    if not user_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"user_id": user_db["user_id"], "email": user_db["email"], "balance": user_db["balance"]}

@app.get("/ping")
def ping():
    return {"message": "pong"} 