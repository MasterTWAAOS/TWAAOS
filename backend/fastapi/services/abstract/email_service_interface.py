from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IEmailService(ABC):
    """Interface for email services."""
    
    @abstractmethod
    async def send_email(self, to_email: str, subject: str, content: str) -> bool:
        """Send an email to a single recipient.
        
        Args:
            to_email: The recipient's email address
            subject: Email subject
            content: Email content (HTML formatted)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def send_bulk_email(self, to_emails: List[str], subject: str, content: str) -> Dict[str, bool]:
        """Send emails to multiple recipients.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            content: Email content (HTML formatted)
            
        Returns:
            Dict[str, bool]: Dictionary with email addresses as keys and success status as values
        """
        pass

    @abstractmethod
    async def send_exam_period_notification(self, to_emails: List[str], start_date: str, end_date: str) -> Dict[str, bool]:
        """Send a notification about new exam period to multiple recipients.
        
        Args:
            to_emails: List of recipient email addresses
            start_date: Start date of the exam period (formatted string)
            end_date: End date of the exam period (formatted string)
            
        Returns:
            Dict[str, bool]: Dictionary with email addresses as keys and success status as values
        """
        pass
        
    @abstractmethod
    async def notify_sg_users_about_new_exam_period(self, start_date: str, end_date: str) -> Dict[str, bool]:
        """Send notification to all Study Group (SG) users about new exam period.
        
        Args:
            start_date: Start date of the exam period (formatted string)
            end_date: End date of the exam period (formatted string)
            
        Returns:
            Dict[str, bool]: Dictionary with email addresses as keys and success status as values
        """
        pass
        
    @abstractmethod
    async def send_exam_proposal_notification(self, teacher_email: str, subject_name: str, group_name: str, date: str) -> bool:
        """Send notification to a Course Director about a new exam date proposal.
        
        Args:
            teacher_email: The course director's email address
            subject_name: The name of the subject for which the exam is proposed
            group_name: The name of the student group proposing the exam date
            date: The proposed exam date (formatted string)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        pass
