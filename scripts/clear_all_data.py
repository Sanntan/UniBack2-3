# scripts/clear_all_data.py

import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from database.config import SessionLocal
from database.models import (
    User, InterfaceSettings, Article,
    ArticleVector, Favorites,
    FavoritesArticles, Base
)
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError


def clear_all_tables():
    """Очищает все таблицы и сбрасывает все sequence"""
    db = SessionLocal()
    try:
        # Отключаем проверку внешних ключей
        db.execute(text("SET session_replication_role = 'replica';"))

        # Удаляем записи
        db.query(FavoritesArticles).delete()
        db.query(ArticleVector).delete()
        db.query(Favorites).delete()
        db.query(InterfaceSettings).delete()
        db.query(Article).delete()
        db.query(User).delete()

        # Сбрасываем sequences для всех таблиц
        sequences = [
            "user_user_id_seq",
            "interface_settings_settings_id_seq",
            "favorites_favorites_id_seq",
            "article_article_id_seq",
            "article_vector_vector_id_seq"
        ]

        for seq in sequences:
            db.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1;"))

        # Включаем проверку внешних ключей обратно
        db.execute(text("SET session_replication_role = 'origin';"))

        db.commit()
        print("✅ Все таблицы очищены. Все счётчики ID сброшены.")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Ошибка при очистке таблиц: {e}")
    finally:
        db.close()


def drop_and_recreate_tables():
    """Полностью пересоздаёт таблицы"""
    db = SessionLocal()
    try:
        Base.metadata.drop_all(bind=db.get_bind())
        Base.metadata.create_all(bind=db.get_bind())
        print("✅ Таблицы успешно пересозданы.")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Ошибка при пересоздании таблиц: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("Выберите действие:")
    print("1 - Очистить данные в таблицах")
    print("2 - Полностью пересоздать таблицы")
    choice = input("Введите номер (1/2): ").strip()

    if choice == "1":
        clear_all_tables()
    elif choice == "2":
        drop_and_recreate_tables()
    else:
        print("Неверный выбор. Введите 1 или 2.")