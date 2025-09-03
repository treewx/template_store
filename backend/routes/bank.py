from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from utils.akahu_service import AkahuService, MockAkahuService
from models.user import User
from models.property import Property

bank_bp = Blueprint('bank', __name__, url_prefix='/api/bank')

# Use real service when credentials are available, otherwise mock
from config import Config
if Config.AKAHU_CLIENT_ID and Config.AKAHU_CLIENT_ID.startswith('app_token_'):
    akahu_service = AkahuService()
else:
    akahu_service = MockAkahuService()

@bank_bp.route('/connect/start', methods=['POST'])
@login_required
def start_bank_connection():
    """Start Akahu OAuth flow - Step 1"""
    try:
        # Generate OAuth authorization URL
        redirect_uri = f"{request.host_url}api/bank/connect/callback"
        auth_url = akahu_service.get_authorization_url(current_user.id, redirect_uri)
        
        return jsonify({
            'auth_url': auth_url,
            'redirect_uri': redirect_uri,
            'instructions': 'Redirect user to auth_url to complete Akahu connection'
        }), 200
        
    except Exception as e:
        print(f"Error starting bank connection: {e}")
        return jsonify({'error': 'Failed to start bank connection'}), 500

@bank_bp.route('/connect/callback', methods=['GET'])
def bank_connection_callback():
    """Handle Akahu OAuth callback - Step 2"""
    try:
        # Get authorization code and state from callback
        code = request.args.get('code')
        state = request.args.get('state')  # This is the user_id
        error = request.args.get('error')
        
        print(f"DEBUG: Callback received - code={code}, state={state}, error={error}")
        
        if error:
            return jsonify({'error': f'Akahu authorization failed: {error}'}), 400
        
        if not code or not state:
            return jsonify({'error': 'Missing authorization code or state'}), 400
        
        # Verify the state matches a valid user
        user = User.get_by_id(int(state))
        if not user:
            return jsonify({'error': 'Invalid user state'}), 400
        
        print(f"DEBUG: User found - {user.email}")
        
        # Exchange code for access token
        redirect_uri = f"{request.host_url}api/bank/connect/callback"
        print(f"DEBUG: Exchanging code with redirect_uri={redirect_uri}")
        token_data = akahu_service.exchange_code_for_token(code, redirect_uri)
        
        print(f"DEBUG: Token exchange result - {token_data}")
        
        if not token_data:
            return jsonify({'error': 'Failed to exchange code for token'}), 400
        
        access_token = token_data['access_token']
        print(f"DEBUG: Access token received - {access_token}")
        
        # Test the token by fetching accounts
        accounts = akahu_service.get_accounts(access_token)
        print(f"DEBUG: Accounts fetched - {len(accounts) if accounts else 0} accounts")
        if not accounts:
            return jsonify({'error': 'No accounts found with token'}), 400
        
        # Store the token with the user
        print(f"DEBUG: Storing credentials for user {user.id}")
        success = user.store_akahu_credentials(access_token, f"akahu_user_{user.id}")
        print(f"DEBUG: Credential storage result - {success}")
        
        if success:
            # Check if this is demo mode
            demo_mode = isinstance(akahu_service, MockAkahuService)
            mode_text = "Demo" if demo_mode else "Real"
            
            # Redirect to frontend success page
            return f"""
            <html>
                <head><title>Bank Connected Successfully</title></head>
                <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; text-align: center; padding: 3rem; background: #f8f9fa;">
                    <div style="max-width: 500px; margin: 0 auto; background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                        <h2 style="color: #28a745; margin-bottom: 1rem;">🎉 {mode_text} Bank Account Connected!</h2>
                        <p style="font-size: 1.1rem; margin: 1rem 0;">Your bank account has been successfully connected to Rent Check.</p>
                        <p style="color: #6c757d; margin: 1rem 0;">Found {len(accounts)} account(s)</p>
                        {('<p style="background: #fff3cd; padding: 0.5rem; border-radius: 6px; color: #856404; font-size: 0.9rem;"><strong>Demo Mode:</strong> Using mock transaction data for testing</p>' if demo_mode else '')}
                        <div style="margin-top: 2rem;">
                            <a href="/" style="background: #007bff; color: white; padding: 0.75rem 1.5rem; text-decoration: none; border-radius: 6px; display: inline-block;">Return to Rent Check</a>
                        </div>
                    </div>
                    <script>
                        // Auto-close window if opened as popup
                        if (window.opener) {{
                            window.opener.postMessage({{
                                type: 'AKAHU_CONNECTION_SUCCESS',
                                accounts: {len(accounts)},
                                demo_mode: {str(demo_mode).lower()}
                            }}, '*');
                            setTimeout(() => window.close(), 2000); // Close after 2 seconds
                        }}
                    </script>
                </body>
            </html>
            """
        else:
            return jsonify({'error': 'Failed to store credentials'}), 500
        
    except Exception as e:
        import traceback
        print(f"Error in bank connection callback: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to complete bank connection'}), 500

@bank_bp.route('/connect', methods=['POST'])
@login_required
def connect_bank():
    """Manual token connection (for testing/development)"""
    try:
        data = request.get_json()
        access_token = data.get('access_token')
        
        if not access_token:
            return jsonify({'error': 'Access token is required'}), 400
        
        # Test the token by fetching accounts
        accounts = akahu_service.get_accounts(access_token)
        
        if not accounts:
            return jsonify({'error': 'Invalid token or no accounts found'}), 400
        
        # Store the token with the user
        success = current_user.store_akahu_credentials(access_token, f"akahu_user_{current_user.id}")
        
        if success:
            return jsonify({
                'message': 'Bank connected successfully',
                'accounts': accounts,
                'token_status': 'valid'
            }), 200
        else:
            return jsonify({'error': 'Failed to store credentials'}), 500
        
    except Exception as e:
        print(f"Error connecting bank: {e}")
        return jsonify({'error': 'Failed to connect bank account'}), 500

@bank_bp.route('/accounts', methods=['GET'])
@login_required
def get_accounts():
    """Get user's connected bank accounts"""
    try:
        # For demo, we'll use a mock token
        # In real implementation, this would come from user's stored token
        mock_token = 'mock_token'
        
        accounts = akahu_service.get_accounts(mock_token)
        
        return jsonify({
            'accounts': accounts,
            'connected': len(accounts) > 0
        }), 200
        
    except Exception as e:
        print(f"Error fetching accounts: {e}")
        return jsonify({'error': 'Failed to fetch accounts'}), 500

@bank_bp.route('/sync/<int:property_id>', methods=['POST'])
@login_required
def sync_transactions(property_id):
    """Sync transactions for a specific property"""
    try:
        data = request.get_json()
        account_id = data.get('account_id')
        
        if not account_id:
            return jsonify({'error': 'Account ID is required'}), 400
        
        # Check if property belongs to current user
        property_obj = Property.get_by_id(property_id)
        if not property_obj or property_obj.user_id != current_user.id:
            return jsonify({'error': 'Property not found or access denied'}), 403
        
        # For demo, use mock token
        mock_token = 'mock_token'
        
        result = akahu_service.sync_property_transactions(
            mock_token, property_id, account_id
        )
        
        if result['success']:
            return jsonify({
                'message': 'Transactions synced successfully',
                'transactions_found': result['transactions_found'],
                'transactions_stored': result['transactions_stored']
            }), 200
        else:
            return jsonify({'error': result['error']}), 500
        
    except Exception as e:
        print(f"Error syncing transactions: {e}")
        return jsonify({'error': 'Failed to sync transactions'}), 500

@bank_bp.route('/status', methods=['GET'])
@login_required
def bank_status():
    """Get bank connection status for current user"""
    try:
        # Check if user has Akahu connection
        is_connected = current_user.bank_connected and current_user.akahu_access_token
        accounts_count = 0
        
        if is_connected:
            try:
                accounts = akahu_service.get_accounts(current_user.akahu_access_token)
                accounts_count = len(accounts)
            except:
                # Token might be expired
                is_connected = False
        
        return jsonify({
            'connected': is_connected,
            'accounts_count': accounts_count,
            'last_sync': None,
            'demo_mode': isinstance(akahu_service, MockAkahuService),
            'user_has_token': current_user.akahu_access_token is not None
        }), 200
        
    except Exception as e:
        print(f"Error getting bank status: {e}")
        return jsonify({'error': 'Failed to get bank status'}), 500

@bank_bp.route('/test-connection', methods=['POST'])
@login_required
def test_connection():
    """Test bank connection with provided token"""
    try:
        data = request.get_json()
        test_token = data.get('test_token', 'mock_token')
        
        # Test with mock service
        accounts = akahu_service.get_accounts(test_token)
        
        if accounts:
            # Also test getting some transactions
            sample_account = accounts[0]
            transactions = akahu_service.get_transactions(test_token, sample_account['id'])
            
            return jsonify({
                'success': True,
                'accounts_found': len(accounts),
                'sample_transactions': len(transactions),
                'test_data': {
                    'accounts': accounts[:2],  # Show first 2 accounts
                    'recent_transactions': transactions[:5]  # Show first 5 transactions
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No accounts found with provided token'
            }), 400
        
    except Exception as e:
        print(f"Error testing connection: {e}")
        return jsonify({'error': 'Failed to test connection'}), 500