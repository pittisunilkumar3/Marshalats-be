"""
Email service for sending emails using SMTP
"""

import smtplib
import ssl
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from .email_monitor import log_email_attempt, log_password_reset_attempt, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self._load_config()

    def _load_config(self):
        """Load SMTP configuration from environment variables"""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_pass = os.getenv('SMTP_PASS', '')
        self.smtp_from = os.getenv('SMTP_FROM', self.smtp_user)

        # Debug logging
        logger.info(f"Loading email config - Host: {self.smtp_host}, Port: {self.smtp_port}")
        logger.info(f"SMTP User: {self.smtp_user}, Has Password: {bool(self.smtp_pass)}")

        # Validate configuration
        if not self.smtp_user or not self.smtp_pass:
            logger.warning("SMTP credentials not configured. Email sending will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"Email service enabled with SMTP host: {self.smtp_host}:{self.smtp_port}")
            logger.info(f"SMTP user: {self.smtp_user}")

    def reload_config(self):
        """Reload configuration from environment variables"""
        self._load_config()

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send an email

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            from_email: Optional sender email (defaults to SMTP_FROM)

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Reload config in case environment variables changed
        if not self.enabled:
            self._load_config()

        if not self.enabled:
            logger.warning(f"Email service disabled. Would send email to {to_email}: {subject}")
            return False
            
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = from_email or self.smtp_from
            message["To"] = to_email
            
            # Add plain text part
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            # Handle different SMTP configurations
            if self.smtp_host == 'localhost' and self.smtp_port == 1025:
                # Mock SMTP server - no authentication needed
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.sendmail(self.smtp_from, to_email, message.as_string())
                logger.info(f"📧 Email sent via mock SMTP server")
            else:
                # Real SMTP server - use secure connection
                context = ssl.create_default_context()

                # Use SMTP_SSL for port 465, SMTP with STARTTLS for port 587
                if self.smtp_port == 465:
                    with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context) as server:
                        server.login(self.smtp_user, self.smtp_pass)
                        server.sendmail(self.smtp_from, to_email, message.as_string())
                else:
                    with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                        if self.smtp_port == 587:
                            server.starttls(context=context)
                        server.login(self.smtp_user, self.smtp_pass)
                        server.sendmail(self.smtp_from, to_email, message.as_string())
            
            logger.info(f"📧 Email sent successfully to {to_email}")
            logger.info(f"📊 Email details - Subject: {subject}, SMTP: {self.smtp_host}:{self.smtp_port}")

            # Log successful email attempt
            log_email_attempt("general", to_email, True)
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP Authentication failed for {to_email}: {str(e)}")
            logger.error(f"🔧 Check SMTP credentials: {self.smtp_user}")
            log_email_attempt("general", to_email, False, str(e))
            return False
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"❌ Recipient refused for {to_email}: {str(e)}")
            log_email_attempt("general", to_email, False, str(e))
            return False
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"❌ SMTP server disconnected for {to_email}: {str(e)}")
            log_email_attempt("general", to_email, False, str(e))
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error for {to_email}: {str(e)}")
            log_email_attempt("general", to_email, False, str(e))
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending email to {to_email}: {str(e)}")
            logger.error(f"🔧 Email config - Host: {self.smtp_host}:{self.smtp_port}, User: {self.smtp_user}")
            log_email_attempt("general", to_email, False, str(e))
            return False

    async def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str, user_exists: bool = True) -> bool:
        """
        Send password reset email with a formatted template

        Args:
            to_email: User's email address
            reset_token: Password reset token
            user_name: User's full name
            user_exists: Whether the user actually exists (for security notifications)

        Returns:
            bool: True if email was sent successfully
        """
        if user_exists:
            # User exists - send normal password reset email
            reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3022')}/reset-password?token={reset_token}"
            subject = "Password Reset Request - Martial Arts Academy"

            # Plain text version for existing user
            text_body = f"""
Hello {user_name},

You have requested to reset your password for your Martial Arts Academy account.

Please click on the following link to reset your password:
{reset_link}

This link will expire in 15 minutes for security reasons.

If you did not request this password reset, please ignore this email and your password will remain unchanged.

Best regards,
Martial Arts Academy Team
            """.strip()
        else:
            # User doesn't exist - send security notification
            subject = "Password Reset Request - Martial Arts Academy"

            # Plain text version for non-existent user
            text_body = f"""
Hello,

Someone requested a password reset for this email address at Martial Arts Academy.

However, we don't have an account associated with this email address.

If you have an account with us, please make sure you're using the correct email address. If you don't have an account and would like to create one, please visit our website.

If you did not request this, you can safely ignore this email.

Best regards,
Martial Arts Academy Team
            """.strip()
        
        # HTML version - different content based on user existence
        if user_exists:
            # HTML for existing user
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset Request</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #ffffff; padding: 30px; border: 1px solid #e9ecef; }}
        .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #6c757d; }}
        .btn {{ display: inline-block; padding: 12px 24px; background-color: #ffc107; color: #000; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
        .btn:hover {{ background-color: #e0a800; }}
        .warning {{ background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0; color: #333;">🥋 Martial Arts Academy</h1>
        </div>

        <div class="content">
            <h2>Password Reset Request</h2>
            <p>Hello <strong>{user_name}</strong>,</p>

            <p>You have requested to reset your password for your Martial Arts Academy account.</p>

            <p>Please click the button below to reset your password:</p>

            <div style="text-align: center;">
                <a href="{reset_link}" class="btn">Reset My Password</a>
            </div>

            <div class="warning">
                <strong>⚠️ Important:</strong> This link will expire in <strong>15 minutes</strong> for security reasons.
            </div>

            <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
            <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 4px;">
                {reset_link}
            </p>

            <p>If you did not request this password reset, please ignore this email and your password will remain unchanged.</p>
        </div>

        <div class="footer">
            <p>Best regards,<br>Martial Arts Academy Team</p>
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
        else:
            # HTML for non-existent user
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset Request</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #ffffff; padding: 30px; border: 1px solid #e9ecef; }}
        .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; font-size: 12px; color: #6c757d; }}
        .info {{ background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0; color: #333;">🥋 Martial Arts Academy</h1>
        </div>

        <div class="content">
            <h2>Password Reset Request</h2>
            <p>Hello,</p>

            <p>Someone requested a password reset for this email address at Martial Arts Academy.</p>

            <div class="info">
                <strong>ℹ️ Account Not Found:</strong> We don't have an account associated with this email address.
            </div>

            <p>If you have an account with us, please make sure you're using the correct email address. If you don't have an account and would like to create one, please visit our website.</p>

            <p>If you did not request this, you can safely ignore this email.</p>
        </div>

        <div class="footer">
            <p>Best regards,<br>Martial Arts Academy Team</p>
            <p>This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
            """.strip()
        
        result = await self.send_email(to_email, subject, text_body, html_body)

        # Log password reset attempt specifically
        log_password_reset_attempt(to_email, result)

        return result

# Global email service instance (lazy-loaded)
_email_service = None

def get_email_service() -> EmailService:
    """Get or create the global email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

# Convenience function for backward compatibility
async def send_email(to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
    """Send an email using the global email service"""
    service = get_email_service()
    return await service.send_email(to_email, subject, body, html_body)

async def send_password_reset_email(to_email: str, reset_token: str, user_name: str, user_exists: bool = True) -> bool:
    """Send password reset email using the global email service"""
    service = get_email_service()
    return await service.send_password_reset_email(to_email, reset_token, user_name, user_exists)
