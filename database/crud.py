from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional
from database import models
from database.schemas import UserCreate, UserUpdate, ArticleCreate, ArticleUpdate, AuthorCreate, AuthorUpdate


# ========== User CRUD ==========
def create_user(db: Session, user: UserCreate):
    db_user = models.User(
        name=user.name,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Создаем связанные записи (1:1)
    create_interface_settings(db, user_id=db_user.user_id)
    create_favorites(db, user_id=db_user.user_id)

    return db_user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: int, user: UserUpdate):
    db_user = get_user(db, user_id=user_id)
    if db_user:
        for var, value in vars(user).items():
            if value is not None:
                setattr(db_user, var, value)
        db.commit()
        db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id=user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


# ========== InterfaceSettings CRUD ==========
def create_interface_settings(db: Session, user_id: int, theme: str = "light"):
    db_settings = models.InterfaceSettings(
        user_id=user_id,
        theme=theme
    )
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings


def get_interface_settings(db: Session, user_id: int):
    return db.query(models.InterfaceSettings).filter(models.InterfaceSettings.user_id == user_id).first()


def update_interface_settings(db: Session, user_id: int, theme: str = None, font_size: int = None,
                              language: str = None):
    db_settings = get_interface_settings(db, user_id=user_id)
    if db_settings:
        if theme is not None:
            db_settings.theme = theme
        if font_size is not None:
            db_settings.font_size = font_size
        if language is not None:
            db_settings.language = language
        db.commit()
        db.refresh(db_settings)
    return db_settings


# ========== Author CRUD ==========
def create_author(db: Session, author: AuthorCreate):
    db_author = models.Author(
        name=author.name,
        bio=author.bio
    )
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


def get_author(db: Session, author_id: int):
    return db.query(models.Author).filter(models.Author.author_id == author_id).first()


def get_authors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Author).offset(skip).limit(limit).all()


def update_author(db: Session, author_id: int, author: AuthorUpdate):
    db_author = get_author(db, author_id=author_id)
    if db_author:
        for var, value in vars(author).items():
            if value is not None:
                setattr(db_author, var, value)
        db.commit()
        db.refresh(db_author)
    return db_author


def delete_author(db: Session, author_id: int):
    db_author = get_author(db, author_id=author_id)
    if db_author:
        db.delete(db_author)
        db.commit()
    return db_author


# ========== Article CRUD ==========
def create_article(db: Session, article: ArticleCreate, author_ids: List[int] = None):
    db_article = models.Article(
        title=article.title,
        content=article.content
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)

    if author_ids:
        for author_id in author_ids:
            add_author_to_article(db, article_id=db_article.article_id, author_id=author_id)

    return db_article


def get_article(db: Session, article_id: int):
    return db.query(models.Article).filter(models.Article.article_id == article_id).first()


def get_articles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Article).offset(skip).limit(limit).all()


def update_article(db: Session, article_id: int, article: ArticleUpdate):
    db_article = get_article(db, article_id=article_id)
    if db_article:
        for var, value in vars(article).items():
            if value is not None:
                setattr(db_article, var, value)
        db_article.updated_at = datetime.now()
        db.commit()
        db.refresh(db_article)
    return db_article


def delete_article(db: Session, article_id: int):
    db_article = get_article(db, article_id=article_id)
    if db_article:
        db.delete(db_article)
        db.commit()
    return db_article


# ========== Article-Author M2M CRUD ==========
def add_author_to_article(db: Session, article_id: int, author_id: int):
    article = get_article(db, article_id=article_id)
    author = get_author(db, author_id=author_id)
    if article and author:
        article.authors.append(author)
        db.commit()
        db.refresh(article)
    return article


def remove_author_from_article(db: Session, article_id: int, author_id: int):
    article = get_article(db, article_id=article_id)
    author = get_author(db, author_id=author_id)
    if article and author and author in article.authors:
        article.authors.remove(author)
        db.commit()
        db.refresh(article)
    return article


# ========== Favorites CRUD ==========
def create_favorites(db: Session, user_id: int):
    db_favorites = models.Favorites(user_id=user_id)
    db.add(db_favorites)
    db.commit()
    db.refresh(db_favorites)
    return db_favorites


def get_favorites(db: Session, user_id: int):
    return db.query(models.Favorites).filter(models.Favorites.user_id == user_id).first()


def add_article_to_favorites(db: Session, user_id: int, article_id: int):
    favorites = get_favorites(db, user_id=user_id)
    article = get_article(db, article_id=article_id)
    if favorites and article:
        favorites.articles.append(article)
        db.commit()
        db.refresh(favorites)
    return favorites


def remove_article_from_favorites(db: Session, user_id: int, article_id: int):
    favorites = get_favorites(db, user_id=user_id)
    article = get_article(db, article_id=article_id)
    if favorites and article and article in favorites.articles:
        favorites.articles.remove(article)
        db.commit()
        db.refresh(favorites)
    return favorites


def get_user_favorites(db: Session, user_id: int):
    favorites = get_favorites(db, user_id=user_id)
    return favorites.articles if favorites else []


# ========== ArticleVector CRUD ==========
def create_article_vector(db: Session, article_id: int, vector_data: bytes):
    db_vector = models.ArticleVector(
        article_id=article_id,
        vector_data=vector_data
    )
    db.add(db_vector)
    db.commit()
    db.refresh(db_vector)
    return db_vector


def get_article_vector(db: Session, article_id: int):
    return db.query(models.ArticleVector).filter(models.ArticleVector.article_id == article_id).first()


def update_article_vector(db: Session, article_id: int, vector_data: bytes):
    db_vector = get_article_vector(db, article_id=article_id)
    if db_vector:
        db_vector.vector_data = vector_data
        db.commit()
        db.refresh(db_vector)
    return db_vector


def delete_article_vector(db: Session, article_id: int):
    db_vector = get_article_vector(db, article_id=article_id)
    if db_vector:
        db.delete(db_vector)
        db.commit()
    return db_vector