import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


def test_db_connection():
    conn = None  # Инициализируем переменную
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not found in .env")

        print(f"Попытка подключения к: {db_url.split('@')[1].split('/')[0]}")  # Логирование хоста

        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()

        print("Успешное подключение к PostgreSQL!")
        print("Версия PostgreSQL:", db_version)

        # Дополнительный тест для Supabase
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print("Имя базы данных:", db_name[0])

    except Exception as e:
        print("Ошибка при подключении к PostgreSQL:", e)
    finally:
        if conn:
            conn.close()
            print("Соединение закрыто")


if __name__ == "__main__":
    test_db_connection()