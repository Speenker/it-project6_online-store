from clickhouse_driver import Client
import os
from datetime import datetime

# ClickHouse configuration
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 9000))
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "default")

# Initialize ClickHouse client
client = Client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, database=CLICKHOUSE_DB)

def init_clickhouse_tables():
    """Initialize ClickHouse tables for logging"""
    client.execute('''
        CREATE TABLE IF NOT EXISTS user_actions (
            timestamp DateTime,
            action_type String,
            email String,
            details String
        ) ENGINE = MergeTree()
        ORDER BY (timestamp, action_type, email)
    ''')

def log_to_clickhouse(action_type, email, **kwargs):
    """Log user action to ClickHouse"""
    try:
        # Convert None to empty string for email
        email = email if email is not None else ''
        # Convert None values in kwargs to empty strings
        kwargs = {k: (v if v is not None else '') for k, v in kwargs.items()}
        
        client.execute(
            'INSERT INTO user_actions (timestamp, action_type, email, details) VALUES',
            [(datetime.now(), action_type, email, str(kwargs))]
        )
    except Exception as e:
        print(f"Failed to log to ClickHouse: {str(e)}")

# Initialize tables on module import
init_clickhouse_tables() 