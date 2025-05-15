# Import the shared Base and its metadata
from models.base import Base

# Import all models to be included in migrations
from models.user import User
from models.group import Group
from models.subject import Subject
from models.room import Room
from models.schedule import Schedule
from models.notification import Notification
from models.excel_template import ExcelTemplate
from models.config import Config

# Export the base and metadata for Alembic to use
__all__ = ['Base', 'User', 'Group', 'Subject', 'Room', 'Schedule', 'Notification', 'ExcelTemplate', 'Config']
metadata = Base.metadata
