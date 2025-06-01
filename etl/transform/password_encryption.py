import bcrypt
import psycopg2
from typing import Dict, Any
import os

def encrypt_passwords(conn_params: Dict[str, Any]) -> None:
    """
    Шифрует пароли в таблице users
    
    Args:
        conn_params (Dict[str, Any]): Параметры подключения к БД
    """
    # Хэширование паролей
    hashed_password_admin = bcrypt.hashpw("admin".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    hashed_password_user = bcrypt.hashpw("user".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Запросы на обновление
    query1 = """
        UPDATE users
        SET password = %(hashed_password)s
        WHERE email = 'admin@admin.com'
    """
    query2 = """
        UPDATE users
        SET password = %(hashed_password)s
        WHERE email != 'admin@admin.com'
    """
    
    try:
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query1, {"hashed_password": hashed_password_admin})
                cursor.execute(query2, {"hashed_password": hashed_password_user})
                conn.commit()
    except Exception as e:
        print(f"Ошибка при шифровании паролей: {e}")
        raise 