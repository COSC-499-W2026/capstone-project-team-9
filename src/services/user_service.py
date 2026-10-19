from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from src.schemas.user_schema import UserCreate

def register_user(db: Session, user_data: UserCreate) -> dict:
    existing_user = db.exec(
        text(
            """
            SELECT id
            FROM user
            WHERE name = :name OR email = :email
            LIMIT 1
            """
        ),
        params={
            "name": user_data.name,
            "email": str(user_data.email),
        },
    ).first()
    if existing_user:
        raise ValueError("Name or email is already registered")
    
    try:
        result = db.exec(
            text(
                """
                INSER INTO User (name, email)
                VALUES (:name, :email)
                RETURNING id, name, email
                """
            ),
            parms={
                "name": user_data.name,
                "email": str(user_data.email),
            },
        )
        created_user = result.mappings().one()
        db.commit()
        
        return dict(created_user)
    
    except IntegrityError:
        db.rollback()
        raise ValueError("Name or email is already registered")