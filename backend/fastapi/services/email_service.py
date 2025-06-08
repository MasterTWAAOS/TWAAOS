import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Personalization
from python_http_client.exceptions import HTTPError
from fastapi import HTTPException

from services.abstract.email_service_interface import IEmailService
from services.abstract.user_service_interface import IUserService
from models.user import UserRole

logger = logging.getLogger(__name__)

class EmailService(IEmailService):
    """SendGrid implementation of the email service interface."""
    
    def __init__(self, user_service: IUserService):
        """Initialize the email service.
        
        Args:
            user_service: User service for retrieving user email addresses
        """
        self.user_service = user_service
        self.api_key = os.environ.get("SENDGRID_API_KEY")
        self.from_email = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@twaaos.ro")
        self.sg_client = None
        
        if not self.api_key:
            logger.warning("SENDGRID_API_KEY environment variable not set. Email functionality will be limited.")
        else:
            try:
                self.sg_client = SendGridAPIClient(self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize SendGrid client: {e}")
    
    async def send_email(self, to_email: str, subject: str, content: str) -> bool:
        """Send an email to a single recipient using SendGrid.
        
        Args:
            to_email: The recipient's email address
            subject: Email subject
            content: Email content (HTML formatted)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.sg_client:
            logger.warning("SendGrid client not initialized. Email not sent.")
            return False
            
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=content
            )
            
            response = self.sg_client.send(message)
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email. Status code: {response.status_code}")
                return False
                
        except HTTPError as e:
            logger.error(f"SendGrid API error: {e.body}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False
    
    async def send_bulk_email(self, to_emails: List[str], subject: str, content: str) -> Dict[str, bool]:
        """Send emails to multiple recipients using SendGrid.
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            content: Email content (HTML formatted)
            
        Returns:
            Dict[str, bool]: Dictionary with email addresses as keys and success status as values
        """
        results = {}
        
        for email in to_emails:
            success = await self.send_email(email, subject, content)
            results[email] = success
        
        return results
    
    async def send_exam_period_notification(self, to_emails: List[str], start_date: str, end_date: str) -> Dict[str, bool]:
        """Send a notification about new exam period to multiple recipients.
        
        Args:
            to_emails: List of recipient email addresses
            start_date: Start date of the exam period (formatted string)
            end_date: End date of the exam period (formatted string)
            
        Returns:
            Dict[str, bool]: Dictionary with email addresses as keys and success status as values
        """
        subject = "Notificare: S-a configurat perioada de examene"
        
        # Create Romanian notification content
        html_content = f"""
        <html>
            <body>
                <h2>Notificare: S-a configurat perioada de examene</h2>
                <p>Bună ziua,</p>
                <p>Vă informăm că perioada de examene a fost configurată în aplicația TWAAOS:</p>
                <ul>
                    <li><strong>Data de început:</strong> {start_date}</li>
                    <li><strong>Data de sfârșit:</strong> {end_date}</li>
                </ul>
                <p>Puteți acum să selectați datele când doriți să programați examenele dumneavoastră.</p>
                <p>Vă rugăm să vă autentificați în aplicație pentru a accesa funcționalitățile de programare a examenelor.</p>
                <p>Acesta este un mesaj automat. Vă rugăm să nu răspundeți la acest email.</p>
                <p>Cu stimă,<br>Sistemul TWAAOS</p>
            </body>
        </html>
        """
        
        return await self.send_bulk_email(to_emails, subject, html_content)
    
    async def notify_sg_users_about_new_exam_period(self, start_date: str, end_date: str) -> Dict[str, bool]:
        """Send notification to all Study Group (SG) users about new exam period.
        
        Args:
            start_date: Start date of the exam period (formatted string)
            end_date: End date of the exam period (formatted string)
            
        Returns:
            Dict[str, bool]: Dictionary with email addresses as keys and success status as values
        """
        # Get all SG users
        sg_users = await self.user_service.get_users_by_role(UserRole.SG)
        
        if not sg_users:
            logger.warning("No SG users found to notify about exam period")
            return {}
        
        # Extract email addresses
        sg_emails = [user.email for user in sg_users if user.email]
        
        if not sg_emails:
            logger.warning("No valid email addresses found for SG users")
            return {}
        
        # Send notifications
        return await self.send_exam_period_notification(sg_emails, start_date, end_date)
