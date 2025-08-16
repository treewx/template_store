from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
import re
from models.user import User
from utils.email_service import send_verification_email, send_password_reset_email, send_welcome_email

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def validate_password(password):
    """Validate password meets requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    return True, "Valid password"

def validate_email(email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if user already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        user = User.create_user(email, password)
        if not user:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Generate verification token
        token = user.generate_verification_token(current_app.config['SECRET_KEY'])
        user.set_verification_token(token)
        
        # Send verification email
        send_verification_email(user.email, token)
        
        return jsonify({
            'message': 'User registered successfully. Please check your email for verification.',
            'user_id': user.id,
            'verification_required': True
        }), 201
        
    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Get user
        user = User.get_by_email(email)
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.email_verified:
            return jsonify({
                'error': 'Email not verified. Please check your email for verification link.',
                'verification_required': True
            }), 401
        
        # Login user
        login_user(user, remember=True)
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'email_verified': user.email_verified
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    try:
        return jsonify({
            'user': {
                'id': current_user.id,
                'email': current_user.email,
                'email_verified': current_user.email_verified
            }
        }), 200
    except Exception as e:
        print(f"Get current user error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    try:
        # Verify token and get email
        email = User.verify_token(token, current_app.config['SECRET_KEY'], 'email-verification', max_age=86400)  # 24 hours
        
        if not email:
            return jsonify({'error': 'Invalid or expired verification token'}), 400
        
        # Get user and update verification status
        user = User.get_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.email_verified:
            return jsonify({'message': 'Email already verified'}), 200
        
        if user.update_verification_status(True):
            # Send welcome email
            send_welcome_email(user.email)
            return jsonify({'message': 'Email verified successfully'}), 200
        else:
            return jsonify({'error': 'Failed to verify email'}), 500
            
    except Exception as e:
        print(f"Email verification error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.get_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.email_verified:
            return jsonify({'message': 'Email already verified'}), 200
        
        # Generate new verification token
        token = user.generate_verification_token(current_app.config['SECRET_KEY'])
        user.set_verification_token(token)
        
        # Send verification email
        send_verification_email(user.email, token)
        
        return jsonify({'message': 'Verification email sent'}), 200
        
    except Exception as e:
        print(f"Resend verification error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.get_by_email(email)
        if not user:
            # Don't reveal whether user exists or not
            return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200
        
        # Generate reset token
        token = user.generate_reset_token(current_app.config['SECRET_KEY'])
        user.set_reset_token(token)
        
        # Send reset email
        send_password_reset_email(user.email, token)
        
        return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    try:
        data = request.get_json()
        new_password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not new_password or not confirm_password:
            return jsonify({'error': 'Password and confirmation are required'}), 400
        
        if new_password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Verify token
        email = User.verify_token(token, current_app.config['SECRET_KEY'], 'password-reset', max_age=3600)  # 1 hour
        
        if not email:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        user = User.get_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update password
        if user.update_password(new_password):
            return jsonify({'message': 'Password reset successfully'}), 200
        else:
            return jsonify({'error': 'Failed to reset password'}), 500
            
    except Exception as e:
        print(f"Reset password error: {e}")
        return jsonify({'error': 'Internal server error'}), 500