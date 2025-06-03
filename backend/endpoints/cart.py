from fastapi import APIRouter, HTTPException, Body, Query
from repositories import products as product_repo, orders as order_repo, users as user_repo
from typing import Dict
import datetime
import psycopg2
import os

router = APIRouter()

# Временное хранилище корзин (на пользователя)
carts = {}

@router.get("/cart")
def get_cart(email: str = Query(...)):
    cart = carts.get(email, {"items": []})
    return cart

@router.post("/cart/add")
def add_to_cart(data: Dict = Body(...)):
    email = data["email"]
    product_id = data["product_id"]
    quantity = int(data.get("quantity", 1))
    # Получить товар
    product = product_repo.get_product_details(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    # Добавить в корзину
    cart = carts.setdefault(email, {"items": []})
    # Проверить, есть ли уже этот товар
    for item in cart["items"]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        cart["items"].append({
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity
        })
    return {"status": "ok"}

@router.post("/cart/checkout")
def checkout_cart(data: Dict = Body(...)):
    email = data["email"]
    cart = carts.get(email)
    if not cart or not cart["items"]:
        raise HTTPException(status_code=400, detail="Корзина пуста")

    user = user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    total_price = sum(item["quantity"] * item["price"] for item in cart["items"])
    if float(user["balance"]) < total_price:
        raise HTTPException(status_code=400, detail="Недостаточно средств на балансе")

    DB_CONFIG = {
        "host": os.getenv("POSTGRES_HOST", "postgres"),
        "port": os.getenv("POSTGRES_PORT", 5432),
        "user": os.getenv("POSTGRES_USER", "user"),
        "password": os.getenv("POSTGRES_PASSWORD", "password"),
        "dbname": os.getenv("POSTGRES_DB", "store_db"),
    }

    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Проверка остатков
                for item in cart["items"]:
                    cur.execute("SELECT stock FROM products WHERE product_id = %s", (item["product_id"],))
                    result = cur.fetchone()
                    if not result:
                        raise HTTPException(status_code=404, detail=f"Товар с ID {item['product_id']} не найден")
                    available_stock = result[0]
                    if item["quantity"] > available_stock:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Недостаточно товара '{item['name']}'. Доступно: {available_stock}"
                        )

                # Обновляем баланс
                new_balance = float(user["balance"]) - total_price
                cur.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_balance, user["user_id"]))

                # Создаём заказ
                order_id = order_repo.create_order(
                    user_id=user["user_id"],
                    total_price=total_price,
                    order_date=datetime.datetime.now(),
                    status="Pending"
                )

                # Добавляем товары и обновляем остатки
                for item in cart["items"]:
                    cur.execute(
                        "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                        (order_id, item["product_id"], item["quantity"])
                    )
                    cur.execute(
                        "UPDATE products SET stock = stock - %s WHERE product_id = %s",
                        (item["quantity"], item["product_id"])
                    )

                conn.commit()

        carts[email] = {"items": []}
        return {"status": "ok", "order_id": order_id}

    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e.pgerror}")


@router.get("/cart/clear")
def clear_cart(data: Dict = Body(...)):
    email = data["email"]
    carts[email] = {"items": []}
    return {"status": "ok"} 