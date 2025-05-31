from fastapi import APIRouter, HTTPException, Body, Query
from repositories import users as user_repo, orders as order_repo
from typing import Dict

router = APIRouter()

@router.get("/user")
def get_user(email: str = Query(...)):
    user = user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.post("/user/balance")
def update_balance(data: Dict = Body(...)):
    email = data["email"]
    amount = data["amount"]
    user = user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    new_balance = float(user["balance"]) + float(amount)
    # Обновить баланс
    import psycopg2, os
    DB_CONFIG = {
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "port": os.getenv("POSTGRES_PORT", 5432),
        "user": os.getenv("POSTGRES_USER", "user"),
        "password": os.getenv("POSTGRES_PASSWORD", "password"),
        "dbname": os.getenv("POSTGRES_DB", "store_db"),
    }
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET balance = %s WHERE email = %s", (new_balance, email))
            conn.commit()
    return {"balance": new_balance}

@router.get("/orders")
def get_user_orders(email: str = Query(...)):
    user = user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return order_repo.get_user_orders(user["user_id"])

@router.get("/orders/{order_id}/items")
def get_order_items(order_id: int):
    return order_repo.get_order_items(order_id) 