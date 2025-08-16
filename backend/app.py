from flask import Flask, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from database import test_db_connection
from routes.auth import auth_bp
from models.user import User
from config import Config
from utils.email_service import init_mail

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, supports_credentials=True)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Initialize Flask-Mail
init_mail(app)

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

# Register blueprints
app.register_blueprint(auth_bp)
from routes.properties import properties_bp
app.register_blueprint(properties_bp)

@app.route('/')
def hello():
    return jsonify({"message": "Rent Check API is running!"})

@app.route('/health')
def health():
    db_status = test_db_connection()
    return jsonify({
        "status": "healthy",
        "database": "connected" if db_status else "disconnected"
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)