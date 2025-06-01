from clickhouse_driver import Client
import os
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

# ClickHouse configuration
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 9000))
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "default")

# PostgreSQL configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_DB = os.getenv("POSTGRES_DB", "store_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

# Initialize ClickHouse client
client = Client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, database=CLICKHOUSE_DB)

def get_user_activity_analytics():
    """
    Получает аналитику по активности пользователей за последние 24 часа и 7 дней
    Возвращает словарь с структурированными данными:
    {
        "hourly_activity": [{"hour": int, "count": int}, ...],
        "top_actions": [{"action": str, "count": int}, ...],
        "daily_activity": [{"date": str, "count": int}, ...],
        "top_users": [{"email": str, "count": int}, ...]
    }
    """
    # Получаем сырые данные из ClickHouse
    hourly_activity_raw = client.execute('''
        SELECT 
            toHour(timestamp) as hour,
            count() as action_count
        FROM user_actions
        WHERE timestamp >= now() - INTERVAL 24 HOUR
        GROUP BY hour
        ORDER BY hour
    ''')
    
    top_actions_raw = client.execute('''
        SELECT 
            action_type,
            count() as count
        FROM user_actions
        WHERE timestamp >= now() - INTERVAL 7 DAY
        GROUP BY action_type
        ORDER BY count DESC
        LIMIT 5
    ''')
    
    daily_activity_raw = client.execute('''
        SELECT 
            toDate(timestamp) as date,
            count() as action_count
        FROM user_actions
        WHERE timestamp >= now() - INTERVAL 7 DAY
        GROUP BY date
        ORDER BY date
    ''')
    
    top_users_raw = client.execute('''
        SELECT 
            email,
            count() as action_count
        FROM user_actions
        WHERE timestamp >= now() - INTERVAL 7 DAY
        GROUP BY email
        ORDER BY action_count DESC
        LIMIT 5
    ''')

    # Обрабатываем данные по часам - заполняем пропущенные часы нулями
    hourly_activity = []
    all_hours = range(24)  # Все возможные часы в сутках
    
    # Создаем словарь для быстрого доступа
    hour_counts = {hour: count for hour, count in hourly_activity_raw}
    
    for hour in all_hours:
        hourly_activity.append({
            "hour": hour,
            "count": hour_counts.get(hour, 0)  # 0 если час отсутствует в данных
        })

    # Обрабатываем остальные данные
    return {
        "hourly_activity": hourly_activity,
        "top_actions": [{"action": action, "count": count} for action, count in top_actions_raw],
        "daily_activity": [{"date": date.strftime("%Y-%m-%d"), "count": count} for date, count in daily_activity_raw],
        "top_users": [{"email": email, "count": count} for email, count in top_users_raw]
    }

def get_error_analytics():
    """
    Получает аналитику по ошибкам
    """
    # Ошибки по типам
    error_types = client.execute('''
        SELECT 
            action_type,
            count() as count
        FROM user_actions
        WHERE details LIKE '%error%' OR details LIKE '%Error%'
        AND timestamp >= now() - INTERVAL 7 DAY
        GROUP BY action_type
        ORDER BY count DESC
    ''')
    
    # Ошибки по времени
    error_timeline = client.execute('''
        SELECT 
            toDate(timestamp) as date,
            count() as error_count
        FROM user_actions
        WHERE details LIKE '%error%' OR details LIKE '%Error%'
        AND timestamp >= now() - INTERVAL 7 DAY
        GROUP BY date
        ORDER BY date
    ''')
    
    return {
        "error_types": [{"type": t, "count": c} for t, c in error_types],
        "error_timeline": [{"date": d.strftime("%Y-%m-%d"), "count": c} for d, c in error_timeline]
    }

def get_user_behavior_analytics():
    """
    Получает аналитику по поведению пользователей
    """
    # Последовательности действий
    action_sequences = client.execute('''
        SELECT 
            email,
            groupArray(action_type) as actions
        FROM (
            SELECT 
                email,
                action_type,
                timestamp
            FROM user_actions
            WHERE timestamp >= now() - INTERVAL 24 HOUR
            AND email != ''
            ORDER BY email, timestamp
        )
        GROUP BY email
        LIMIT 10
    ''')
    
    # Среднее время между действиями (исправленная версия)
    avg_time_between_actions = client.execute('''
        WITH user_times AS (
            SELECT 
                email,
                timestamp,
                min(timestamp) OVER (PARTITION BY email ORDER BY timestamp ROWS BETWEEN 1 FOLLOWING AND 1 FOLLOWING) as next_timestamp
            FROM user_actions
            WHERE timestamp >= now() - INTERVAL 24 HOUR
            AND email != ''
        )
        SELECT avg(dateDiff('second', timestamp, next_timestamp)) as avg_time
        FROM user_times
        WHERE next_timestamp IS NOT NULL
    ''')
    
    return {
        "action_sequences": [{"email": e, "actions": a} for e, a in action_sequences if e],  # Фильтруем пустые email
        "avg_time_between_actions": avg_time_between_actions[0][0] if avg_time_between_actions and avg_time_between_actions[0][0] is not None else 0
    }

