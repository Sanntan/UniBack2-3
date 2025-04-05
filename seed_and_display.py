from database.config import get_db
from database.models import User, InterfaceSettings
from sqlalchemy.orm import Session, joinedload
import random
import string


def generate_random_email():
    name = ''.join(random.choices(string.ascii_lowercase, k=5))
    return f"{name}@example.com"


def seed_database(db: Session):
    """Заполняет таблицы тестовыми данными"""
    print("\nДобавление тестовых данных...")

    # Очищаем таблицы перед заполнением
    db.query(InterfaceSettings).delete()
    db.query(User).delete()
    db.commit()

    # Создаем 5 пользователей
    themes = ["light", "dark", "system"]
    for i in range(1, 6):
        user = User(
            name=f"Пользователь {i}",
            email=generate_random_email()
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Создаем настройки для каждого пользователя
        settings = InterfaceSettings(
            user_id=user.user_id,
            theme=random.choice(themes),
            font_size=random.randint(10, 16),
            language=random.choice(["ru", "en"])
        )
        db.add(settings)

    db.commit()
    print("Данные успешно добавлены!")


def display_data(db: Session):
    """Выводит содержимое таблиц"""
    print("\nСодержимое таблицы User:")
    users = db.query(User).all()
    for user in users:
        print(f"ID: {user.user_id}, Имя: {user.name}, Email: {user.email}")

    print("\nСодержимое таблицы InterfaceSettings:")
    settings = db.query(InterfaceSettings).options(joinedload(InterfaceSettings.user)).all()
    for setting in settings:
        print(
            f"Пользователь: {setting.user.name}, Тема: {setting.theme}, Размер шрифта: {setting.font_size}, Язык: {setting.language}")


if __name__ == "__main__":
    db = next(get_db())

    # Заполняем таблицы тестовыми данными
    seed_database(db)

    # Выводим содержимое таблиц
    display_data(db)

    db.close()