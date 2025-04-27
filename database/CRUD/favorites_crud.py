from sqlalchemy.orm import Session
from database.models import Favorites, FavoritesArticles, Article

def create_favorites(db: Session, user_id: int):
    favorites = Favorites(user_id=user_id)
    db.add(favorites)
    db.commit()
    db.refresh(favorites)
    return favorites

def add_article_to_favorites(db: Session, favorites_id: int, article_id: int):
    link = FavoritesArticles(favorites_id=favorites_id, article_id=article_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link

def remove_article_from_favorites(db: Session, favorites_id: int, article_id: int):
    link = db.query(FavoritesArticles).filter_by(favorites_id=favorites_id, article_id=article_id).first()
    if link:
        db.delete(link)
        db.commit()
    return link
