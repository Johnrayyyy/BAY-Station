"""
Database Verification Script
Check if data is being properly stored in LostLink database
"""

import sqlite3
import os

def check_lostlink_database():
    """Check LostLink database tables and data"""
    db_path = os.path.join('databases', 'lostlink.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return
    
    print(f"✅ Database found at: {db_path}")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\n📊 Tables in database: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "=" * 70)
        
        # Check Reports table
        print("\n📋 REPORTS TABLE:")
        cursor.execute("SELECT COUNT(*) FROM reports")
        report_count = cursor.fetchone()[0]
        print(f"  Total Reports: {report_count}")
        
        if report_count > 0:
            cursor.execute("SELECT id, item, place, description, timestamp, report_by FROM reports ORDER BY timestamp DESC LIMIT 5")
            reports = cursor.fetchall()
            print("\n  Recent Reports:")
            for report in reports:
                print(f"    ID: {report[0]} | Item: {report[1]} | Place: {report[2]}")
                print(f"       Description: {report[3]}")
                print(f"       Timestamp: {report[4]} | Reported by: {report[5]}")
                print()
        else:
            print("  ⚠️  No reports in database")
        
        print("=" * 70)
        
        # Check Returns table
        print("\n📦 RETURNS TABLE:")
        cursor.execute("SELECT COUNT(*) FROM returns")
        return_count = cursor.fetchone()[0]
        print(f"  Total Returns: {return_count}")
        
        if return_count > 0:
            cursor.execute("SELECT id, item_name, claimed_by, contact, timestamp_claimed FROM returns ORDER BY timestamp_claimed DESC LIMIT 5")
            returns = cursor.fetchall()
            print("\n  Recent Returns:")
            for ret in returns:
                print(f"    ID: {ret[0]} | Item: {ret[1]} | Claimed by: {ret[2]}")
                print(f"       Contact: {ret[3]} | Date: {ret[4]}")
                print()
        else:
            print("  ⚠️  No returns in database")
        
        print("=" * 70)
        
        # Check Users table
        print("\n👤 USERS TABLE:")
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"  Total Users: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT sr_code, name, email FROM users LIMIT 5")
            users = cursor.fetchall()
            print("\n  Sample Users:")
            for user in users:
                print(f"    SR Code: {user[0]} | Name: {user[1]} | Email: {user[2]}")
        else:
            print("  ⚠️  No users in database")
        
        print("=" * 70)
        
        # Check Admins table
        print("\n🔑 ADMINS TABLE:")
        cursor.execute("SELECT COUNT(*) FROM admins")
        admin_count = cursor.fetchone()[0]
        print(f"  Total Admins: {admin_count}")
        
        if admin_count > 0:
            cursor.execute("SELECT id, username FROM admins")
            admins = cursor.fetchall()
            print("\n  Admins:")
            for admin in admins:
                print(f"    ID: {admin[0]} | Username: {admin[1]}")
        else:
            print("  ⚠️  No admins in database")
        
        print("\n" + "=" * 70)
        
        # Summary
        print("\n📊 SUMMARY:")
        print(f"  ✓ Reports: {report_count}")
        print(f"  ✓ Returns: {return_count}")
        print(f"  ✓ Pending: {report_count - return_count}")
        if report_count > 0:
            success_rate = (return_count / report_count) * 100
            print(f"  ✓ Success Rate: {success_rate:.1f}%")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading database: {str(e)}")

def check_rgo_database():
    """Check RGO database tables and data"""
    db_path = os.path.join('databases', 'rgo.db')
    
    if not os.path.exists(db_path):
        print(f"\n❌ RGO Database not found at: {db_path}")
        return
    
    print(f"\n\n{'=' * 70}")
    print("RGO DATABASE")
    print("=" * 70)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check Users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"\n👤 RGO Users: {user_count}")
        
        # Check Products
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        print(f"📦 Products: {product_count}")
        
        # Check Orders
        cursor.execute("SELECT COUNT(*) FROM orders")
        order_count = cursor.fetchone()[0]
        print(f"🛒 Orders: {order_count}")
        
        if order_count > 0:
            cursor.execute("SELECT id, user_id, total_amount, status, created_at FROM orders ORDER BY created_at DESC LIMIT 3")
            orders = cursor.fetchall()
            print("\n  Recent Orders:")
            for order in orders:
                print(f"    Order #{order[0]} | User: {order[1]} | Amount: PHP {order[2]} | Status: {order[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error reading RGO database: {str(e)}")

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DATABASE VERIFICATION - BSU KIOSK SYSTEM")
    print("=" * 70)
    
    check_lostlink_database()
    check_rgo_database()
    
    print("\n" + "=" * 70)
    print("✅ Database check complete!")
    print("=" * 70 + "\n")
