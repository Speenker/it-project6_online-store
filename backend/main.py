from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import uuid
from repositories import users as user_repo
from repositories import admin as admin_repo
from services.auth import Authorize
from endpoints.products import router as products_router
from endpoints.profile import router as profile_router
from endpoints.cart import router as cart_router
from endpoints.admin_panel import router as admin_panel_router
from repositories.es_sync import sync_products_to_es

app = FastAPI()
app.include_router(products_router)
app.include_router(profile_router)
app.include_router(cart_router)
app.include_router(admin_panel_router)

# Список email'ов администраторов
admin_emails = ["admin@admin.com"]

# Инициализация сервиса авторизации
auth_service = Authorize()

class UserIn(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    user_id: int
    email: str
    balance: float

@app.on_event("startup")
def sync_es_on_startup():
    sync_products_to_es()

@app.post("/login")
def login(user: UserIn):
    print(f"Попытка входа пользователя {user.email}")
    if not auth_service.auth(user.email, user.password):
        print(f"Неудачная попытка входа для {user.email}")
        raise HTTPException(status_code=401, detail="Неверная почта или пароль")
    
    user_db = user_repo.get_user_by_email(user.email)
    token = str(uuid.uuid4())
    is_admin = user_db["email"] in admin_emails
    
    print(f"Успешный вход пользователя {user.email}, admin={is_admin}")
    return {
        "token": token,
        "user": {
            "user_id": user_db["user_id"],
            "email": user_db["email"],
            "balance": user_db["balance"]
        },
        "is_admin": is_admin
    }

@app.post("/register")
def register(user: UserIn):
    print(f"Попытка регистрации пользователя {user.email}")
    
    if user_repo.get_user_by_email(user.email):
        print(f"Пользователь {user.email} уже существует")
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")
    
    # Хешируем пароль перед сохранением
    hashed_password = auth_service.hash_password(user.password)
    print(f"Пароль для {user.email} успешно хеширован")
    
    # Создаем пользователя с хешированным паролем
    user_id = user_repo.create_user(user.email, hashed_password)
    print(f"Пользователь {user.email} создан с ID {user_id}")
    
    # Получаем созданного пользователя для проверки
    new_user = user_repo.get_user_by_email(user.email)
    if not new_user:
        print(f"Ошибка: пользователь {user.email} не найден после создания")
        raise HTTPException(status_code=500, detail="Ошибка при создании пользователя")
    
    print(f"Регистрация пользователя {user.email} успешно завершена")
    return {
        "user_id": user_id,
        "email": user.email,
        "message": "Пользователь успешно зарегистрирован"
    }

@app.get("/user")
def get_user(email: str):
    user_db = user_repo.get_user_by_email(email)
    if not user_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"user_id": user_db["user_id"], "email": user_db["email"], "balance": user_db["balance"]}

@app.get("/ping")
def ping():
    return {"message": "pong"} 