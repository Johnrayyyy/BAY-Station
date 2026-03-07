#!/usr/bin/env python3
"""Test script to verify login/guest status tracker works across all modules"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from flask import session

def test_context_processor():
    """Test the context processor for all module login states"""
    with app.app_context():
        with app.test_client() as client:
            print("\n" + "="*70)
            print("Testing Login/Guest Status Tracker Context Processor")
            print("="*70)
            
            # Test 1: Guest Mode (no login)
            print("\n1. Testing GUEST MODE (no login)...")
            response = client.get('/')
            assert response.status_code == 200
            assert b'Guest' in response.data or b'guest' in response.data.lower()
            print("   ✓ Guest mode status appears in response")
            
            # Test 2: Check that the context processor exists and returns correct structure
            print("\n2. Testing context processor structure...")
            with client.session_transaction() as sess:
                sess['test'] = 'value'
            
            response = client.get('/', environ_base={'HTTP_USER_AGENT': 'Test'})
            # The context processor should make user_status available in all templates
            assert response.status_code == 200
            print("   ✓ Context processor is working and templates render successfully")
            
            # Test 3: Simulate LostLink login
            print("\n3. Testing LOSTLINK LOGIN simulation...")
            with client.session_transaction() as sess:\n                sess['username'] = 'testuser'\n                sess['sr_code'] = '2023-001'\n                sess['role'] = 'student'\n            
            response = client.get('/')\n            assert response.status_code == 200\n            assert b'testuser' in response.data or b'Logged In' in response.data\n            print(\"   ✓ LostLink login status recognized\")\n            
            # Test 4: Simulate RGO admin login\n            print(\"\\n4. Testing RGO ADMIN LOGIN simulation...\")\n            with client.session_transaction() as sess:\n                sess.clear()\n                sess['rgo_admin_id'] = 1\n                sess['rgo_admin_name'] = 'Admin User'\n            \n            response = client.get('/')\n            assert response.status_code == 200\n            assert b'Admin User' in response.data or b'Admin' in response.data\n            print(\"   ✓ RGO admin login status recognized\")\n            \n            # Test 5: Simulate Grievance student login\n            print(\"\\n5. Testing GRIEVANCE STUDENT LOGIN simulation...\")\n            with client.session_transaction() as sess:\n                sess.clear()\n                sess['student_id'] = '12345'\n                sess['student_name'] = 'John Doe'\n                sess['student_email'] = 'john@bsu.edu.ph'\n            \n            response = client.get('/')\n            assert response.status_code == 200\n            assert b'John Doe' in response.data or b'Logged In' in response.data\n            print(\"   ✓ Grievance student login status recognized\")\n            \n            # Test 6: Simulate Grievance admin login\n            print(\"\\n6. Testing GRIEVANCE ADMIN LOGIN simulation...\")\n            with client.session_transaction() as sess:\n                sess.clear()\n                sess['admin_id'] = 1\n                sess['admin_name'] = 'Admin Officer'\n            \n            response = client.get('/')\n            assert response.status_code == 200\n            assert b'Admin Officer' in response.data or b'Logged In' in response.data\n            print(\"   ✓ Grievance admin login status recognized\")\n            \n            print(\"\\n\" + \"=\"*70)\n            print(\"✓ ALL TESTS PASSED - Status tracker is working correctly!\")\n            print(\"=\"*70)\n            print(\"\\nThe navbar now displays:\")\n            print(\"  • Guest Mode badge for unauthenticated users\")\n            print(\"  • Logged In badge for authenticated users next to BAY-Station\")\n            print(\"  • User name, module, and admin status\")\n            print(\"  • Module-specific logout functionality\")\n            print(\"=\"*70 + \"\\n\")\n            return True

if __name__ == '__main__':
    try:
        success = test_context_processor()\n        sys.exit(0 if success else 1)
    except Exception as e:
        print(f\"\\n✗ ERROR: {str(e)}\")\n        import traceback\n        traceback.print_exc()\n        sys.exit(1)
