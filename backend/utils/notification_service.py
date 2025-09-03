from datetime import datetime
from models.user import User
from utils.email_service import mail
from flask_mail import Message
from flask import current_app
try:
    from database import get_db_connection
except ImportError:
    from database_sqlite import get_db_connection

class NotificationService:
    @staticmethod
    def log_notification(user_id, property_id, notification_type, message):
        """Log notification to database"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO notification_log (user_id, property_id, notification_type, message, date_sent)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, property_id, notification_type, message, datetime.now()))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error logging notification: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    @staticmethod
    def send_rent_overdue_email(user, property_data):
        """Send email notification for overdue rent"""
        try:
            subject = f"Rent Overdue - {property_data['property_name']}"
            
            msg = Message(
                subject=subject,
                sender=current_app.config.get('MAIL_USERNAME'),
                recipients=[user.email]
            )
            
            days_overdue = property_data.get('days_overdue', 1)
            expected_amount = property_data.get('expected_amount', 0)
            expected_date = property_data.get('expected_date')
            
            msg.html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #e74c3c;">⚠️ Rent Payment Overdue</h2>
                <div style="background-color: #ffe6e6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">Property: {property_data['property_name']}</h3>
                    <p><strong>Expected Amount:</strong> ${expected_amount}</p>
                    <p><strong>Expected Date:</strong> {expected_date}</p>
                    <p><strong>Days Overdue:</strong> {days_overdue} day(s)</p>
                </div>
                
                <p>No rent payment has been detected for the above property. Please check:</p>
                <ul>
                    <li>Bank account transactions</li>
                    <li>Payment method used by tenant</li>
                    <li>Contact tenant if necessary</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}" 
                       style="background-color: #3498db; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Dashboard
                    </a>
                </div>
                
                <p style="color: #7f8c8d; font-size: 14px;">
                    This alert was generated automatically by Rent Check. 
                    If you believe this is an error, please check your bank account connection.
                </p>
            </div>
            """
            
            msg.body = f"""
            Rent Payment Overdue - {property_data['property_name']}
            
            Expected Amount: ${expected_amount}
            Expected Date: {expected_date}
            Days Overdue: {days_overdue} day(s)
            
            No rent payment has been detected for this property. Please check:
            - Bank account transactions
            - Payment method used by tenant
            - Contact tenant if necessary
            
            View your dashboard at: {current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}
            
            This alert was generated automatically by Rent Check.
            """
            
            mail.send(msg)
            
            # Log the notification
            NotificationService.log_notification(
                user.id, 
                property_data['property_id'], 
                'rent_overdue', 
                f"Rent overdue notification sent for {property_data['property_name']}"
            )
            
            return True
            
        except Exception as e:
            print(f"Error sending rent overdue email: {e}")
            return False
    
    @staticmethod
    def send_daily_summary_email(user, overdue_properties, recent_payments):
        """Send daily summary email with rent status"""
        try:
            if not overdue_properties and not recent_payments:
                return True  # No need to send empty summary
            
            subject = "Daily Rent Summary - Rent Check"
            
            msg = Message(
                subject=subject,
                sender=current_app.config.get('MAIL_USERNAME'),
                recipients=[user.email]
            )
            
            overdue_html = ""
            if overdue_properties:
                overdue_html = """
                <div style="background-color: #ffe6e6; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h3 style="color: #e74c3c; margin-top: 0;">⚠️ Overdue Payments</h3>
                """ + "".join([
                    f"<p>• {prop['property_name']} - ${prop['expected_amount']} ({prop['days_overdue']} days overdue)</p>"
                    for prop in overdue_properties
                ]) + "</div>"
            
            payments_html = ""
            if recent_payments:
                payments_html = """
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h3 style="color: #27ae60; margin-top: 0;">✅ Recent Payments</h3>
                """ + "".join([
                    f"<p>• {payment['property_name']} - ${payment['amount']} received</p>"
                    for payment in recent_payments
                ]) + "</div>"
            
            msg.html = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2c3e50;">🏠 Daily Rent Summary</h2>
                <p>Here's your rent status update for {datetime.now().strftime('%B %d, %Y')}:</p>
                
                {overdue_html}
                {payments_html}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}" 
                       style="background-color: #3498db; color: white; padding: 15px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Full Dashboard
                    </a>
                </div>
                
                <p style="color: #7f8c8d; font-size: 14px;">
                    Rent Check - Making rent tracking simple for NZ landlords
                </p>
            </div>
            """
            
            mail.send(msg)
            
            # Log the notification
            NotificationService.log_notification(
                user.id, 
                None, 
                'daily_summary', 
                f"Daily summary sent - {len(overdue_properties)} overdue, {len(recent_payments)} recent payments"
            )
            
            return True
            
        except Exception as e:
            print(f"Error sending daily summary email: {e}")
            return False