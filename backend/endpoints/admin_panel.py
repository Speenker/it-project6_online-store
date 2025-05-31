from fastapi import APIRouter
from repositories import users as user_repo, orders as order_repo

router = APIRouter()

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
            cur.execute("SELECT user_id, email, role FROM users")
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