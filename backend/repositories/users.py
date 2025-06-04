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
    """
    Получает пользователя по email
    
    Args:
        email (str): Email пользователя
        
    Returns:
        dict: Данные пользователя или None, если пользователь не найден
    """
    query = "SELECT user_id, email, password, balance FROM users WHERE email = %s"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, (email,))
                user = cur.fetchone()
                if user:
                    print(f"Найден пользователь {email} с паролем: {user['password'][:10]}...")
                else:
                    print(f"Пользователь {email} не найден")
                return user
    except Exception as e:
        print(f"Ошибка при получении пользователя {email}: {e}")
        return None

def get_users_with_password():
    """
    Получает всех пользователей с паролями
    
    Returns:
        list: Список пользователей с паролями
    """
    query = "SELECT user_id, email, password FROM users"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query)
                users = cur.fetchall()
                print(f"Получено {len(users)} пользователей из базы данных")
                for user in users:
                    print(f"Пользователь {user['email']} с паролем: {user['password'][:10]}...")
                return users
    except Exception as e:
        print(f"Ошибка при получении пользователей: {e}")
        return []

def update_user_balance(email: str, new_balance: float):
    """
    Обновляет баланс пользователя
    
    Args:
        email (str): Email пользователя
        new_balance (float): Новый баланс пользователя
        
    Returns:
        bool: True если обновление прошло успешно, False в противном случае
    """
    query = "UPDATE users SET balance = %s WHERE email = %s"
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (new_balance, email))
                conn.commit()
                return True
    except Exception as e:
        print(f"Ошибка при обновлении баланса пользователя {email}: {e}")
        return False

def create_user(email, password):
    """
    Создает нового пользователя
    
    Args:
        email (str): Email пользователя
        password (str): Хешированный пароль пользователя
        
    Returns:
        int: ID созданного пользователя
    """
    query = """
        INSERT INTO users (email, password, balance) 
        VALUES (%s, %s, 0.0) 
        RETURNING user_id
    """
    try:
        print(f"Создание пользователя {email} с паролем: {password[:10]}...")
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (email, password))
                user_id = cur.fetchone()[0]
                conn.commit()
                print(f"Пользователь {email} успешно создан с ID {user_id}")
                return user_id
    except Exception as e:
        print(f"Ошибка при создании пользователя {email}: {e}")
        raise

def check_user_password(email, password):
    user = get_user_by_email(email)
    if not user:
        return False
    return user["password"] == password 