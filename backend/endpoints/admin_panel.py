from fastapi import APIRouter
from repositories import users as user_repo, orders as order_repo
from pydantic import BaseModel

router = APIRouter()

class OrderStatusUpdate(BaseModel):
    status: str

@router.get("/admin/users")
def get_all_users():
    # Получить всех пользователей
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
            cur.execute("SELECT user_id, email, role, balance FROM users")
            users = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
    return users

@router.get("/admin/orders")
def get_all_orders():
    # Получить все заказы
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
            cur.execute("SELECT * FROM orders")
            orders = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
    return orders

@router.get("/admin/orders/{order_id}/items")
def get_order_items(order_id: int):
    # Получить товары заказа
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
            cur.execute("""
                SELECT oi.order_item_id, oi.quantity, p.* 
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            items = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
    return items

@router.put("/admin/orders/{order_id}/status")
def update_order_status(order_id: int, status_update: OrderStatusUpdate):
    # Обновить статус заказа
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
            cur.execute("""
                UPDATE orders 
                SET status = %s 
                WHERE order_id = %s 
                RETURNING *
            """, (status_update.status, order_id))
            updated_order = dict(zip([desc[0] for desc in cur.description], cur.fetchone()))
            conn.commit()
    return updated_order 