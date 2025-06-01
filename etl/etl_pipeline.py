import os
from extract.extract import read_csv_file, get_data_files
from transform.transform import transform_data
from load.load import create_tables, load_data

# Порядок загрузки таблиц в соответствии с зависимостями
TABLE_LOAD_ORDER = [
    'manufacturers',
    'categories',
    'users',
    'products',
    'orders',
    'reviews',
    'order_items'
]

def run_etl():
    """
    Запускает ETL пайплайн
    """
    # Создаем таблицы
    create_tables()
    
    # Получаем список CSV файлов
    data_files = get_data_files()
    
    # Сортируем файлы в соответствии с порядком загрузки
    sorted_files = []
    for table_name in TABLE_LOAD_ORDER:
        for file_path in data_files:
            if os.path.splitext(os.path.basename(file_path))[0] == table_name:
                sorted_files.append(file_path)
                break
    
    # Обрабатываем каждый файл в правильном порядке
    for file_path in sorted_files:
        # Получаем имя таблицы из имени файла
        table_name = os.path.splitext(os.path.basename(file_path))[0]
        
        try:
            # Извлекаем данные
            print(f"Извлечение данных из {file_path}")
            df = read_csv_file(file_path)
            
            # Трансформируем данные
            print(f"Трансформация данных для таблицы {table_name}")
            df = transform_data(df, table_name)
            
            # Загружаем данные
            print(f"Загрузка данных в таблицу {table_name}")
            load_data(df, table_name)
            
        except Exception as e:
            print(f"Ошибка при обработке файла {file_path}: {str(e)}")
            continue

if __name__ == "__main__":
    run_etl() 