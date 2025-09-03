import requests
from datetime import datetime, timedelta
from config import Config
from models.transaction import Transaction

class AkahuService:
    def __init__(self):
        self.client_id = Config.AKAHU_CLIENT_ID
        self.client_secret = Config.AKAHU_CLIENT_SECRET
        self.base_url = "https://api.akahu.io/v1"
    
    def get_authorization_url(self, user_id, redirect_uri):
        """Get Akahu OAuth authorization URL"""
        from urllib.parse import urlencode
        
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': 'ENDURING_CONSENT',
            'state': user_id  # For security
        }
        return f"https://oauth.akahu.nz?{urlencode(params)}"
    
    def exchange_code_for_token(self, code, redirect_uri):
        """Exchange OAuth code for access token"""
        try:
            response = requests.post("https://api.akahu.io/v1/token", data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            })
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    'access_token': token_data.get('access_token'),
                    'user_token': token_data.get('access_token')  # Akahu uses this term
                }
            return None
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None
    
    def get_accounts(self, access_token):
        """Get user's bank accounts"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'X-Akahu-Id': self.client_id  # Required for Akahu
            }
            response = requests.get(f"{self.base_url}/accounts", headers=headers)
            
            if response.status_code == 200:
                return response.json().get('items', [])  # Akahu uses 'items'
            else:
                print(f"Akahu API error: {response.status_code} - {response.text}")
            return []
        except Exception as e:
            print(f"Error fetching accounts: {e}")
            return []
    
    def get_transactions(self, access_token, start_date=None, end_date=None, account_id=None):
        """Get transactions with proper Akahu headers"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'X-Akahu-Id': self.client_id  # Required for Akahu
            }
            
            params = {}
            if start_date:
                # Akahu expects millisecond timestamps
                params['start'] = int(start_date.timestamp() * 1000)
            if end_date:
                params['end'] = int(end_date.timestamp() * 1000)
            if account_id:
                params['account'] = account_id
                
            response = requests.get(f"{self.base_url}/transactions", 
                                  headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json().get('items', [])  # Akahu uses 'items'
            else:
                print(f"Akahu API error: {response.status_code} - {response.text}")
            return []
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []
    
    def store_transactions(self, transactions, property_id):
        """Store transactions in database with Akahu deduplication"""
        stored_count = 0
        
        for txn in transactions:
            try:
                # Convert Akahu transaction format to our format
                transaction_date = datetime.fromisoformat(txn['date'].replace('Z', '+00:00')).date()
                amount = abs(float(txn['amount']))  # Take absolute value for credit amounts
                description = txn.get('description', '')
                akahu_txn_id = txn.get('_id', '')  # Akahu transaction ID
                
                # Only process credit transactions (rent payments)
                if float(txn['amount']) > 0:
                    transaction = Transaction.create_transaction(
                        property_id=property_id,
                        date=transaction_date,
                        amount=amount,
                        description=description,
                        matched=False,
                        akahu_transaction_id=akahu_txn_id,
                        raw_data=str(txn)  # Store full transaction data
                    )
                    
                    if transaction:
                        stored_count += 1
                        
            except Exception as e:
                print(f"Error storing transaction: {e}")
                continue
        
        return stored_count
    
    def sync_property_transactions(self, user_access_token, property_id, account_id=None):
        """Sync transactions for a specific property"""
        try:
            transactions = self.get_transactions(user_access_token, account_id=account_id)
            stored_count = self.store_transactions(transactions, property_id)
            
            return {
                'success': True,
                'transactions_found': len(transactions),
                'transactions_stored': stored_count
            }
        except Exception as e:
            print(f"Error syncing property transactions: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def fetch_rent_due_transactions(self, user_access_token, property_id, rent_due_date):
        """
        Ultra-efficient: Fetch transactions only around rent due date
        Minimizes API calls by targeting 3-day window
        """
        try:
            # Create 3-day window around rent due date
            start_date = datetime.combine(rent_due_date - timedelta(days=1), datetime.min.time())
            end_date = datetime.combine(rent_due_date + timedelta(days=2), datetime.min.time())
            
            print(f"Fetching targeted transactions for property {property_id}: {start_date} to {end_date}")
            
            # Fetch only transactions in this window
            transactions = self.get_transactions(
                user_access_token,
                start_date=start_date,
                end_date=end_date
            )
            
            # Store transactions with Akahu deduplication
            stored_count = self.store_transactions(transactions, property_id)
            
            return {
                'success': True,
                'property_id': property_id,
                'date_range': f"{start_date.date()} to {end_date.date()}",
                'transactions_found': len(transactions),
                'transactions_stored': stored_count,
                'api_calls_used': 1,  # Only 1 API call per property
                'estimated_cost': 0.10  # $0.10 per call
            }
            
        except Exception as e:
            print(f"Error fetching rent due transactions: {e}")
            return {
                'success': False,
                'error': str(e),
                'api_calls_used': 0,
                'estimated_cost': 0.0
            }
    
    def detect_rent_payments(self, transactions, property_obj):
        """
        Enhanced rent payment detection with confidence scoring
        """
        detected_payments = []
        rent_amount = float(property_obj.rent_amount)
        tolerance = rent_amount * 0.05  # 5% tolerance
        
        for txn in transactions:
            amount = abs(float(txn.get('amount', 0)))
            description = txn.get('description', '').lower()
            
            # Amount matching
            amount_match = abs(amount - rent_amount) <= tolerance
            if not amount_match:
                continue
            
            # Keyword matching
            confidence_score = 0.5  # Base score for amount match
            
            # Check for property keyword
            if hasattr(property_obj, 'keyword') and property_obj.keyword:
                if property_obj.keyword.lower() in description:
                    confidence_score += 0.3
            
            # Check for tenant nickname
            if hasattr(property_obj, 'tenant_nickname') and property_obj.tenant_nickname:
                if property_obj.tenant_nickname.lower() in description:
                    confidence_score += 0.2
            
            # Check for common rent keywords
            rent_keywords = ['rent', 'rental', 'lease', 'housing']
            for keyword in rent_keywords:
                if keyword in description:
                    confidence_score += 0.1
                    break
            
            if confidence_score >= 0.6:  # Minimum confidence threshold
                detected_payments.append({
                    'transaction': txn,
                    'property': property_obj,
                    'confidence': confidence_score,
                    'amount_match': True,
                    'keyword_match': confidence_score > 0.5
                })
        
        return detected_payments

# Mock service for development/testing
class MockAkahuService(AkahuService):
    """Mock Akahu service for development and testing"""
    
    def get_authorization_url(self, user_id, redirect_uri):
        """Return mock authorization URL for demo"""
        # Return a mock URL that shows a demo success page instead of real Akahu
        return f"{redirect_uri}?code=mock_auth_code_demo&state={user_id}"
    
    def exchange_code_for_token(self, code, redirect_uri):
        """Return mock access token for demo"""
        if code == 'mock_auth_code_demo':
            return {
                'access_token': 'mock_access_token_demo_12345',
                'user_token': 'mock_access_token_demo_12345'
            }
        return None
    
    def get_accounts(self, access_token):
        """Return mock accounts"""
        return [
            {
                'id': 'acc_test_123',
                'name': 'BNZ Everyday Account',
                'bank': 'BNZ',
                'type': 'CHECKING'
            },
            {
                'id': 'acc_test_456', 
                'name': 'ASB Savings Account',
                'bank': 'ASB',
                'type': 'SAVINGS'
            }
        ]
    
    def get_transactions(self, access_token, account_id, days_back=2):
        """Return mock transactions"""
        from decimal import Decimal
        import random
        
        transactions = []
        
        # Generate some mock rent payments
        for i in range(3):
            date = datetime.now() - timedelta(days=i)
            transactions.append({
                'id': f'txn_mock_{i}',
                'date': date.isoformat(),
                'amount': random.choice([450.00, 520.00, 380.00]),  # Mock rent amounts
                'description': random.choice([
                    'Rent payment - Smith',
                    'Weekly rent',
                    'Property rent - Jones',
                    'Rental payment'
                ]),
                'type': 'CREDIT'
            })
        
        return transactions
    
