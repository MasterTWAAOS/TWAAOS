from sqlalchemy.orm import Session
from typing import List, Optional

from models.user import User
from repositories.abstract.user_repository_interface import IUserRepository

class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[User]:
        return self.db.query(User).all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
        
    def get_by_google_id(self, google_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.googleId == google_id).first()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
        
    def delete_all(self) -> int:
        """Delete all users from the database.
        
        Returns:
            int: The number of users deleted
        """
        count = self.db.query(User).count()
        self.db.query(User).delete()
        self.db.commit()
        return count