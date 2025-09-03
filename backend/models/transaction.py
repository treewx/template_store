from database_sqlite import get_db_connection
from datetime import datetime

class Transaction:
    def __init__(self, id=None, property_id=None, date=None, amount=None, 
                 description=None, matched=False, akahu_transaction_id=None,
                 confidence_score=None, raw_data=None, created_at=None):
        self.id = id
        self.property_id = property_id
        self.date = date
        self.amount = amount
        self.description = description
        self.matched = matched
        self.akahu_transaction_id = akahu_transaction_id
        self.confidence_score = confidence_score
        self.raw_data = raw_data
        self.created_at = created_at
    
    @staticmethod
    def create_transaction(property_id, date, amount, description=None, matched=False,
                          akahu_transaction_id=None, confidence_score=None, raw_data=None):
        """Create a new transaction"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            
            # Check if transaction already exists (Akahu deduplication)
            if akahu_transaction_id:
                cursor.execute("""
                    SELECT id FROM transactions WHERE akahu_transaction_id = ?
                """, (akahu_transaction_id,))
                if cursor.fetchone():
                    print(f"Transaction {akahu_transaction_id} already exists, skipping")
                    return None
            
            cursor.execute("""
                INSERT INTO transactions (property_id, date, amount, description, matched, 
                                        akahu_transaction_id, confidence_score, raw_data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (property_id, date, amount, description, matched, 
                  akahu_transaction_id, confidence_score, raw_data, datetime.now()))
            
            # Get the inserted record
            transaction_id = cursor.lastrowid
            cursor.execute("""
                SELECT id, property_id, date, amount, description, matched,
                       akahu_transaction_id, confidence_score, raw_data, created_at
                FROM transactions WHERE id = ?
            """, (transaction_id,))
            result = cursor.fetchone()
            
            conn.commit()
            
            if result:
                return Transaction(
                    id=result['id'],
                    property_id=result['property_id'],
                    date=result['date'],
                    amount=result['amount'],
                    description=result['description'],
                    matched=result['matched'],
                    akahu_transaction_id=result['akahu_transaction_id'] if 'akahu_transaction_id' in result.keys() else None,
                    confidence_score=result['confidence_score'] if 'confidence_score' in result.keys() else None,
                    raw_data=result['raw_data'] if 'raw_data' in result.keys() else None,
                    created_at=result['created_at']
                )
            return None
        except Exception as e:
            print(f"Error creating transaction: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_property_id(property_id, limit=None):
        """Get transactions for a property"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT id, property_id, date, amount, description, matched, created_at
                    FROM transactions WHERE property_id = %s ORDER BY date DESC
                """
                params = [property_id]
                
                if limit:
                    query += " LIMIT %s"
                    params.append(limit)
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                transactions = []
                
                for result in results:
                    transactions.append(Transaction(
                        id=result['id'],
                        property_id=result['property_id'],
                        date=result['date'],
                        amount=result['amount'],
                        description=result['description'],
                        matched=result['matched'],
                        created_at=result['created_at']
                    ))
                
                return transactions
        except Exception as e:
            print(f"Error getting transactions by property ID: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_unmatched_by_property(property_id):
        """Get unmatched transactions for a property"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, property_id, date, amount, description, matched, created_at
                    FROM transactions WHERE property_id = %s AND matched = FALSE
                    ORDER BY date DESC
                """, (property_id,))
                
                results = cursor.fetchall()
                transactions = []
                
                for result in results:
                    transactions.append(Transaction(
                        id=result['id'],
                        property_id=result['property_id'],
                        date=result['date'],
                        amount=result['amount'],
                        description=result['description'],
                        matched=result['matched'],
                        created_at=result['created_at']
                    ))
                
                return transactions
        except Exception as e:
            print(f"Error getting unmatched transactions: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_by_date_range(property_id, start_date, end_date):
        """Get transactions within a date range"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, property_id, date, amount, description, matched, created_at
                    FROM transactions 
                    WHERE property_id = %s AND date BETWEEN %s AND %s
                    ORDER BY date DESC
                """, (property_id, start_date, end_date))
                
                results = cursor.fetchall()
                transactions = []
                
                for result in results:
                    transactions.append(Transaction(
                        id=result['id'],
                        property_id=result['property_id'],
                        date=result['date'],
                        amount=result['amount'],
                        description=result['description'],
                        matched=result['matched'],
                        created_at=result['created_at']
                    ))
                
                return transactions
        except Exception as e:
            print(f"Error getting transactions by date range: {e}")
            return []
        finally:
            conn.close()
    
    def mark_as_matched(self):
        """Mark transaction as matched"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE transactions SET matched = TRUE WHERE id = %s
                """, (self.id,))
                conn.commit()
                self.matched = True
                return True
        except Exception as e:
            print(f"Error marking transaction as matched: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_description(self, description):
        """Update transaction description"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE transactions SET description = %s WHERE id = %s
                """, (description, self.id))
                conn.commit()
                self.description = description
                return True
        except Exception as e:
            print(f"Error updating transaction description: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete(self):
        """Delete transaction"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM transactions WHERE id = %s", (self.id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting transaction: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'property_id': self.property_id,
            'date': self.date.isoformat() if self.date else None,
            'amount': float(self.amount) if self.amount else None,
            'description': self.description,
            'matched': self.matched,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }