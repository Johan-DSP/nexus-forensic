from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    """Busca por email o username (case-insensitive en username)."""
    return (
        db.query(User)
        .filter(
            (User.email == identifier)
            | (User.username == identifier.lower())
        )
        .first()
    )


def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user_in: UserCreate, is_superuser: bool = False) -> User:
    db_user = User(
        email=user_in.email,
        username=user_in.username.lower(),
        full_name=user_in.full_name,
        hashed_password=hash_password(user_in.password),
        is_active=True,
        is_superuser=is_superuser,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
