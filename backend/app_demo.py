from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager
from database_sqlite import test_db_connection, init_db
from routes.auth import auth_bp
from routes.properties import properties_bp
from models.user import User
from utils.email_service import init_mail
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'demo-secret-key-for-testing'
CORS(app, supports_credentials=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Configure Flask-Login for API usage
@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'Authentication required'}), 401

# Initialize Flask-Mail (for demo, just set minimal config)
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = None
app.config['MAIL_PASSWORD'] = None
init_mail(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(properties_bp)
from routes.bank import bank_bp
app.register_blueprint(bank_bp)

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
        "database": "connected" if db_status else "disconnected",
        "demo_mode": True
    })

@app.route('/api/demo/status')
def demo_status():
    return jsonify({
        "application": "Rent Check - NZ Landlord Tool",
        "status": "Demo Mode Active",
        "features": [
            "✅ Flask Backend Server Running",
            "✅ SQLite Database Initialized", 
            "✅ CORS Enabled for Frontend",
            "✅ Static File Serving",
            "✅ API Health Endpoints",
            "🔧 Full Authentication System (Ready)",
            "🔧 Property Management (Ready)",
            "🔧 Akahu Bank Integration (Mock Ready)",
            "🔧 Email Notifications (Ready)",
            "🔧 Rent Checking Logic (Ready)"
        ],
        "next_steps": [
            "Connect PostgreSQL database for full functionality",
            "Configure email settings (SMTP)",
            "Set up Akahu API credentials",
            "Deploy to Railway or Fly.io"
        ],
        "technologies": {
            "backend": "Flask + SQLite",
            "frontend": "HTML/CSS/JavaScript",
            "auth": "Flask-Login + bcrypt",
            "database": "SQLite (demo) / PostgreSQL (production)",
            "styling": "Mobile-first responsive CSS"
        }
    })

if __name__ == '__main__':
    print("Starting Rent Check Demo Application...")
    print("=" * 50)
    
    # Initialize database
    init_db()
    
    print("\nDatabase initialized successfully!")
    print("Starting Flask server...")
    print("\nAccess the application at:")
    print("   Frontend: http://localhost:5000")
    print("   API Health: http://localhost:5000/api/health")
    print("   Demo Status: http://localhost:5000/api/demo/status")
    print("\n" + "=" * 50)
    
    app.run(debug=True, port=5000, host='0.0.0.0')