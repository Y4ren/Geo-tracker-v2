from sqlalchemy.orm import Session
from app.db.models.users import User
from app.schemas.users import UserAdd

def add_user(db: Session, user: UserAdd):
    db_user = User(
        id=user.id,
        username=user.username,
        country_code=user.country_code,
        rating=user.rating,
        avatar_url=user.avatar_url,
        pin_url=user.pin_url,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user