import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from database.config import get_db
from database.models import (
    User, InterfaceSettings,
    Article,
    ArticleVector, Favorites,
    FavoritesArticles
)
from sqlalchemy.orm import joinedload

def display_all_tables(db):
    """Отображает содержимое всех таблиц"""
    print("\n=== Пользователи ===")
    users = db.query(User).all()
    for user in users:
        print(f"ID: {user.user_id}, Имя: {user.name}, Email: {user.email}")

    print("\n=== Настройки интерфейса ===")
    settings = db.query(InterfaceSettings).options(joinedload(InterfaceSettings.user)).all()
    for setting in settings:
        print(f"ID: {setting.settings_id}, Пользователь: {setting.user.name}, Тема: {setting.theme}")

    print("\n=== Статьи ===")
    articles = db.query(Article).all()  # Убрали joinedload для authors
    for article in articles:
        print(f"ID: {article.article_id}, Заголовок: {article.title}, Авторы: {article.authors}, URL: {article.article_url}")

    print("\n=== Векторные представления ===")
    vectors = db.query(ArticleVector).options(joinedload(ArticleVector.article)).all()
    for vector in vectors:
        print(f"ID: {vector.vector_id}, Статья: {vector.article.title}, Размер вектора: {len(vector.vector_data) if vector.vector_data else 0} байт")

    print("\n=== Избранное ===")
    favorites = db.query(Favorites).options(
        joinedload(Favorites.user),
        joinedload(Favorites.articles)
    ).all()
    for fav in favorites:
        articles = ", ".join([a.title for a in fav.articles]) if fav.articles else "Нет статей"
        print(f"ID: {fav.favorites_id}, Пользователь: {fav.user.name}, Статьи: {articles}")

    print("\n=== Связи избранное-статьи ===")
    fav_links = db.query(FavoritesArticles).all()
    for link in fav_links:
        print(f"Избранное ID: {link.favorites_id}, Статья ID: {link.article_id}")

if __name__ == "__main__":
    db = next(get_db())
    try:
        display_all_tables(db)
    finally:
        db.close()