def get_financial_analytics():
    """
    Получает финансовую аналитику
    """
    # Общая сумма продаж
    total_sales = client.execute('''
        SELECT sum(CAST(JSONExtractFloat(details, 'total_amount') as Decimal(10,2))) as total
        FROM user_actions
        WHERE action_type = 'checkout'
        AND timestamp >= now() - INTERVAL 30 DAY
        AND details != ''
    ''')
    
    # Продажи по дням
    daily_sales = client.execute('''
        SELECT 
            toDate(timestamp) as date,
            sum(CAST(JSONExtractFloat(details, 'total_amount') as Decimal(10,2))) as amount
        FROM user_actions
        WHERE action_type = 'checkout'
        AND timestamp >= now() - INTERVAL 30 DAY
        AND details != ''
        GROUP BY date
        ORDER BY date
    ''')
    
    # Средний чек
    avg_check = client.execute('''
        SELECT avg(CAST(JSONExtractFloat(details, 'total_amount') as Decimal(10,2))) as avg_amount
        FROM user_actions
        WHERE action_type = 'checkout'
        AND timestamp >= now() - INTERVAL 30 DAY
        AND details != ''
    ''')
    
    # Топ покупателей
    top_buyers = client.execute('''
        SELECT 
            email,
            sum(CAST(JSONExtractFloat(details, 'total_amount') as Decimal(10,2))) as total_spent
        FROM user_actions
        WHERE action_type = 'checkout'
        AND timestamp >= now() - INTERVAL 30 DAY
        AND details != ''
        AND email != ''
        GROUP BY email
        ORDER BY total_spent DESC
        LIMIT 5
    ''')
    
    return {
        "total_sales": float(total_sales[0][0]) if total_sales and total_sales[0][0] is not None else 0,
        "daily_sales": [{"date": d.strftime("%Y-%m-%d"), "amount": float(a)} for d, a in daily_sales if a is not None],
        "avg_check": float(avg_check[0][0]) if avg_check and avg_check[0][0] is not None else 0,
        "top_buyers": [{"email": e, "total_spent": float(t)} for e, t in top_buyers if t is not None]
    }

def get_extended_financial_analytics():
    """
    Получает расширенную финансовую аналитику из PostgreSQL
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
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Общая статистика по заказам
                cur.execute('''
                    SELECT 
                        COUNT(*) as total_orders,
                        SUM(total_price) as total_revenue,
                        AVG(total_price) as avg_order_value,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_orders,
                        COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled_orders
                    FROM orders
                    WHERE order_date >= NOW() - INTERVAL '30 days'
                ''')
                order_stats = cur.fetchone()
                
                # Статистика по категориям
                cur.execute('''
                    SELECT 
                        c.name as category,
                        COUNT(DISTINCT o.order_id) as order_count,
                        SUM(oi.quantity) as total_items,
                        SUM(oi.quantity * p.price) as total_revenue
                    FROM orders o
                    JOIN order_items oi ON o.order_id = oi.order_id
                    JOIN products p ON oi.product_id = p.product_id
                    JOIN categories c ON p.category_id = c.category_id
                    WHERE o.order_date >= NOW() - INTERVAL '30 days'
                    GROUP BY c.category_id, c.name
                    ORDER BY total_revenue DESC
                    LIMIT 5
                ''')
                category_stats = cur.fetchall()
                
                # Статистика по продуктам
                cur.execute('''
                    SELECT 
                        p.name as product,
                        COUNT(DISTINCT o.order_id) as order_count,
                        SUM(oi.quantity) as total_quantity,
                        SUM(oi.quantity * p.price) as total_revenue,
                        p.stock as current_stock
                    FROM orders o
                    JOIN order_items oi ON o.order_id = oi.order_id
                    JOIN products p ON oi.product_id = p.product_id
                    WHERE o.order_date >= NOW() - INTERVAL '30 days'
                    GROUP BY p.product_id, p.name, p.stock
                    ORDER BY total_revenue DESC
                    LIMIT 5
                ''')
                product_stats = cur.fetchall()
                
                # Статистика по времени заказов
                cur.execute('''
                    SELECT 
                        DATE_TRUNC('hour', order_date) as hour,
                        COUNT(*) as order_count,
                        SUM(total_price) as total_revenue
                    FROM orders
                    WHERE order_date >= NOW() - INTERVAL '30 days'
                    GROUP BY hour
                    ORDER BY hour
                ''')
                hourly_stats = cur.fetchall()
                
                # Статистика по клиентам
                cur.execute('''
                    SELECT 
                        u.email,
                        COUNT(DISTINCT o.order_id) as order_count,
                        SUM(o.total_price) as total_spent,
                        AVG(o.total_price) as avg_order_value
                    FROM orders o
                    JOIN users u ON o.user_id = u.user_id
                    WHERE o.order_date >= NOW() - INTERVAL '30 days'
                    GROUP BY u.user_id, u.email
                    ORDER BY total_spent DESC
                    LIMIT 5
                ''')
                customer_stats = cur.fetchall()
                
                return {
                    "order_stats": dict(order_stats) if order_stats else {},
                    "category_stats": [dict(row) for row in category_stats],
                    "product_stats": [dict(row) for row in product_stats],
                    "hourly_stats": [dict(row) for row in hourly_stats],
                    "customer_stats": [dict(row) for row in customer_stats]
                }
            
    finally:
        conn.close() 