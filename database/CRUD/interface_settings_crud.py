from sqlalchemy.orm import Session
from database.models import InterfaceSettings

def create_interface_settings(db: Session, user_id: int, theme: str = "light"):
    settings = InterfaceSettings(user_id=user_id, theme=theme)
    db.add(settings)
    db.commit()
    db.refresh(settings)
    return settings

def update_interface_settings(db: Session, user_id: int, theme: str = None):
    settings = db.query(InterfaceSettings).filter(InterfaceSettings.user_id == user_id).first()
    if settings and theme:
        settings.theme = theme
        db.commit()
        db.refresh(settings)
    return settings
