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

def get_user_by_email(email):
    query = "SELECT user_id, email, password, balance FROM users WHERE email = %s"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (email,))
            user = cur.fetchone()
            return user

def create_user(email, password):
    query = "INSERT INTO users (email, password, balance) VALUES (%s, %s, 0.0) RETURNING user_id, email, balance"
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, (email, password))
            user = cur.fetchone()
            conn.commit()
            return user

def check_user_password(email, password):
    user = get_user_by_email(email)
    if not user:
        return False
    return user["password"] == password 