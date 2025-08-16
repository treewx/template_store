from database import get_db_connection
from datetime import datetime

class Transaction:
    def __init__(self, id=None, property_id=None, date=None, amount=None, 
                 description=None, matched=False, created_at=None):
        self.id = id
        self.property_id = property_id
        self.date = date
        self.amount = amount
        self.description = description
        self.matched = matched
        self.created_at = created_at
    
    @staticmethod
    def create_transaction(property_id, date, amount, description=None, matched=False):
        """Create a new transaction"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO transactions (property_id, date, amount, description, matched, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, property_id, date, amount, description, matched, created_at
                """, (property_id, date, amount, description, matched, datetime.now()))
                
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