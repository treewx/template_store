import psycopg2
from psycopg2.extras import RealDictCursor
import os
from config import Config

def get_db_connection():
    """Get a database connection using configuration"""
    try:
        conn = psycopg2.connect(
            Config.DATABASE_URL,
            cursor_factory=RealDictCursor
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def test_db_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                conn.close()
                return result['test'] == 1
        return False
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        with conn.cursor() as cursor:
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email_verified BOOLEAN DEFAULT FALSE,
                    verification_token VARCHAR(255),
                    reset_token VARCHAR(255),
                    reset_token_expires TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Properties table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS properties (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    name VARCHAR(255) NOT NULL,
                    address TEXT,
                    rent_amount DECIMAL(10,2) NOT NULL,
                    due_day INTEGER NOT NULL,
                    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('weekly', 'fortnightly', 'monthly')),
                    tenant_nickname VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    property_id INTEGER REFERENCES properties(id),
                    date DATE NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    description TEXT,
                    matched BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Notification log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notification_log (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    property_id INTEGER REFERENCES properties(id),
                    notification_type VARCHAR(50) NOT NULL,
                    date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message TEXT
                )
            """)
            
            conn.commit()
            print("Database tables created successfully")
            return True
            
    except Exception as e:
        print(f"Database initialization error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    if test_db_connection():
        print("Database connection successful")
        init_db()
    else:
        print("Database connection failed")