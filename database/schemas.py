from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ========== User Schemas ==========
class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class User(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# ========== Article Schemas ==========
class ArticleBase(BaseModel):
    title: str
    authors: str | None = None
    content: str | None = None
    article_url: str | None = None


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class Article(ArticleBase):
    article_id: int
    created_at: datetime
    updated_at: datetime
    authors: List['Author'] = []

    class Config:
        orm_mode = True


# ========== Author Schemas ==========
class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None


class Author(AuthorBase):
    author_id: int
    created_at: datetime
    articles: List[Article] = []

    class Config:
        orm_mode = True


# Обновляем ссылки для корректной работы моделей
Article.update_forward_refs()