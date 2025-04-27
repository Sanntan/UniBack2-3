from sqlalchemy.orm import Session
from database.models import ArticleVector

def create_article_vector(db: Session, article_id: int, vector_data):
    vector = ArticleVector(article_id=article_id, vector_data=vector_data)
    db.add(vector)
    db.commit()
    db.refresh(vector)
    return vector

def update_article_vector(db: Session, article_id: int, vector_data):
    vector = db.query(ArticleVector).filter(ArticleVector.article_id == article_id).first()
    if vector:
        vector.vector_data = vector_data
        db.commit()
        db.refresh(vector)
    return vector
