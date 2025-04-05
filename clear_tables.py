from database.config import get_db
from database.models import User, InterfaceSettings

def clear_tables():
    """Очищает указанные таблицы"""
    db = next(get_db())
    try:
        # Удаляем данные в правильном порядке из-за foreign key constraints
        db.query(InterfaceSettings).delete()
        db.query(User).delete()
        db.commit()
        print("Таблицы User и InterfaceSettings успешно очищены!")
    except Exception as e:
        db.rollback()
        print(f"Ошибка при очистке таблиц: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    clear_tables()