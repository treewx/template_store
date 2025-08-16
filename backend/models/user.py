import bcrypt
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from database import get_db_connection

class User:
    def __init__(self, id=None, email=None, password_hash=None, email_verified=False, 
                 verification_token=None, reset_token=None, reset_token_expires=None, created_at=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.email_verified = email_verified
        self.verification_token = verification_token
        self.reset_token = reset_token
        self.reset_token_expires = reset_token_expires
        self.created_at = created_at
    
    @staticmethod
    def hash_password(password):
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def generate_verification_token(self, secret_key):
        """Generate email verification token"""
        serializer = URLSafeTimedSerializer(secret_key)
        return serializer.dumps(self.email, salt='email-verification')
    
    def generate_reset_token(self, secret_key):
        """Generate password reset token"""
        serializer = URLSafeTimedSerializer(secret_key)
        return serializer.dumps(self.email, salt='password-reset')
    
    @staticmethod
    def verify_token(token, secret_key, salt, max_age=3600):
        """Verify a token and return the email if valid"""
        serializer = URLSafeTimedSerializer(secret_key)
        try:
            return serializer.loads(token, salt=salt, max_age=max_age)
        except:
            return None
    
    @staticmethod
    def create_user(email, password):
        """Create a new user"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            password_hash = User.hash_password(password)
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (email, password_hash, email_verified, created_at)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, email, password_hash, email_verified, created_at
                """, (email, password_hash, False, datetime.now()))
                
                result = cursor.fetchone()
                conn.commit()
                
                if result:
                    return User(
                        id=result['id'],
                        email=result['email'],
                        password_hash=result['password_hash'],
                        email_verified=result['email_verified'],
                        created_at=result['created_at']
                    )
                return None
        except Exception as e:
            print(f"Error creating user: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, email, password_hash, email_verified, verification_token,
                           reset_token, reset_token_expires, created_at
                    FROM users WHERE email = %s
                """, (email,))
                
                result = cursor.fetchone()
                if result:
                    return User(
                        id=result['id'],
                        email=result['email'],
                        password_hash=result['password_hash'],
                        email_verified=result['email_verified'],
                        verification_token=result.get('verification_token'),
                        reset_token=result.get('reset_token'),
                        reset_token_expires=result.get('reset_token_expires'),
                        created_at=result['created_at']
                    )
                return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, email, password_hash, email_verified, verification_token,
                           reset_token, reset_token_expires, created_at
                    FROM users WHERE id = %s
                """, (user_id,))
                
                result = cursor.fetchone()
                if result:
                    return User(
                        id=result['id'],
                        email=result['email'],
                        password_hash=result['password_hash'],
                        email_verified=result['email_verified'],
                        verification_token=result.get('verification_token'),
                        reset_token=result.get('reset_token'),
                        reset_token_expires=result.get('reset_token_expires'),
                        created_at=result['created_at']
                    )
                return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
        finally:
            conn.close()
    
    def update_verification_status(self, verified=True):
        """Update user's email verification status"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET email_verified = %s, verification_token = NULL
                    WHERE id = %s
                """, (verified, self.id))
                conn.commit()
                self.email_verified = verified
                self.verification_token = None
                return True
        except Exception as e:
            print(f"Error updating verification status: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def set_verification_token(self, token):
        """Store verification token"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET verification_token = %s WHERE id = %s
                """, (token, self.id))
                conn.commit()
                self.verification_token = token
                return True
        except Exception as e:
            print(f"Error setting verification token: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def set_reset_token(self, token):
        """Store password reset token with expiration"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            expires_at = datetime.now() + timedelta(hours=1)
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET reset_token = %s, reset_token_expires = %s WHERE id = %s
                """, (token, expires_at, self.id))
                conn.commit()
                self.reset_token = token
                self.reset_token_expires = expires_at
                return True
        except Exception as e:
            print(f"Error setting reset token: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_password(self, new_password):
        """Update user's password"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            new_hash = User.hash_password(new_password)
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET password_hash = %s, reset_token = NULL, reset_token_expires = NULL
                    WHERE id = %s
                """, (new_hash, self.id))
                conn.commit()
                self.password_hash = new_hash
                self.reset_token = None
                self.reset_token_expires = None
                return True
        except Exception as e:
            print(f"Error updating password: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def is_authenticated(self):
        """Required for Flask-Login"""
        return True
    
    def is_active(self):
        """Required for Flask-Login"""
        return self.email_verified
    
    def is_anonymous(self):
        """Required for Flask-Login"""
        return False
    
    def get_id(self):
        """Required for Flask-Login"""
        return str(self.id)