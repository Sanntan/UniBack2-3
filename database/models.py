from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Table, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.config import Base
from sqlalchemy.schema import PrimaryKeyConstraint

# Промежуточные таблицы для связей M:N
article_author = Table(
    'article_author',
    Base.metadata,
    Column('article_id', Integer, ForeignKey('article.article_id', ondelete="CASCADE")),
    Column('author_id', Integer, ForeignKey('author.author_id', ondelete="CASCADE")),
    PrimaryKeyConstraint('article_id', 'author_id')
)

favorite_articles = Table(
    'favorite_articles',
    Base.metadata,
    Column('favorites_id', Integer, ForeignKey('favorites.favorites_id', ondelete="CASCADE")),
    Column('article_id', Integer, ForeignKey('article.article_id', ondelete="CASCADE")),
    Column('added_at', TIMESTAMP, server_default=func.now()),
    PrimaryKeyConstraint('favorites_id', 'article_id')
)


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    settings = relationship("InterfaceSettings", back_populates="user", uselist=False)
    favorites = relationship("Favorites", back_populates="user", uselist=False)


class InterfaceSettings(Base):
    __tablename__ = "interface_settings"

    settings_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), unique=True)
    theme = Column(String(20), nullable=False)
    font_size = Column(Integer)
    language = Column(String(10), default="en")

    user = relationship("User", back_populates="settings")


class Author(Base):
    __tablename__ = "author"

    author_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    bio = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    articles = relationship("Article", secondary=article_author, back_populates="authors")


class Article(Base):
    __tablename__ = "article"

    article_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    authors = relationship("Author", secondary=article_author, back_populates="articles")
    vector = relationship("ArticleVector", back_populates="article", uselist=False)
    in_favorites = relationship("Favorites", secondary=favorite_articles, back_populates="articles")


class ArticleVector(Base):
    __tablename__ = "article_vector"

    vector_id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("article.article_id", ondelete="CASCADE"), unique=True)
    vector_data = Column(LargeBinary)  # Теперь LargeBinary определен

    article = relationship("Article", back_populates="vector")


class Favorites(Base):
    __tablename__ = "favorites"

    favorites_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), unique=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="favorites")
    articles = relationship("Article", secondary=favorite_articles, back_populates="in_favorites")