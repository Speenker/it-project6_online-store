import psycopg2
import psycopg2.extras
import os
import sys

# Добавляем корневую директорию проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from etl.config.db_config import DB_CONFIG

def create_tables():
    """
    Создает таблицы в базе данных
    """
    sql_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'init_tables.sql')
    if not os.path.exists(sql_path):
        raise FileNotFoundError(f"Файл {sql_path} не найден")
        
    with open(sql_path, 'r', encoding='utf-8') as f:
        ddl_script = f.read()
        
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(ddl_script)
            conn.commit()

def load_data(df, table_name):
    """
    Загружает данные в таблицу базы данных
    
    Args:
        df (pandas.DataFrame): Данные для загрузки
        table_name (str): Название таблицы
    """
    if df.empty:
        print(f"Нет данных для загрузки в таблицу {table_name}")
        return
        
    # Получаем список колонок
    columns = df.columns.tolist()
    
    # Создаем строку с плейсхолдерами для SQL запроса
    placeholders = ','.join(['%s'] * len(columns))
    
    # Создаем SQL запрос
    query = f"""
        INSERT INTO {table_name} ({','.join(columns)})
        VALUES ({placeholders})
        ON CONFLICT DO NOTHING
    """
    
    # Преобразуем DataFrame в список кортежей
    values = [tuple(x) for x in df.to_numpy()]
    
    # Загружаем данные
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_batch(cur, query, values)
            conn.commit()
            
    print(f"Загружено {len(values)} записей в таблицу {table_name}") 