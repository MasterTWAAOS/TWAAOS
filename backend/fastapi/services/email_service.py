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
        logger.info(f"[DEBUG] EmailService - Attempting to send email to: {to_email}, Subject: {subject}")
        
        # Check API key and client setup
        if not self.api_key:
            logger.error("[DEBUG] EmailService - SendGrid API key not configured. Check SENDGRID_API_KEY environment variable.")
            return False
            
        if not self.sg_client:
            logger.error("[DEBUG] EmailService - SendGrid client not initialized. Email not sent.")
            return False
            
        # Validate recipient email
        if not to_email or '@' not in to_email:
            logger.error(f"[DEBUG] EmailService - Invalid recipient email: {to_email}")
            return False
            
        message = Mail(
            from_email=Email(self.from_email),
            to_emails=To(to_email),
            subject=subject,
            html_content=Content("text/html", content)
        )
        
        try:
            logger.info(f"[DEBUG] EmailService - Sending email via SendGrid: From={self.from_email}, To={to_email}")
            response = self.sg_client.send(message=message)
            
            if response.status_code == 202:
                logger.info(f"[DEBUG] EmailService - Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"[DEBUG] EmailService - Failed to send email to {to_email}. Status code: {response.status_code}")
                return False
        except HTTPError as e:
            logger.error(f"[DEBUG] EmailService - SendGrid HTTP error: {e.to_dict}")
            return False
        except Exception as e:
            logger.error(f"[DEBUG] EmailService - Error sending email: {str(e)}")
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
        subject = "Notificare: Propunere nouă de programare examen"
        
        # Create Romanian notification content
        html_content = f"""
        <html>
            <body>
                <h2>O nouă propunere de examen a fost trimisă pentru aprobarea dumneavoastră</h2>
                <p>Detalii despre propunere:</p>
                <ul>
                    <li><strong>Disciplina:</strong> {subject_name}</li>
                    <li><strong>Grupa:</strong> {group_name}</li>
                    <li><strong>Data propusă:</strong> {date}</li>
                </ul>
                <p>Puteți accesa aplicația pentru a aproba sau respinge această propunere.</p>
                <p>Acesta este un mesaj automat. Vă rugăm să nu răspundeți la acest email.</p>
                <p>Cu stimă,<br>Sistemul TWAAOS</p>
            </body>
        </html>
        """
        
        return await self.send_email(teacher_email, subject, html_content)
