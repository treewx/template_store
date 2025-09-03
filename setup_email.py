#!/usr/bin/env python3
"""
Email Setup Helper for Rent Check Application

This script helps you configure email settings for rent notifications.
"""

import os
import getpass
from pathlib import Path

def setup_email_config():
    """Interactive email configuration setup"""
    print("🏠 RENT CHECK - EMAIL CONFIGURATION SETUP")
    print("=" * 50)
    print("\nThis will help you configure email notifications for rent alerts.")
    print("You'll need an email account that supports SMTP (like Gmail).")
    print("\nFor Gmail, you'll need an 'App Password' (not your regular password):")
    print("1. Enable 2-factor authentication on your Gmail account")
    print("2. Go to Google Account settings > Security > App passwords")
    print("3. Generate an app password for this application")
    print()
    
    # Get email configuration
    email = input("Enter your email address: ").strip()
    if not email or '@' not in email:
        print("❌ Invalid email address")
        return False
    
    password = getpass.getpass("Enter your app password (hidden): ").strip()
    if not password:
        print("❌ Password cannot be empty")
        return False
    
    # SMTP server selection
    print("\nSelect your email provider:")
    print("1. Gmail (gmail.com)")
    print("2. Outlook (outlook.com)")
    print("3. Custom SMTP server")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
    elif choice == "2":
        smtp_server = "smtp-mail.outlook.com"
        smtp_port = 587
    elif choice == "3":
        smtp_server = input("Enter SMTP server: ").strip()
        smtp_port = int(input("Enter SMTP port (usually 587): ").strip() or 587)
    else:
        print("❌ Invalid choice")
        return False
    
    # Update .env file
    env_path = Path(__file__).parent / '.env'
    
    # Read existing .env content
    env_content = ""
    if env_path.exists():
        with open(env_path, 'r') as f:
            env_content = f.read()
    
    # Update email settings
    email_config = f"""
# Email Configuration (Updated by setup_email.py)
MAIL_SERVER={smtp_server}
MAIL_PORT={smtp_port}
MAIL_USE_TLS=true
MAIL_USERNAME={email}
MAIL_PASSWORD={password}
"""
    
    # Check if email config already exists
    if 'MAIL_USERNAME=' in env_content:
        # Replace existing email configuration
        lines = env_content.split('\n')
        new_lines = []
        skip_next = False
        
        for line in lines:
            if line.startswith('MAIL_'):
                skip_next = True
                continue
            if skip_next and line.strip() == '':
                continue
            skip_next = False
            new_lines.append(line)
        
        env_content = '\n'.join(new_lines) + email_config
    else:
        # Add email configuration
        env_content += email_config
    
    # Write updated .env file
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("\n✅ Email configuration saved to .env file!")
    print(f"   Email: {email}")
    print(f"   SMTP Server: {smtp_server}:{smtp_port}")
    print("\n🔄 Restart the application to apply email settings.")
    print("📧 Test email functionality at: http://localhost:5000/api/test/email")
    
    return True

def show_email_providers_help():
    """Show help for different email providers"""
    print("\n📧 EMAIL PROVIDER SETUP GUIDES:")
    print("=" * 40)
    
    print("\n🔸 GMAIL:")
    print("1. Enable 2-factor authentication")
    print("2. Go to: Google Account > Security > App passwords")
    print("3. Generate app password for 'Mail'")
    print("4. Use the 16-character app password (not your Gmail password)")
    
    print("\n🔸 OUTLOOK/HOTMAIL:")
    print("1. Enable 2-factor authentication")
    print("2. Go to: Microsoft Account > Security > App passwords")
    print("3. Generate app password")
    
    print("\n🔸 OTHER PROVIDERS:")
    print("- Check your email provider's SMTP settings")
    print("- Common ports: 587 (TLS), 465 (SSL), 25 (unsecured)")
    print("- Most providers require app passwords for security")

if __name__ == "__main__":
    try:
        print("Choose an option:")
        print("1. Configure email settings")
        print("2. Show email provider help")
        
        choice = input("\nEnter choice (1-2): ").strip()
        
        if choice == "1":
            setup_email_config()
        elif choice == "2":
            show_email_providers_help()
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")