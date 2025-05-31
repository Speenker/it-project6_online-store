import psycopg2
import psycopg2.extras
import os

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": os.getenv("POSTGRES_PORT", 5432),
    "user": os.getenv("POSTGRES_USER", "user"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "dbname": os.getenv("POSTGRES_DB", "store_db"),
}

def create_order(user_id, total_price, order_date, status):
    query = "INSERT INTO orders (user_id, total_price, order_date, status) VALUES (%s, %s, %s, %s) RETURNING order_id"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (user_id, total_price, order_date, status))
            order_id = cur.fetchone()[0]
            conn.commit()
            return order_id

def get_user_orders(user_id):
    query = "SELECT * FROM orders WHERE user_id = %s ORDER BY order_date DESC"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (user_id,))
            return cur.fetchall()

def get_order_items(order_id):
    query = "SELECT oi.order_item_id, oi.quantity, p.name, p.price FROM order_items oi JOIN products p ON oi.product_id = p.product_id WHERE oi.order_id = %s"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (order_id,))
            return cur.fetchall() 