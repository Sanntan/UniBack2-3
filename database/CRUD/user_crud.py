from sqlalchemy.orm import Session
from database.models import User

def create_user(db: Session, name: str, email: str):
    user = User(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()

def update_user(db: Session, user_id: int, name: str = None, email: str = None):
    user = get_user(db, user_id)
    if user:
        if name:
            user.name = name
        if email:
            user.email = email
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
    return user
