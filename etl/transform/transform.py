import pandas as pd
import numpy as np

def generate_random_foreign_keys(df, column_name, min_id=1, max_id=80):
    """
    Генерирует случайные значения для внешних ключей
    
    Args:
        df (pandas.DataFrame): Исходный датафрейм
        column_name (str): Название колонки с внешним ключом
        min_id (int): Минимальное значение ID
        max_id (int): Максимальное значение ID
        
    Returns:
        pandas.DataFrame: Датафрейм с обновленными внешними ключами
    """
    # Создаем копию DataFrame
    df = df.copy()
    
    # Генерируем случайные значения
    random_values = np.random.randint(min_id, max_id + 1, size=len(df))
    
    # Заменяем значения в колонке
    df.loc[:, column_name] = random_values
    
    return df

def clean_data(df):
    """
    Очищает данные от пропусков и дубликатов
    
    Args:
        df (pandas.DataFrame): Исходный датафрейм
        
    Returns:
        pandas.DataFrame: Очищенный датафрейм
    """
    # Создаем копию DataFrame
    df = df.copy()
    
    # Удаляем дубликаты
    df = df.drop_duplicates()
    
    # Заполняем пропуски в числовых колонках нулями
    numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
    df.loc[:, numeric_columns] = df[numeric_columns].fillna(0)
    
    # Заполняем пропуски в строковых колонках пустыми строками
    string_columns = df.select_dtypes(include=['object']).columns
    df.loc[:, string_columns] = df[string_columns].fillna('')
    
    return df

def transform_data(df, table_name):
    """
    Трансформирует данные в зависимости от таблицы
    
    Args:
        df (pandas.DataFrame): Исходный датафрейм
        table_name (str): Название таблицы
        
    Returns:
        pandas.DataFrame: Трансформированный датафрейм
    """
    df = clean_data(df)
    
    # Специфичные трансформации для разных таблиц
    if table_name == 'products':
        # Преобразуем цены в float
        df.loc[:, 'price'] = pd.to_numeric(df['price'], errors='coerce')
        # Преобразуем stock в int
        df.loc[:, 'stock'] = pd.to_numeric(df['stock'], errors='coerce').astype('Int64')
        # Генерируем случайные manufacturer_id и category_id
        if 'manufacturer_id' in df.columns:
            df = generate_random_foreign_keys(df, 'manufacturer_id')
        if 'category_id' in df.columns:
            df = generate_random_foreign_keys(df, 'category_id')
        
    elif table_name == 'orders':
        # Преобразуем дату в datetime
        df.loc[:, 'order_date'] = pd.to_datetime(df['order_date'])
        # Преобразуем total_price в float
        df.loc[:, 'total_price'] = pd.to_numeric(df['total_price'], errors='coerce')
        # Генерируем случайные user_id
        if 'user_id' in df.columns:
            df = generate_random_foreign_keys(df, 'user_id')
        
    elif table_name == 'reviews':
        # Преобразуем rating в int
        df.loc[:, 'rating'] = pd.to_numeric(df['rating'], errors='coerce').astype('Int64')
        # Преобразуем дату в datetime
        df.loc[:, 'review_date'] = pd.to_datetime(df['review_date'])
        # Генерируем случайные product_id и user_id
        # if 'product_id' in df.columns:
        #     df = generate_random_foreign_keys(df, 'product_id')
        # if 'user_id' in df.columns:
        #     df = generate_random_foreign_keys(df, 'user_id')
            
    elif table_name == 'order_items':
        # Генерируем случайные order_id и product_id
        if 'order_id' in df.columns:
            df = generate_random_foreign_keys(df, 'order_id')
        if 'product_id' in df.columns:
            df = generate_random_foreign_keys(df, 'product_id')
    
    return df 