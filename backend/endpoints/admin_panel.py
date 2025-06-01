from fastapi import APIRouter
from repositories import users as user_repo, orders as order_repo
from pydantic import BaseModel
import psycopg2
import os
from datetime import datetime, timedelta

router = APIRouter()

class OrderStatusUpdate(BaseModel):
    status: str

@router.get("/admin/users")
def get_all_users():
    # Получить всех пользователей
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

@router.get("/admin/dashboard/sales")
def get_sales_analytics():
    """
    Получает аналитику по продажам
    """
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
                # Общая сумма продаж
                cur.execute("""
                    SELECT COALESCE(SUM(total_price), 0) as total_sales
                    FROM orders
                    WHERE status != 'Cancelled'
                """)
                total_sales = cur.fetchone()[0]

                # Продажи по дням за последние 7 дней
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
                daily_sales = [
                    {
                        "date": row[0].strftime("%Y-%m-%d"),
                        "sales": float(row[1]),
                        "orders": row[2]
                    }
                    for row in cur.fetchall()
                ]

                # Топ продаваемых товаров
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
                top_products = [
                    {
                        "name": row[0],
                        "quantity": row[1],
                        "revenue": float(row[2])
                    }
                    for row in cur.fetchall()
                ]

                # Статистика по статусам заказов
                cur.execute("""
                    SELECT 
                        status,
                        COUNT(*) as count,
                        COALESCE(SUM(total_price), 0) as total_amount
                    FROM orders
                    GROUP BY status
                """)
                order_statuses = [
                    {
                        "status": row[0],
                        "count": row[1],
                        "amount": float(row[2])
                    }
                    for row in cur.fetchall()
                ]

                return {
                    "total_sales": float(total_sales),
                    "daily_sales": daily_sales,
                    "top_products": top_products,
                    "order_statuses": order_statuses
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении аналитики: {str(e)}")

@router.get("/admin/dashboard/inventory")
def get_inventory_analytics():
    """
    Получает аналитику по товарам на складе
    """
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
                # Товары с низким остатком (меньше 5)
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
                low_stock = [
                    {
                        "name": row[0],
                        "stock": row[1],
                        "category": row[2],
                        "manufacturer": row[3]
                    }
                    for row in cur.fetchall()
                ]

                # Распределение товаров по категориям
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
                category_stats = [
                    {
                        "category": row[0],
                        "product_count": row[1],
                        "total_stock": row[2],
                        "total_value": float(row[3])
                    }
                    for row in cur.fetchall()
                ]

                # Общая статистика по складу
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_products,
                        SUM(stock) as total_stock,
                        COALESCE(SUM(stock * price), 0) as total_value
                    FROM products
                """)
                total_stats = cur.fetchone()
                inventory_stats = {
                    "total_products": total_stats[0],
                    "total_stock": total_stats[1],
                    "total_value": float(total_stats[2])
                }

                return {
                    "low_stock": low_stock,
                    "category_stats": category_stats,
                    "inventory_stats": inventory_stats
                }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при получении аналитики: {str(e)}") 