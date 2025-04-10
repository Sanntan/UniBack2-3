# scripts/clear_all_data.py
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from database.config import get_db
from database.models import (
    User, InterfaceSettings, Article,
    ArticleVector, Favorites,
    FavoritesArticles, Base
)


def clear_all_tables(db):
    """Очищает все таблицы в правильном порядке с учетом зависимостей"""
    try:
        # Отключаем проверку внешних ключей для безопасного удаления
        db.execute(text("SET session_replication_role = 'replica';"))

        # Удаляем данные из таблиц с учетом зависимостей
        db.query(FavoritesArticles).delete()
        db.query(ArticleVector).delete()
        db.query(Favorites).delete()
        db.query(InterfaceSettings).delete()
        db.query(Article).delete()
        db.query(User).delete()

        # Включаем проверку внешних ключей обратно
        db.execute(text("SET session_replication_role = 'origin';"))

        db.commit()
        print("Все таблицы успешно очищены!")
    except Exception as e:
        db.rollback()
        raise e


def drop_and_recreate_tables(db):
    """Полностью удаляет и создает таблицы заново (более радикальный вариант)"""
    try:
        Base.metadata.drop_all(bind=db.get_bind())
        Base.metadata.create_all(bind=db.get_bind())
        print("Таблицы успешно пересозданы!")
    except Exception as e:
        db.rollback()
        raise e


if __name__ == "__main__":
    db = next(get_db())
    try:
        print("Выберите действие:")
        print("1 - Очистить данные в таблицах")
        print("2 - Полностью пересоздать таблицы")
        choice = input("Введите номер (1/2): ").strip()

        if choice == "1":
            clear_all_tables(db)
        elif choice == "2":
            drop_and_recreate_tables(db)
        else:
            print("Неверный выбор. Введите 1 или 2.")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        db.close()