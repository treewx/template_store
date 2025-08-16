from datetime import datetime, timedelta
from models.user import User
from models.property import Property
from utils.rent_checker import RentChecker
from utils.notification_service import NotificationService
from utils.akahu_service import AkahuService, MockAkahuService
import os

class RentScheduler:
    def __init__(self, use_mock_akahu=True):
        self.rent_checker = RentChecker()
        self.akahu_service = MockAkahuService() if use_mock_akahu else AkahuService()
    
    def run_daily_rent_check(self):
        """Run daily rent checking for all users"""
        print(f"Starting daily rent check at {datetime.now()}")
        
        # This would typically get all users from database
        # For now, we'll implement a basic version
        try:
            results = {
                'users_processed': 0,
                'properties_checked': 0,
                'overdue_found': 0,
                'notifications_sent': 0,
                'errors': []
            }
            
            # In a real implementation, you'd iterate through all users
            # For now, this is a framework for the daily job
            print(f"Daily rent check completed: {results}")
            return results
            
        except Exception as e:
            print(f"Error in daily rent check: {e}")
            return {'error': str(e)}
    
    def check_rent_for_user(self, user_id):
        """Check rent for a specific user and send notifications if needed"""
        try:
            user = User.get_by_id(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Check for overdue rent (1 day overdue)
            overdue_properties = self.rent_checker.get_overdue_rent(user_id, days_overdue=1)
            
            notifications_sent = 0
            
            # Send individual notifications for each overdue property
            for property_data in overdue_properties:
                success = NotificationService.send_rent_overdue_email(user, property_data)
                if success:
                    notifications_sent += 1
            
            return {
                'user_id': user_id,
                'properties_checked': len(Property.get_by_user_id(user_id)),
                'overdue_properties': len(overdue_properties),
                'notifications_sent': notifications_sent
            }
            
        except Exception as e:
            print(f"Error checking rent for user {user_id}: {e}")
            return {'error': str(e)}
    
    def sync_transactions_for_user(self, user_id, user_access_token):
        """Sync bank transactions for all user properties"""
        try:
            properties = Property.get_by_user_id(user_id)
            results = []
            
            for property_obj in properties:
                # In a real implementation, each property would be linked to a specific bank account
                # For now, we'll use a default account ID
                account_id = 'acc_test_123'  # This would come from user's linked accounts
                
                result = self.akahu_service.sync_property_transactions(
                    user_access_token, 
                    property_obj.id, 
                    account_id
                )
                
                result['property_id'] = property_obj.id
                result['property_name'] = property_obj.name
                results.append(result)
            
            return {
                'user_id': user_id,
                'properties_synced': len(results),
                'results': results
            }
            
        except Exception as e:
            print(f"Error syncing transactions for user {user_id}: {e}")
            return {'error': str(e)}
    
    def send_weekly_summary(self, user_id):
        """Send weekly summary email to user"""
        try:
            user = User.get_by_id(user_id)
            if not user:
                return {'error': 'User not found'}
            
            # Get weekly data
            overdue_properties = self.rent_checker.get_overdue_rent(user_id, days_overdue=1)
            
            # In a real implementation, you'd also get recent payments
            recent_payments = []
            
            success = NotificationService.send_daily_summary_email(
                user, 
                overdue_properties, 
                recent_payments
            )
            
            return {
                'user_id': user_id,
                'summary_sent': success,
                'overdue_count': len(overdue_properties),
                'recent_payments_count': len(recent_payments)
            }
            
        except Exception as e:
            print(f"Error sending weekly summary for user {user_id}: {e}")
            return {'error': str(e)}

# CLI command for manual testing
def run_manual_check():
    """Manual rent check for testing"""
    scheduler = RentScheduler(use_mock_akahu=True)
    
    print("Running manual rent check...")
    results = scheduler.run_daily_rent_check()
    print(f"Results: {results}")

if __name__ == "__main__":
    run_manual_check()