from sqlalchemy.orm import Session
from database.models import Article

def create_article(db: Session, title: str, authors: str = None, content: str = None, article_url: str = None):
    article = Article(title=title, authors=authors, content=content, article_url=article_url)
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

def get_article(db: Session, article_id: int):
    return db.query(Article).filter(Article.article_id == article_id).first()

def update_article(db: Session, article_id: int, title: str = None, authors: str = None, content: str = None, article_url: str = None):
    article = get_article(db, article_id)
    if article:
        if title:
            article.title = title
        if authors:
            article.authors = authors
        if content:
            article.content = content
        if article_url:
            article.article_url = article_url
        db.commit()
        db.refresh(article)
    return article

def delete_article(db: Session, article_id: int):
    article = get_article(db, article_id)
    if article:
        db.delete(article)
        db.commit()
    return article
