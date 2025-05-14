from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional

from models.user import User
from repositories.abstract.user_repository_interface import IUserRepository

class UserRepository(IUserRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
        
    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).filter(User.googleId == google_id))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        try:
            self.db.add(user)
            # Explicitly commit the change to ensure data persistence
            # This is critical for operations like sync where we need to ensure
            # that each entity is saved before proceeding to dependent entities
            await self.db.flush()
            await self.db.commit()  # Explicitly commit the transaction
            await self.db.refresh(user)
            return user
        except Exception as e:
            # Log the error and rollback before re-raising
            import logging
            logging.error(f"Error in user repository create: {str(e)}")
            await self.db.rollback()  # Explicitly rollback on error
            raise

    async def update(self, user: User) -> User:
        try:
            # The commit is now handled by the database provider in the get_db function
            await self.db.flush()
            await self.db.refresh(user)
            return user
        except Exception as e:
            import logging
            logging.error(f"Error in user repository update: {str(e)}")
            raise

    async def delete(self, user_id: int) -> bool:
        try:
            user = await self.get_by_id(user_id)
            if user:
                await self.db.delete(user)
                # The commit is now handled by the database provider in the get_db function
                await self.db.flush()
                return True
            return False
        except Exception as e:
            import logging
            logging.error(f"Error in user repository delete: {str(e)}")
            raise
        
    async def delete_all(self) -> int:
        """Delete all users from the database.
        
        Returns:
            int: The number of users deleted
        """
        # Get count first
        result = await self.db.execute(select(User))
        users = result.scalars().all()
        count = len(users)
        
        # Delete all users
        await self.db.execute(delete(User))
        await self.db.commit()
        return count
        
    async def find_by_filters(self, filters: dict) -> List[User]:
        """Find users by specified filters.
        
        Args:
            filters (dict): Dictionary of field-value pairs to filter by
            
        Returns:
            List[User]: List of matching users
        """
        try:
            from sqlalchemy import func
            
            # Start with a basic query
            query = select(User)
            
            # Text fields that should use case-insensitive search
            text_fields = ["firstName", "lastName", "email"]
            
            # Add filter conditions dynamically based on provided filters
            for field, value in filters.items():
                # Make sure the attribute exists on the User model
                if hasattr(User, field):
                    if field in text_fields and value is not None:
                        # Use case-insensitive search for text fields
                        # This works for PostgreSQL which is your database
                        query = query.filter(func.lower(getattr(User, field)) == func.lower(value))
                    else:
                        # Use exact match for non-text fields or when value is None
                        query = query.filter(getattr(User, field) == value)
            
            # Execute the query
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            import logging
            logging.error(f"Error in user repository find_by_filters: {str(e)}")
            raise