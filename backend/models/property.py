from database import get_db_connection
from datetime import datetime

class Property:
    def __init__(self, id=None, user_id=None, name=None, address=None, 
                 rent_amount=None, due_day=None, frequency=None, 
                 tenant_nickname=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.address = address
        self.rent_amount = rent_amount
        self.due_day = due_day  # Day of month (1-31)
        self.frequency = frequency  # 'weekly', 'fortnightly', 'monthly'
        self.tenant_nickname = tenant_nickname
        self.created_at = created_at
    
    @staticmethod
    def create_property(user_id, name, address, rent_amount, due_day, frequency, tenant_nickname=None):
        """Create a new property"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO properties (user_id, name, address, rent_amount, due_day, frequency, tenant_nickname, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, user_id, name, address, rent_amount, due_day, frequency, tenant_nickname, created_at
                """, (user_id, name, address, rent_amount, due_day, frequency, tenant_nickname, datetime.now()))
                
                result = cursor.fetchone()
                conn.commit()
                
                if result:
                    return Property(
                        id=result['id'],
                        user_id=result['user_id'],
                        name=result['name'],
                        address=result['address'],
                        rent_amount=result['rent_amount'],
                        due_day=result['due_day'],
                        frequency=result['frequency'],
                        tenant_nickname=result['tenant_nickname'],
                        created_at=result['created_at']
                    )
                return None
        except Exception as e:
            print(f"Error creating property: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get all properties for a user"""
        conn = get_db_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, user_id, name, address, rent_amount, due_day, frequency, tenant_nickname, created_at
                    FROM properties WHERE user_id = %s ORDER BY name
                """, (user_id,))
                
                results = cursor.fetchall()
                properties = []
                
                for result in results:
                    properties.append(Property(
                        id=result['id'],
                        user_id=result['user_id'],
                        name=result['name'],
                        address=result['address'],
                        rent_amount=result['rent_amount'],
                        due_day=result['due_day'],
                        frequency=result['frequency'],
                        tenant_nickname=result['tenant_nickname'],
                        created_at=result['created_at']
                    ))
                
                return properties
        except Exception as e:
            print(f"Error getting properties by user ID: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_by_id(property_id):
        """Get property by ID"""
        conn = get_db_connection()
        if not conn:
            return None
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, user_id, name, address, rent_amount, due_day, frequency, tenant_nickname, created_at
                    FROM properties WHERE id = %s
                """, (property_id,))
                
                result = cursor.fetchone()
                if result:
                    return Property(
                        id=result['id'],
                        user_id=result['user_id'],
                        name=result['name'],
                        address=result['address'],
                        rent_amount=result['rent_amount'],
                        due_day=result['due_day'],
                        frequency=result['frequency'],
                        tenant_nickname=result['tenant_nickname'],
                        created_at=result['created_at']
                    )
                return None
        except Exception as e:
            print(f"Error getting property by ID: {e}")
            return None
        finally:
            conn.close()
    
    def update(self, name=None, address=None, rent_amount=None, due_day=None, frequency=None, tenant_nickname=None):
        """Update property details"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = %s")
                params.append(name)
                self.name = name
                
            if address is not None:
                updates.append("address = %s")
                params.append(address)
                self.address = address
                
            if rent_amount is not None:
                updates.append("rent_amount = %s")
                params.append(rent_amount)
                self.rent_amount = rent_amount
                
            if due_day is not None:
                updates.append("due_day = %s")
                params.append(due_day)
                self.due_day = due_day
                
            if frequency is not None:
                updates.append("frequency = %s")
                params.append(frequency)
                self.frequency = frequency
                
            if tenant_nickname is not None:
                updates.append("tenant_nickname = %s")
                params.append(tenant_nickname)
                self.tenant_nickname = tenant_nickname
            
            if not updates:
                return True
                
            params.append(self.id)
            
            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE properties SET {', '.join(updates)} WHERE id = %s
                """, params)
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating property: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def delete(self):
        """Delete property"""
        conn = get_db_connection()
        if not conn:
            return False
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM properties WHERE id = %s", (self.id,))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting property: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'address': self.address,
            'rent_amount': float(self.rent_amount) if self.rent_amount else None,
            'due_day': self.due_day,
            'frequency': self.frequency,
            'tenant_nickname': self.tenant_nickname,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }