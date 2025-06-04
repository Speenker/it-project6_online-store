import psycopg2
import os
from datetime import datetime

class CartRepository:
    def __init__(self):
        self.DB_CONFIG = {
            "host": os.getenv("POSTGRES_HOST", "postgres"),
            "port": os.getenv("POSTGRES_PORT", 5432),
            "user": os.getenv("POSTGRES_USER", "user"),
            "password": os.getenv("POSTGRES_PASSWORD", "password"),
            "dbname": os.getenv("POSTGRES_DB", "store_db"),
        }

    def check_product_stock(self, product_id: int, quantity: int):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT stock FROM products WHERE product_id = %s", (product_id,))
                result = cur.fetchone()
                if not result:
                    return None
                return result[0]

    def update_user_balance(self, user_id: int, new_balance: float):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE users SET balance = %s WHERE user_id = %s", (new_balance, user_id))
                conn.commit()

    def create_order_item(self, order_id: int, product_id: int, quantity: int):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (order_id, product_id, quantity)
                )
                conn.commit()

    def update_product_stock(self, product_id: int, quantity: int):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE products SET stock = stock - %s WHERE product_id = %s",
                    (quantity, product_id)
                )
                conn.commit() 