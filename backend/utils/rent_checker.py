from datetime import datetime, timedelta
from models.property import Property
from models.transaction import Transaction
from decimal import Decimal

class RentChecker:
    def __init__(self, tolerance_percentage=0.1):
        self.tolerance_percentage = tolerance_percentage  # 10% tolerance for amount matching
    
    def check_rent_for_property(self, property_obj, check_date=None):
        """Check if rent has been received for a property on the expected date"""
        if not check_date:
            check_date = datetime.now().date()
        
        # Calculate expected rent date based on frequency
        expected_date = self.calculate_expected_rent_date(property_obj, check_date)
        
        # Get transactions around the expected date (±1 day)
        start_date = expected_date - timedelta(days=1)
        end_date = expected_date + timedelta(days=1)
        
        transactions = Transaction.get_by_date_range(property_obj.id, start_date, end_date)
        
        # Check for matching transactions
        matched_transactions = []
        for transaction in transactions:
            if self.is_rent_payment(transaction, property_obj):
                matched_transactions.append(transaction)
                transaction.mark_as_matched()
        
        return {
            'property_id': property_obj.id,
            'property_name': property_obj.name,
            'expected_date': expected_date,
            'rent_received': len(matched_transactions) > 0,
            'matched_transactions': [t.to_dict() for t in matched_transactions],
            'expected_amount': float(property_obj.rent_amount)
        }
    
    def calculate_expected_rent_date(self, property_obj, reference_date):
        """Calculate when rent was expected based on property frequency and due day"""
        due_day = property_obj.due_day
        frequency = property_obj.frequency
        
        if frequency == 'monthly':
            # For monthly rent, use the due day of the current month
            expected_date = reference_date.replace(day=min(due_day, 28))  # Handle months with fewer days
            
            # If we're past the due date, check if we should look at previous month
            if reference_date.day < due_day:
                # Look at previous month
                if expected_date.month == 1:
                    expected_date = expected_date.replace(year=expected_date.year - 1, month=12)
                else:
                    expected_date = expected_date.replace(month=expected_date.month - 1)
                    
        elif frequency == 'weekly':
            # For weekly rent, find the most recent occurrence of the due day
            days_since_due = (reference_date.weekday() - (due_day - 1)) % 7
            expected_date = reference_date - timedelta(days=days_since_due)
            
        elif frequency == 'fortnightly':
            # For fortnightly rent, find the most recent occurrence (every 14 days)
            days_since_due = (reference_date.weekday() - (due_day - 1)) % 14
            expected_date = reference_date - timedelta(days=days_since_due)
            
        else:
            expected_date = reference_date
        
        return expected_date
    
    def is_rent_payment(self, transaction, property_obj):
        """Check if a transaction matches expected rent payment"""
        expected_amount = property_obj.rent_amount
        actual_amount = transaction.amount
        
        # Check amount with tolerance
        tolerance = expected_amount * Decimal(str(self.tolerance_percentage))
        amount_match = abs(actual_amount - expected_amount) <= tolerance
        
        # Additional checks could include description matching
        # For now, we'll just check the amount
        return amount_match
    
    def check_all_properties_for_user(self, user_id, check_date=None):
        """Check rent for all properties belonging to a user"""
        properties = Property.get_by_user_id(user_id)
        results = []
        
        for property_obj in properties:
            result = self.check_rent_for_property(property_obj, check_date)
            results.append(result)
        
        return results
    
    def get_overdue_rent(self, user_id, days_overdue=1):
        """Get properties with rent overdue by specified days"""
        check_date = datetime.now().date() - timedelta(days=days_overdue)
        results = self.check_all_properties_for_user(user_id, check_date)
        
        overdue_properties = []
        for result in results:
            if not result['rent_received']:
                result['days_overdue'] = days_overdue
                overdue_properties.append(result)
        
        return overdue_properties