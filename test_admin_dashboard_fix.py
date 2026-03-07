#!/usr/bin/env python3
"""Test script to verify admin dashboard database queries work correctly"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from blueprints.lostlink_bp import Report, Return, LostLinkAdmin

def test_admin_dashboard_queries():
    """Test that admin dashboard queries work with the fixed code"""
    with app.app_context():
        print("Testing LostLink Admin Dashboard Database Queries...")
        print("=" * 60)
        
        try:
            # Test 1: Count total reports
            print("\n1. Testing total_reports query...")
            total_reports = db.session.query(Report).count()
            print(f"   ✓ Total reports: {total_reports}")
            
            # Test 2: Count total returned
            print("\n2. Testing total_returned query...")
            total_returned = db.session.query(Return).count()
            print(f"   ✓ Total returned: {total_returned}")
            
            # Test 3: Get recent reports
            print("\n3. Testing recent_reports query...")
            recent_reports = db.session.query(Report).order_by(Report.timestamp.desc()).limit(10).all()
            print(f"   ✓ Recent reports retrieved: {len(recent_reports)} records")
            if recent_reports:
                report = recent_reports[0]
                print(f"     - First report: {report.item} at {report.place}")
            
            # Test 4: Get recent returns
            print("\n4. Testing recent_returns query...")
            recent_returns = db.session.query(Return).order_by(Return.timestamp_claimed.desc()).limit(10).all()
            print(f"   ✓ Recent returns retrieved: {len(recent_returns)} records")
            if recent_returns:
                ret = recent_returns[0]
                print(f"     - First return: {ret.item_name} claimed by {ret.claimed_by}")
            
            # Test 5: Calculate statistics
            print("\n5. Testing statistics calculation...")
            pending = max(0, total_reports - total_returned)
            if total_reports > 0:
                success_rate = round((total_returned / total_reports) * 100, 1)
            else:
                success_rate = 0
            print(f"   ✓ Pending items: {pending}")
            print(f"   ✓ Success rate: {success_rate}%")
            
            # Test 6: Create stats dictionary (like in the route)
            print("\n6. Testing stats dictionary creation...")
            stats = {
                'total_reports': total_reports,
                'total_returned': total_returned,
                'pending': pending,
                'success_rate': success_rate,
                'recent_reports': recent_reports,
                'recent_returns': recent_returns
            }
            print(f"   ✓ Stats dictionary created successfully")
            print(f"     - Keys: {list(stats.keys())}")
            
            print("\n" + "=" * 60)
            print("✓ ALL TESTS PASSED - Dashboard database connection is working!")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n✗ ERROR: {str(e)}")
            print("=" * 60)
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_admin_dashboard_queries()
    sys.exit(0 if success else 1)
