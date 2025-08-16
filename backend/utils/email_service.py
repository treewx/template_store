from flask_mail import Mail, Message
from flask import current_app, url_for
import os

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app"""
    mail.init_app(app)

def send_verification_email(user_email, verification_token):
    """Send email verification link"""
    try:
        # In production, this would be your actual domain
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
        verification_url = f"{frontend_url}/verify-email?token={verification_token}"
        
        msg = Message(
            subject='Verify Your Email - Rent Check',
            sender=current_app.config.get('MAIL_USERNAME'),
            recipients=[user_email]
        )
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">Welcome to Rent Check!</h2>
            <p>Thank you for registering. Please verify your email address to complete your account setup.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #3498db; color: white; padding: 15px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Verify Email Address
                </a>
            </div>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #7f8c8d;">{verification_url}</p>
            <p style="color: #7f8c8d; font-size: 14px;">
                This link will expire in 24 hours. If you didn't create an account, please ignore this email.
            </p>
        </div>
        """
        
        msg.body = f"""
        Welcome to Rent Check!
        
        Thank you for registering. Please verify your email address by clicking the link below:
        
        {verification_url}
        
        This link will expire in 24 hours. If you didn't create an account, please ignore this email.
        """
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False

def send_password_reset_email(user_email, reset_token):
    """Send password reset link"""
    try:
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        msg = Message(
            subject='Password Reset - Rent Check',
            sender=current_app.config.get('MAIL_USERNAME'),
            recipients=[user_email]
        )
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">Password Reset Request</h2>
            <p>You requested a password reset for your Rent Check account.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #e74c3c; color: white; padding: 15px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </div>
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #7f8c8d;">{reset_url}</p>
            <p style="color: #7f8c8d; font-size: 14px;">
                This link will expire in 1 hour. If you didn't request a password reset, please ignore this email.
            </p>
        </div>
        """
        
        msg.body = f"""
        Password Reset Request
        
        You requested a password reset for your Rent Check account.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 1 hour. If you didn't request a password reset, please ignore this email.
        """
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False

def send_welcome_email(user_email):
    """Send welcome email after verification"""
    try:
        msg = Message(
            subject='Welcome to Rent Check!',
            sender=current_app.config.get('MAIL_USERNAME'),
            recipients=[user_email]
        )
        
        frontend_url = current_app.config.get('FRONTEND_URL', 'http://localhost:3000')
        
        msg.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #2c3e50;">🏠 Welcome to Rent Check!</h2>
            <p>Your email has been verified successfully. You can now:</p>
            <ul>
                <li>Add your rental properties</li>
                <li>Connect your bank account via Akahu</li>
                <li>Set up automated rent monitoring</li>
                <li>Receive email alerts for missed payments</li>
            </ul>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{frontend_url}" 
                   style="background-color: #27ae60; color: white; padding: 15px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Get Started
                </a>
            </div>
            <p style="color: #7f8c8d;">
                Built specifically for New Zealand landlords to make rent tracking simple and reliable.
            </p>
        </div>
        """
        
        msg.body = f"""
        Welcome to Rent Check!
        
        Your email has been verified successfully. You can now:
        
        - Add your rental properties
        - Connect your bank account via Akahu  
        - Set up automated rent monitoring
        - Receive email alerts for missed payments
        
        Get started at: {frontend_url}
        
        Built specifically for New Zealand landlords to make rent tracking simple and reliable.
        """
        
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False