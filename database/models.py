from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    settings = relationship("InterfaceSettings", back_populates="user", uselist=False)
    favorites = relationship("Favorites", back_populates="user", uselist=False)


class InterfaceSettings(Base):
    __tablename__ = 'interface_settings'

    settings_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), unique=True)
    theme = Column(String(50), nullable=False)

    user = relationship("User", back_populates="settings")


class Favorites(Base):
    __tablename__ = 'favorites'

    favorites_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'), unique=True)

    user = relationship("User", back_populates="favorites")
    articles = relationship("Article", secondary="favorites_articles", back_populates="in_favorites")


class Article(Base):
    __tablename__ = 'article'

    article_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    authors = Column(Text)
    content = Column(Text)
    article_url = Column(String(512))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    in_favorites = relationship("Favorites", secondary="favorites_articles", back_populates="articles")
    vector = relationship("ArticleVector", back_populates="article", uselist=False)


class FavoritesArticles(Base):
    __tablename__ = 'favorites_articles'

    favorites_id = Column(Integer, ForeignKey('favorites.favorites_id'), primary_key=True)
    article_id = Column(Integer, ForeignKey('article.article_id'), primary_key=True)
    added_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class ArticleVector(Base):
    __tablename__ = 'article_vector'

    vector_id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('article.article_id'), unique=True)
    vector_data = Column(ARRAY(Float))  # Для pgvector

    article = relationship("Article", back_populates="vector")