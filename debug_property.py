#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from database_sqlite import get_db_connection, init_db
    from models.property import Property
    from decimal import Decimal
    
    print("Testing property creation...")
    
    # Test database connection
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database")
        exit(1)
    print("OK - Database connection successful")
    
    # Test property creation
    try:
        property_obj = Property.create_property(
            user_id=1,
            keyword="RENT-123TEST",
            address="123 Test Street, Auckland",
            rent_amount=Decimal("650.00"),
            due_day="friday",
            frequency="weekly",
            tenant_nickname="John & Mary"
        )
        
        if property_obj:
            print("OK - Property created successfully!")
            print(f"Property ID: {property_obj.id}")
            print(f"Keyword: {property_obj.keyword}")
            print(f"Address: {property_obj.address}")
            print(f"Rent: ${property_obj.rent_amount}")
            print(f"Due Day: {property_obj.due_day}")
            print(f"Frequency: {property_obj.frequency}")
            print(f"Balance: ${property_obj.balance}")
        else:
            print("ERROR - Property creation failed - returned None")
            
    except Exception as e:
        import traceback
        print(f"ERROR - Property creation failed with error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        
except Exception as e:
    print(f"Failed to import modules: {e}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")