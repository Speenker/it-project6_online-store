import psycopg2
import os
from datetime import datetime, timedelta

class AdminRepository:
    def __init__(self):
        self.DB_CONFIG = {
            "host": os.getenv("POSTGRES_HOST", "postgres"),
            "port": os.getenv("POSTGRES_PORT", 5432),
            "user": os.getenv("POSTGRES_USER", "user"),
            "password": os.getenv("POSTGRES_PASSWORD", "password"),
            "dbname": os.getenv("POSTGRES_DB", "store_db"),
        }

    def get_all_users(self):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, email, role, balance FROM users")
                users = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        return users

    def get_all_orders(self):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM orders")
                orders = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        return orders

    def get_order_items(self, order_id: int):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT oi.order_item_id, oi.quantity, p.* 
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.product_id
                    WHERE oi.order_id = %s
                """, (order_id,))
                items = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        return items

    def update_order_status(self, order_id: int, status: str):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE orders 
                    SET status = %s 
                    WHERE order_id = %s 
                    RETURNING *
                """, (status, order_id))
                updated_order = dict(zip([desc[0] for desc in cur.description], cur.fetchone()))
                conn.commit()
        return updated_order

    def get_total_sales(self):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT COALESCE(SUM(total_price), 0) as total_sales
                    FROM orders
                    WHERE status != 'Cancelled'
                """)
                return cur.fetchone()[0]

    def get_daily_sales(self):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        DATE(order_date) as date,
                        COALESCE(SUM(total_price), 0) as daily_sales,
                        COUNT(*) as orders_count
                    FROM orders
                    WHERE order_date >= NOW() - INTERVAL '7 days'
                    AND status != 'Cancelled'
                    GROUP BY DATE(order_date)
                    ORDER BY date
                """)
                return cur.fetchall()

    def get_top_products(self):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        p.name,
                        SUM(oi.quantity) as total_quantity,
                        SUM(oi.quantity * p.price) as total_revenue
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.product_id
                    JOIN orders o ON oi.order_id = o.order_id
                    WHERE o.status != 'Cancelled'
                    GROUP BY p.name
                    ORDER BY total_quantity DESC
                    LIMIT 5
                """)
                return cur.fetchall()

    def get_order_statuses(self):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        status,
                        COUNT(*) as count,
                        COALESCE(SUM(total_price), 0) as total_amount
                    FROM orders
                    GROUP BY status
                """)
                return cur.fetchall()

    def get_low_stock_products(self):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        p.name,
                        p.stock,
                        c.name as category,
                        m.name as manufacturer
                    FROM products p
                    LEFT JOIN categories c ON p.category_id = c.category_id
                    LEFT JOIN manufacturers m ON p.manufacturer_id = m.manufacturer_id
                    WHERE p.stock < 5
                    ORDER BY p.stock ASC
                """)
                return cur.fetchall()

    def get_category_stats(self):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        c.name as category,
                        COUNT(*) as product_count,
                        SUM(p.stock) as total_stock,
                        COALESCE(SUM(p.stock * p.price), 0) as total_value
                    FROM products p
                    JOIN categories c ON p.category_id = c.category_id
                    GROUP BY c.name
                """)
                return cur.fetchall()

    def get_inventory_summary(self):
        with psycopg2.connect(**self.DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_products,
                        SUM(stock) as total_stock,
                        COALESCE(SUM(stock * price), 0) as total_value
                    FROM products
                """)
                return cur.fetchone() 