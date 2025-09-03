from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user
from flask_mail import Mail
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try PostgreSQL first, fall back to SQLite
try:
    from database import get_db_connection, test_db_connection, init_db
    # Test if PostgreSQL is actually available
    if test_db_connection():
        print("Using PostgreSQL database")
        DB_TYPE = "PostgreSQL"
    else:
        raise ImportError("PostgreSQL not accessible")
except (ImportError, Exception):
    from database_sqlite import get_db_connection, test_db_connection, init_db  
    print("Using SQLite database (PostgreSQL not available)")
    DB_TYPE = "SQLite"

# Import our application modules
from routes.auth import auth_bp
from routes.properties import properties_bp
from models.user import User
from utils.email_service import init_mail
from utils.akahu_service import MockAkahuService
from utils.rent_checker import RentChecker
from utils.notification_service import NotificationService

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///rentcheck.db')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['FRONTEND_URL'] = os.getenv('FRONTEND_URL', 'http://localhost:5000')

CORS(app, supports_credentials=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    # Return JSON error for API requests instead of redirecting
    return jsonify({'error': 'Authentication required'}), 401

# Initialize Flask-Mail
try:
    init_mail(app)
    MAIL_CONFIGURED = bool(app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD'])
    print(f"Email configured: {MAIL_CONFIGURED}")
except Exception as e:
    print(f"Email setup issue: {e}")
    MAIL_CONFIGURED = False

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(properties_bp)

# Serve static files from frontend directory
@app.route('/')
def serve_frontend():
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    return send_from_directory(frontend_path, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    return send_from_directory(frontend_path, filename)

@app.route('/api/health')
def health():
    db_status = test_db_connection()
    return jsonify({
        "status": "healthy",
        "message": "Rent Check API is running!",
        "database": {
            "type": DB_TYPE,
            "connected": db_status
        },
        "email": {
            "configured": MAIL_CONFIGURED,
            "server": app.config['MAIL_SERVER']
        },
        "features": {
            "authentication": True,
            "property_management": True,
            "rent_checking": True,
            "notifications": MAIL_CONFIGURED,
            "bank_integration": "Mock Ready"
        }
    })

@app.route('/api/system/status')
@login_required
def system_status():
    """Detailed system status for logged-in users"""
    rent_checker = RentChecker()
    
    # Get user's properties and recent activity
    from models.property import Property
    properties = Property.get_by_user_id(current_user.id)
    
    # Check rent status for user's properties
    rent_results = []
    for prop in properties:
        result = rent_checker.check_rent_for_property(prop)
        rent_results.append(result)
    
    return jsonify({
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "verified": current_user.email_verified
        },
        "properties": {
            "total": len(properties),
            "list": [p.to_dict() for p in properties]
        },
        "rent_status": rent_results,
        "system": {
            "database": DB_TYPE,
            "email_enabled": MAIL_CONFIGURED,
            "akahu_mode": "Mock",
            "notifications": "Ready" if MAIL_CONFIGURED else "Email not configured"
        }
    })

@app.route('/api/demo/rent-check')
def demo_rent_check():
    """Demo the rent checking functionality"""
    rent_checker = RentChecker()
    akahu_service = MockAkahuService()
    
    # Create mock property data for demo
    class MockProperty:
        def __init__(self):
            self.id = 1
            self.name = "Demo Property - 123 Main St"
            self.rent_amount = 450.00
            self.due_day = 15
            self.frequency = "weekly"
    
    mock_property = MockProperty()
    
    # Demo rent check
    result = rent_checker.check_rent_for_property(mock_property)
    
    # Demo Akahu transactions
    mock_transactions = akahu_service.get_transactions("mock_token", "acc_demo")
    
    return jsonify({
        "demo_property": {
            "name": mock_property.name,
            "rent_amount": mock_property.rent_amount,
            "frequency": mock_property.frequency,
            "due_day": mock_property.due_day
        },
        "rent_check_result": result,
        "mock_transactions": mock_transactions[:3],  # Show first 3
        "note": "This is a demonstration using mock data. Connect your properties for real rent checking."
    })

@app.route('/api/test/email')
def test_email():
    """Test email configuration"""
    if not MAIL_CONFIGURED:
        return jsonify({
            "success": False,
            "error": "Email not configured. Please set MAIL_USERNAME and MAIL_PASSWORD in .env file"
        }), 400
    
    try:
        from flask_mail import Message
        from utils.email_service import mail
        
        # Create test email
        msg = Message(
            subject='Rent Check - Email Test',
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']]  # Send to self
        )
        
        msg.body = """
        This is a test email from your Rent Check application.
        
        If you receive this email, your email configuration is working correctly!
        
        System Details:
        - Server: {}
        - Port: {}
        - TLS: {}
        
        Rent Check is ready to send notifications about missed rent payments.
        """.format(
            app.config['MAIL_SERVER'],
            app.config['MAIL_PORT'],
            app.config['MAIL_USE_TLS']
        )
        
        mail.send(msg)
        
        return jsonify({
            "success": True,
            "message": f"Test email sent to {app.config['MAIL_USERNAME']}",
            "smtp_server": app.config['MAIL_SERVER']
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to send test email: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("RENT CHECK - PRODUCTION MODE")
    print("=" * 60)
    
    # Initialize database
    print(f"Database: {DB_TYPE}")
    init_result = init_db()
    if init_result:
        print("Database initialized successfully!")
    else:
        print("Database initialization failed!")
    
    # Check email configuration
    print(f"Email configured: {MAIL_CONFIGURED}")
    if MAIL_CONFIGURED:
        print(f"   Server: {app.config['MAIL_SERVER']}:{app.config['MAIL_PORT']}")
    else:
        print("   To enable email: Set MAIL_USERNAME and MAIL_PASSWORD in .env")
    
    print("\nStarting production server...")
    print("\nApplication URLs:")
    print("   Frontend: http://localhost:5000")
    print("   API Health: http://localhost:5000/api/health")
    print("   Email Test: http://localhost:5000/api/test/email")
    print("   Demo Rent Check: http://localhost:5000/api/demo/rent-check")
    print("\n" + "=" * 60)
    
    app.run(debug=True, port=5000, host='0.0.0.0')