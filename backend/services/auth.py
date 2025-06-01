import bcrypt
from repositories import users as user_repo

class Authorize:
    def __init__(self):
        pass

    def auth(self, email, password: str):
        user = user_repo.get_user_by_email(email)
        if not user:
            print(f"Пользователь {email} не найден")
            return False

        stored_password = user["password"]
        if not stored_password:
            print(f"Пароль для пользователя {email} не найден")
            return False

        try:
            # Проверяем, является ли stored_password уже хешем
            if stored_password.startswith('$2b$'):
                print(f"Проверка хешированного пароля для {email}")
                result = bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8"))
                print(f"Результат проверки пароля: {result}")
                return result
            else:
                # Если пароль не хеширован, сравниваем напрямую
                print(f"Прямое сравнение паролей для {email}")
                result = password == stored_password
                print(f"Результат сравнения: {result}")
                return result
        except Exception as e:
            print(f"Ошибка при проверке пароля для {email}: {e}")
            return False

    def hash_password(self, password: str) -> str:
        """
        Хеширует пароль с использованием bcrypt
        
        Args:
            password (str): Пароль для хеширования
            
        Returns:
            str: Хешированный пароль
        """
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
            print(f"Пароль успешно хеширован: {hashed[:10]}...")
            return hashed
        except Exception as e:
            print(f"Ошибка при хешировании пароля: {e}")
            raise 