import pandas as pd
import os

def read_csv_file(file_path):
    """
    Читает данные из CSV файла
    
    Args:
        file_path (str): Путь к CSV файлу
        
    Returns:
        pandas.DataFrame: Данные из CSV файла
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден")
    
    return pd.read_csv(file_path, encoding='utf-8')

def get_data_files():
    """
    Получает список всех CSV файлов в директории data
    
    Returns:
        list: Список путей к CSV файлам
    """
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    return [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.csv')] 