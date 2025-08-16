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
        # In a real implementation, you'd implement proper OAuth flow
        # For now, this is a placeholder structure
        return f"{self.base_url}/auth?client_id={self.client_id}&redirect_uri={redirect_uri}&state={user_id}"
    
    def exchange_code_for_token(self, code, redirect_uri):
        """Exchange OAuth code for access token"""
        # Placeholder implementation
        # In reality, this would make a POST request to Akahu's token endpoint
        try:
            response = requests.post(f"{self.base_url}/token", {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            })
            
            if response.status_code == 200:
                return response.json().get('access_token')
            return None
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None
    
    def get_accounts(self, access_token):
        """Get user's bank accounts"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(f"{self.base_url}/accounts", headers=headers)
            
            if response.status_code == 200:
                return response.json().get('accounts', [])
            return []
        except Exception as e:
            print(f"Error fetching accounts: {e}")
            return []
    
    def get_transactions(self, access_token, account_id, days_back=2):
        """Get recent transactions from account"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            params = {
                'start': start_date,
                'account': account_id
            }
            
            response = requests.get(f"{self.base_url}/transactions", 
                                  headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json().get('transactions', [])
            return []
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return []
    
    def store_transactions(self, transactions, property_id):
        """Store transactions in database"""
        stored_count = 0
        
        for txn in transactions:
            try:
                # Convert Akahu transaction format to our format
                transaction_date = datetime.fromisoformat(txn['date'].replace('Z', '+00:00')).date()
                amount = abs(float(txn['amount']))  # Take absolute value for credit amounts
                description = txn.get('description', '')
                
                # Only process credit transactions (rent payments)
                if float(txn['amount']) > 0:
                    transaction = Transaction.create_transaction(
                        property_id=property_id,
                        date=transaction_date,
                        amount=amount,
                        description=description,
                        matched=False
                    )
                    
                    if transaction:
                        stored_count += 1
                        
            except Exception as e:
                print(f"Error storing transaction: {e}")
                continue
        
        return stored_count
    
    def sync_property_transactions(self, user_access_token, property_id, account_id):
        """Sync transactions for a specific property"""
        try:
            transactions = self.get_transactions(user_access_token, account_id)
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

# Mock service for development/testing
class MockAkahuService(AkahuService):
    """Mock Akahu service for development and testing"""
    
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
    
    def exchange_code_for_token(self, code, redirect_uri):
        """Return mock access token"""
        return 'mock_access_token_12345'