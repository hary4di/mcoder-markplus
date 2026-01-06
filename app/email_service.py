"""
Email Service using Brevo (formerly SendinBlue) API
"""
import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from app.models import SystemSettings

class EmailService:
    """Email service for sending OTP and notifications via Brevo"""
    
    def __init__(self):
        """Initialize Brevo API client"""
        self.configuration = sib_api_v3_sdk.Configuration()
        self.api_key = SystemSettings.get_setting('brevo_api_key', os.getenv('BREVO_API_KEY', ''))
        self.sender_email = SystemSettings.get_setting('brevo_sender_email', 'msurvey@markplusinc.com')
        self.sender_name = SystemSettings.get_setting('brevo_sender_name', 'M-Coder Platform')
        
        if self.api_key:
            self.configuration.api_key['api-key'] = self.api_key
            self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(self.configuration))
        else:
            self.api_instance = None
    
    def send_otp_email(self, recipient_email, recipient_name, otp_code):
        """
        Send OTP code via email
        
        Args:
            recipient_email: Email address to send OTP
            recipient_name: Name of recipient
            otp_code: 6-digit OTP code
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.api_instance:
            return False, "Brevo API key not configured. Please contact administrator."
        
        try:
            # Create email sender
            sender = {"name": self.sender_name, "email": self.sender_email}
            
            # Create recipient
            to = [{"email": recipient_email, "name": recipient_name}]
            
            # Email subject
            subject = "Your Password Reset Code - M-Coder Platform"
            
            # HTML email body
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                             color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .otp-code {{ font-size: 32px; font-weight: bold; color: #667eea; 
                               text-align: center; background: white; padding: 20px; 
                               border-radius: 8px; letter-spacing: 8px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                    .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; 
                              padding: 12px; margin: 20px 0; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0;">M-Coder Platform</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">Password Reset Request</p>
                    </div>
                    <div class="content">
                        <h2>Hello, {recipient_name}!</h2>
                        <p>We received a request to reset your password. Use the verification code below to complete the process:</p>
                        
                        <div class="otp-code">{otp_code}</div>
                        
                        <div class="warning">
                            <strong>⚠️ Security Notice:</strong>
                            <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                                <li>This code will expire in <strong>10 minutes</strong></li>
                                <li>Never share this code with anyone</li>
                                <li>If you didn't request this, please ignore this email</li>
                            </ul>
                        </div>
                        
                        <p style="margin-top: 20px;">After entering the code, you'll be able to set a new password for your account.</p>
                        
                        <p>Best regards,<br><strong>M-Coder Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message from M-Coder Platform by MarkPlus Indonesia</p>
                        <p>&copy; 2025 MarkPlus Indonesia. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create SendSmtpEmail object
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to,
                sender=sender,
                subject=subject,
                html_content=html_content
            )
            
            # Send email
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            return True, f"OTP sent successfully to {recipient_email}"
            
        except ApiException as e:
            error_msg = f"Brevo API error: {str(e)}"
            print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            print(error_msg)
            return False, error_msg    
    def send_registration_otp(self, recipient_email, recipient_name, otp_code):
        """
        Send OTP code for email verification during registration
        
        Args:
            recipient_email: Email address to send OTP
            recipient_name: Name of recipient
            otp_code: 6-digit OTP code
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.api_instance:
            return False, "Brevo API key not configured. Please contact administrator."
        
        try:
            # Create email sender
            sender = {"name": self.sender_name, "email": self.sender_email}
            
            # Create recipient
            to = [{"email": recipient_email, "name": recipient_name}]
            
            # Email subject
            subject = "Verify Your Email - M-Code Pro"
            
            # HTML email body
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                             color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .otp-code {{ font-size: 32px; font-weight: bold; color: #667eea; 
                               text-align: center; background: white; padding: 20px; 
                               border-radius: 8px; letter-spacing: 8px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                    .info {{ background: #d1ecf1; border-left: 4px solid #0c5460; 
                           padding: 12px; margin: 20px 0; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0;">M-Code Pro</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">Email Verification</p>
                    </div>
                    <div class="content">
                        <h2>Welcome, {recipient_name}!</h2>
                        <p>Thank you for registering with M-Code Pro. To complete your registration, please verify your email address using the code below:</p>
                        
                        <div class="otp-code">{otp_code}</div>
                        
                        <div class="info">
                            <strong>ℹ️ Important:</strong>
                            <ul style="margin: 10px 0 0 0; padding-left: 20px;">
                                <li>This code will expire in <strong>15 minutes</strong></li>
                                <li>Enter this code on the verification page</li>
                                <li>If you didn't register, please ignore this email</li>
                            </ul>
                        </div>
                        
                        <p style="margin-top: 20px;">Once verified, you'll be able to access all features of M-Code Pro platform.</p>
                        
                        <p>Best regards,<br><strong>M-Code Pro Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message from M-Code Pro by MarkPlus Indonesia</p>
                        <p>&copy; 2025 MarkPlus Indonesia. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create SendSmtpEmail object
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to,
                sender=sender,
                subject=subject,
                html_content=html_content
            )
            
            # Send email
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            return True, f"Verification code sent successfully to {recipient_email}"
            
        except ApiException as e:
            error_msg = f"Brevo API error: {str(e)}"
            print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            return False, error_msg    
    def send_password_changed_notification(self, recipient_email, recipient_name):
        """
        Send notification that password was changed successfully
        
        Args:
            recipient_email: Email address
            recipient_name: Name of recipient
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.api_instance:
            return False, "Brevo API key not configured"
        
        try:
            sender = {"name": self.sender_name, "email": self.sender_email}
            to = [{"email": recipient_email, "name": recipient_name}]
            subject = "Password Changed Successfully - M-Coder Platform"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                             color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .success {{ background: #d4edda; border-left: 4px solid #28a745; 
                              padding: 12px; margin: 20px 0; border-radius: 4px; color: #155724; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0;">✓ Password Changed</h1>
                    </div>
                    <div class="content">
                        <h2>Hello, {recipient_name}!</h2>
                        
                        <div class="success">
                            <strong>✓ Success!</strong> Your password has been changed successfully.
                        </div>
                        
                        <p>Your M-Coder Platform account password was recently updated. You can now log in with your new password.</p>
                        
                        <p><strong>Didn't make this change?</strong><br>
                        If you did not change your password, please contact your administrator immediately.</p>
                        
                        <p>Best regards,<br><strong>M-Coder Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2025 MarkPlus Indonesia. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to,
                sender=sender,
                subject=subject,
                html_content=html_content
            )
            
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            return True, "Notification sent successfully"
            
        except Exception as e:
            print(f"Failed to send notification: {str(e)}")
            return False, str(e)
    
    def test_connection(self):
        """
        Test Brevo API connection
        
        Returns:
            tuple: (success: bool, message: str)
        """
        if not self.api_instance:
            return False, "API key not configured"
        
        try:
            # Try to get account info
            api_instance = sib_api_v3_sdk.AccountApi(sib_api_v3_sdk.ApiClient(self.configuration))
            account_info = api_instance.get_account()
            return True, f"Connected successfully. Account: {account_info.email}"
        except ApiException as e:
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

