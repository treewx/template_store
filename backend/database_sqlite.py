import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'rentcheck.db'

def get_db_connection():
    """Get a database connection using SQLite"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # This makes rows behave like dictionaries
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def test_db_connection():
    """Test database connection"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            conn.close()
            return result['test'] == 1
        return False
    except Exception as e:
        print(f"Database test failed: {e}")
        return False

def migrate_akahu_fields(cursor):
    """Migrate existing database to add Akahu fields"""
    try:
        # Check if akahu fields exist in users table
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [column[1] for column in cursor.fetchall()]
        
        if 'akahu_access_token' not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN akahu_access_token TEXT")
            cursor.execute("ALTER TABLE users ADD COLUMN akahu_user_id TEXT") 
            cursor.execute("ALTER TABLE users ADD COLUMN bank_connected BOOLEAN DEFAULT FALSE")
            print("Added Akahu fields to users table")
        
        # Check if akahu fields exist in transactions table
        cursor.execute("PRAGMA table_info(transactions)")
        txn_columns = [column[1] for column in cursor.fetchall()]
        
        if 'akahu_transaction_id' not in txn_columns:
            cursor.execute("ALTER TABLE transactions ADD COLUMN akahu_transaction_id TEXT")
            cursor.execute("ALTER TABLE transactions ADD COLUMN confidence_score DECIMAL(3,2)")
            cursor.execute("ALTER TABLE transactions ADD COLUMN raw_data TEXT")
            print("Added Akahu fields to transactions table")
            
    except Exception as e:
        print(f"Migration error (non-critical): {e}")

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token TEXT,
                reset_token TEXT,
                reset_token_expires TIMESTAMP,
                akahu_access_token TEXT,
                akahu_user_id TEXT,
                bank_connected BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Properties table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                keyword TEXT NOT NULL,
                address TEXT NOT NULL,
                rent_amount DECIMAL(10,2) NOT NULL,
                due_day TEXT NOT NULL CHECK (due_day IN ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')),
                frequency TEXT NOT NULL CHECK (frequency IN ('weekly', 'fortnightly', 'monthly')),
                tenant_nickname TEXT,
                balance DECIMAL(10,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER REFERENCES properties(id),
                date DATE NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                description TEXT,
                matched BOOLEAN DEFAULT FALSE,
                akahu_transaction_id TEXT UNIQUE,
                confidence_score DECIMAL(3,2),
                raw_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Notification log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                property_id INTEGER REFERENCES properties(id),
                notification_type TEXT NOT NULL,
                date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT
            )
        """)
        
        # Apply migrations for existing databases
        migrate_akahu_fields(cursor)
        
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