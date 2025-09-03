#!/usr/bin/env python3
"""
Test script for the Smart Rent Scheduler
Demonstrates ultra-cheap Akahu integration
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.smart_scheduler import SmartRentScheduler
from datetime import datetime, timedelta

def test_smart_scheduler():
    """Test the smart scheduler functionality"""
    print("Testing Smart Rent Scheduler")
    print("=" * 50)
    
    # Initialize scheduler with mock Akahu
    scheduler = SmartRentScheduler(use_mock_akahu=True)
    
    print("\n1. Getting properties due for check today...")
    properties_to_check = scheduler.get_properties_due_for_check_today()
    print(f"   Properties found: {len(properties_to_check)}")
    
    print("\n2. Running smart daily check...")
    results = scheduler.run_daily_smart_check()
    
    print(f"\nSmart Check Results:")
    print(f"   Properties checked: {results.get('properties_checked', 0)}")
    print(f"   API calls used: {results.get('api_calls_used', 0)}")
    print(f"   Estimated cost: ${results.get('total_cost', 0):.2f}")
    print(f"   Notifications sent: {results.get('notifications_sent', 0)}")
    print(f"   Successful checks: {results.get('successful_checks', 0)}")
    print(f"   Failed checks: {results.get('failed_checks', 0)}")
    
    print("\n3. Generating upcoming schedule...")
    schedule = scheduler.schedule_rent_checks()
    
    if schedule:
        print(f"\nNext 7 Rent Checks:")
        for item in schedule[:7]:
            print(f"   {item['check_date']} - {item['property_address']} (${item['rent_amount']}) - {item['frequency']}")
    else:
        print("   No upcoming checks found")
    
    # Cost projections
    weekly_properties = len([s for s in schedule[:7]])
    monthly_cost = (len(schedule) / 30) * 0.10 * 30 if schedule else 0  # Rough monthly estimate
    
    print(f"\nCost Projections:")
    print(f"   Weekly API calls: ~{weekly_properties}")
    print(f"   Estimated monthly cost: ~${monthly_cost:.2f}")
    if schedule:
        print(f"   Cost per property per month: ~${monthly_cost/max(1, len(schedule)/30):.2f}")

def demo_cost_comparison():
    """Demo showing cost comparison between approaches"""
    print("\nCost Comparison Demo")
    print("=" * 50)
    
    num_users = 100
    
    # Daily polling approach
    daily_calls = num_users * 30  # 30 days
    daily_cost = daily_calls * 0.10
    
    # Smart approach (weekly rent = 4 calls/month, monthly = 1 call/month)
    smart_calls = (num_users * 0.7 * 4) + (num_users * 0.3 * 1)  # 70% weekly, 30% monthly
    smart_cost = smart_calls * 0.10
    
    print(f"For {num_users} users:")
    print(f"   Daily polling: {daily_calls} calls/month = ${daily_cost:.2f}")
    print(f"   Smart scheduling: {smart_calls:.0f} calls/month = ${smart_cost:.2f}")
    print(f"   Savings: ${daily_cost - smart_cost:.2f}/month ({((daily_cost - smart_cost)/daily_cost)*100:.1f}% reduction)")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cost":
        demo_cost_comparison()
    else:
        test_smart_scheduler()
        demo_cost_comparison()