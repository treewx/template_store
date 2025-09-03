from datetime import datetime, timedelta
from models.user import User
from models.property import Property
from utils.akahu_service import AkahuService, MockAkahuService
from utils.notification_service import NotificationService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartRentScheduler:
    """
    Ultra-efficient scheduler that only fetches transactions 
    on the day after rent is due for each property
    """
    
    def __init__(self, use_mock_akahu=True):
        self.akahu_service = MockAkahuService() if use_mock_akahu else AkahuService()
    
    def get_properties_due_for_check_today(self):
        """
        Get all properties where rent should be checked today
        (i.e., rent was due yesterday)
        """
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get day of week names
        yesterday_weekday = yesterday.strftime('%A').lower()
        
        try:
            # Get all properties from all users
            all_properties = []
            users = User.get_all_with_bank_connected()
            
            for user in users:
                properties = Property.get_by_user_id(user.id)
                for prop in properties:
                    # Add user info to property for convenience
                    prop.user = user
                    all_properties.append(prop)
            
            # Filter properties that had rent due yesterday
            properties_to_check = []
            
            for prop in all_properties:
                if self._should_check_property_today(prop, yesterday, yesterday_weekday):
                    properties_to_check.append(prop)
            
            logger.info(f"Found {len(properties_to_check)} properties to check today")
            return properties_to_check
            
        except Exception as e:
            logger.error(f"Error getting properties due for check: {e}")
            return []
    
    def _should_check_property_today(self, property_obj, yesterday, yesterday_weekday):
        """
        Determine if a property should be checked today based on its rent frequency
        """
        if property_obj.frequency == 'weekly':
            # Check if yesterday was the rent due day
            return property_obj.due_day == yesterday_weekday
            
        elif property_obj.frequency == 'fortnightly':
            # For fortnightly, we need to check if it's been 14 days since last due date
            # This is more complex - for now, check every 2 weeks on the due day
            return property_obj.due_day == yesterday_weekday and yesterday.isocalendar()[1] % 2 == 0
            
        elif property_obj.frequency == 'monthly':
            # Check if yesterday was the monthly due date
            # For monthly, we use the due_day as the day of month (1-31)
            try:
                due_day_of_month = int(property_obj.due_day) if property_obj.due_day.isdigit() else 1
                return yesterday.day == due_day_of_month
            except:
                # Fallback: check first day of month
                return yesterday.day == 1
        
        return False
    
    def fetch_transactions_for_property(self, property_obj):
        """
        Fetch transactions for a specific property around its rent due date
        """
        user = property_obj.user
        
        if not user.akahu_access_token:
            logger.warning(f"User {user.id} has no Akahu token, skipping")
            return {'success': False, 'error': 'No Akahu token'}
        
        try:
            # Define date range: 3 days around rent due date
            today = datetime.now().date()
            start_date = datetime.combine(today - timedelta(days=2), datetime.min.time())
            end_date = datetime.combine(today + timedelta(days=1), datetime.min.time())
            
            logger.info(f"Fetching transactions for property {property_obj.id} from {start_date} to {end_date}")
            
            # Fetch transactions (without specifying account - get all accounts)
            transactions = self.akahu_service.get_transactions(
                user.akahu_access_token,
                start_date=start_date,
                end_date=end_date
            )
            
            # Store and process transactions
            stored_count = self.akahu_service.store_transactions(transactions, property_obj.id)
            
            # Check for rent payments and update property balance
            rent_payments = self._detect_rent_payments(transactions, property_obj)
            
            result = {
                'success': True,
                'property_id': property_obj.id,
                'transactions_fetched': len(transactions),
                'transactions_stored': stored_count,
                'rent_payments_detected': len(rent_payments),
                'api_calls_used': 1  # Track for cost monitoring
            }
            
            # If no rent payment found, send notification
            if len(rent_payments) == 0:
                self._send_late_rent_notification(user, property_obj)
                result['notification_sent'] = True
            else:
                result['notification_sent'] = False
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching transactions for property {property_obj.id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def _detect_rent_payments(self, transactions, property_obj):
        """
        Detect rent payments from transactions using amount and keyword matching
        """
        rent_payments = []
        rent_amount = float(property_obj.rent_amount)
        tolerance = rent_amount * 0.05  # 5% tolerance
        
        for txn in transactions:
            amount = abs(float(txn.get('amount', 0)))
            description = txn.get('description', '').lower()
            
            # Check amount match
            amount_match = abs(amount - rent_amount) <= tolerance
            
            # Check keyword match if property has keywords
            keyword_match = True
            if hasattr(property_obj, 'keyword') and property_obj.keyword:
                keyword_match = property_obj.keyword.lower() in description
            
            # Check tenant nickname match if available
            if hasattr(property_obj, 'tenant_nickname') and property_obj.tenant_nickname:
                tenant_match = property_obj.tenant_nickname.lower() in description
                keyword_match = keyword_match or tenant_match
            
            if amount_match and keyword_match:
                rent_payments.append(txn)
                logger.info(f"Rent payment detected: ${amount} - {description}")
        
        return rent_payments
    
    def _send_late_rent_notification(self, user, property_obj):
        """
        Send notification for late rent payment
        """
        try:
            NotificationService.send_rent_overdue_email(user, {
                'property': property_obj,
                'days_overdue': 1,
                'amount': property_obj.rent_amount
            })
            logger.info(f"Sent late rent notification for property {property_obj.id}")
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    def run_daily_smart_check(self):
        """
        Main method: Run smart rent checking only for properties due today
        """
        logger.info("Starting smart daily rent check...")
        
        properties_to_check = self.get_properties_due_for_check_today()
        
        if not properties_to_check:
            logger.info("No properties due for checking today")
            return {
                'properties_checked': 0,
                'api_calls_used': 0,
                'notifications_sent': 0,
                'total_cost': 0.0
            }
        
        results = {
            'properties_checked': 0,
            'api_calls_used': 0,
            'notifications_sent': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'total_cost': 0.0,
            'details': []
        }
        
        # Process each property
        for property_obj in properties_to_check:
            result = self.fetch_transactions_for_property(property_obj)
            
            results['properties_checked'] += 1
            results['details'].append(result)
            
            if result['success']:
                results['successful_checks'] += 1
                results['api_calls_used'] += result.get('api_calls_used', 0)
                if result.get('notification_sent'):
                    results['notifications_sent'] += 1
            else:
                results['failed_checks'] += 1
        
        # Calculate cost ($0.10 per API call)
        results['total_cost'] = results['api_calls_used'] * 0.10
        
        logger.info(f"Smart rent check completed: {results}")
        return results
    
    def schedule_rent_checks(self):
        """
        Create a schedule of when to check each property
        Returns a list of (date, property_id) tuples for the next 30 days
        """
        schedule = []
        today = datetime.now().date()
        
        try:
            # Get all properties from all users
            users = User.get_all_with_bank_connected()
            all_properties = []
            
            for user in users:
                properties = Property.get_by_user_id(user.id)
                for prop in properties:
                    prop.user = user
                    all_properties.append(prop)
            
            # Generate schedule for next 30 days
            for days_ahead in range(1, 31):
                check_date = today + timedelta(days=days_ahead)
                rent_due_date = check_date - timedelta(days=1)
                rent_due_weekday = rent_due_date.strftime('%A').lower()
                
                for prop in all_properties:
                    if self._should_check_property_today(prop, rent_due_date, rent_due_weekday):
                        schedule.append({
                            'check_date': check_date,
                            'property_id': prop.id,
                            'property_address': getattr(prop, 'address', 'Unknown'),
                            'user_email': prop.user.email,
                            'rent_amount': prop.rent_amount,
                            'frequency': prop.frequency
                        })
            
            # Sort by date
            schedule.sort(key=lambda x: x['check_date'])
            
            logger.info(f"Generated schedule for {len(schedule)} property checks over next 30 days")
            return schedule
            
        except Exception as e:
            logger.error(f"Error generating schedule: {e}")
            return []

# CLI functions for testing
def run_smart_check():
    """Run smart check manually"""
    scheduler = SmartRentScheduler(use_mock_akahu=True)
    results = scheduler.run_daily_smart_check()
    print(f"Smart check results: {results}")

def show_schedule():
    """Show upcoming rent check schedule"""
    scheduler = SmartRentScheduler(use_mock_akahu=True)
    schedule = scheduler.schedule_rent_checks()
    
    print("Upcoming Rent Check Schedule:")
    print("=" * 50)
    for item in schedule[:10]:  # Show next 10
        print(f"{item['check_date']} - Property {item['property_id']} - {item['property_address']} - ${item['rent_amount']}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'schedule':
        show_schedule()
    else:
        run_smart_check()