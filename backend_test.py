#!/usr/bin/env python3
"""
Backend API Test Suite for Daily Debug App
Tests the admin-only DELETE endpoint for answers
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/.env')

BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

# CRITICAL: App uses basePath "/daily-debug"
API_BASE = f"{BASE_URL}/daily-debug/api"

print(f"🔧 Testing against: {API_BASE}")
print(f"🔑 Admin password loaded: {'✓' if ADMIN_PASSWORD else '✗'}")
print("=" * 80)

def test_delete_endpoint():
    """Test the admin-only DELETE /api/answers endpoint"""
    
    # ========================================================================
    # SETUP: Get today's question and create a test answer
    # ========================================================================
    print("\n📋 SETUP: Creating test answer for deletion...")
    print("-" * 80)
    
    try:
        # Step 1: Get today's question
        print("1️⃣  GET /daily-debug/api/daily-question")
        resp = requests.get(f"{API_BASE}/daily-question", timeout=10)
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"   ❌ FAILED: Expected 200, got {resp.status_code}")
            print(f"   Response: {resp.text}")
            return False
        
        data = resp.json()
        question_id = data.get('dailyQuestion', {}).get('question_id')
        print(f"   ✅ Got question_id: {question_id}")
        
        if not question_id:
            print("   ❌ FAILED: No question_id in response")
            return False
        
        # Step 2: POST a test answer
        print("\n2️⃣  POST /daily-debug/api/answers (create test answer)")
        test_payload = {
            "questionId": question_id,
            "answer": "Delete me test - this answer should be removed by admin",
            "displayName": "TempTestUser"
        }
        resp = requests.post(f"{API_BASE}/answers", json=test_payload, timeout=10)
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code != 201:
            print(f"   ❌ FAILED: Expected 201, got {resp.status_code}")
            print(f"   Response: {resp.text}")
            return False
        
        answer_data = resp.json()
        test_answer_id = answer_data.get('answer', {}).get('id')
        print(f"   ✅ Created answer with id: {test_answer_id}")
        print(f"   Answer: {answer_data}")
        
        if not test_answer_id:
            print("   ❌ FAILED: No answer id in response")
            return False
        
    except Exception as e:
        print(f"❌ SETUP FAILED: {str(e)}")
        return False
    
    # ========================================================================
    # TEST 1: DELETE SUCCESS - Delete with correct password
    # ========================================================================
    print("\n" + "=" * 80)
    print("🧪 TEST 1: DELETE with correct admin password")
    print("-" * 80)
    
    try:
        delete_payload = {
            "id": test_answer_id,
            "password": ADMIN_PASSWORD
        }
        print(f"DELETE /daily-debug/api/answers")
        print(f"Body: {{'id': {test_answer_id}, 'password': '***'}}")
        
        resp = requests.delete(f"{API_BASE}/answers", json=delete_payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
        if resp.status_code != 200:
            print(f"❌ FAILED: Expected 200, got {resp.status_code}")
            return False
        
        result = resp.json()
        if not result.get('ok') or result.get('id') != test_answer_id:
            print(f"❌ FAILED: Expected {{ok: true, id: {test_answer_id}}}")
            return False
        
        print("✅ DELETE returned success")
        
        # Verify the answer is gone from feed
        print("\n   Verifying answer is removed from feed...")
        resp = requests.get(f"{API_BASE}/feed?limit=200", timeout=10)
        if resp.status_code != 200:
            print(f"   ⚠️  Could not verify feed (status {resp.status_code})")
        else:
            feed_data = resp.json()
            answers = feed_data.get('answers', [])
            answer_ids = [a.get('id') for a in answers]
            
            if test_answer_id in answer_ids:
                print(f"   ❌ FAILED: Answer {test_answer_id} still exists in feed!")
                return False
            else:
                print(f"   ✅ Confirmed: Answer {test_answer_id} is NOT in feed (deleted successfully)")
        
        print("✅ TEST 1 PASSED")
        
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {str(e)}")
        return False
    
    # ========================================================================
    # TEST 2: DELETE with WRONG PASSWORD
    # ========================================================================
    print("\n" + "=" * 80)
    print("🧪 TEST 2: DELETE with incorrect admin password")
    print("-" * 80)
    
    try:
        # First create another test answer
        print("Creating another test answer...")
        test_payload = {
            "questionId": question_id,
            "answer": "Another test answer for wrong password test",
            "displayName": "TestUser2"
        }
        resp = requests.post(f"{API_BASE}/answers", json=test_payload, timeout=10)
        if resp.status_code == 201:
            test_id_2 = resp.json().get('answer', {}).get('id')
            print(f"Created answer id: {test_id_2}")
        else:
            test_id_2 = 999999  # Use a fake ID if creation fails
            print(f"Using fake id: {test_id_2}")
        
        delete_payload = {
            "id": test_id_2,
            "password": "totally-wrong-password"
        }
        print(f"\nDELETE /daily-debug/api/answers")
        print(f"Body: {{'id': {test_id_2}, 'password': 'totally-wrong-password'}}")
        
        resp = requests.delete(f"{API_BASE}/answers", json=delete_payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
        if resp.status_code != 401:
            print(f"❌ FAILED: Expected 401, got {resp.status_code}")
            return False
        
        result = resp.json()
        error_msg = result.get('error', '').lower()
        if 'password' not in error_msg and 'incorrect' not in error_msg:
            print(f"❌ FAILED: Expected password error message, got: {result.get('error')}")
            return False
        
        print("✅ TEST 2 PASSED - Correctly rejected wrong password with 401")
        
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {str(e)}")
        return False
    
    # ========================================================================
    # TEST 3: DELETE with INVALID ID (non-integer)
    # ========================================================================
    print("\n" + "=" * 80)
    print("🧪 TEST 3: DELETE with non-integer id")
    print("-" * 80)
    
    try:
        delete_payload = {
            "id": "abc",
            "password": ADMIN_PASSWORD
        }
        print(f"DELETE /daily-debug/api/answers")
        print(f"Body: {{'id': 'abc', 'password': '***'}}")
        
        resp = requests.delete(f"{API_BASE}/answers", json=delete_payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
        if resp.status_code != 400:
            print(f"❌ FAILED: Expected 400, got {resp.status_code}")
            return False
        
        result = resp.json()
        error_msg = result.get('error', '').lower()
        if 'invalid' not in error_msg and 'id' not in error_msg:
            print(f"⚠️  Warning: Expected 'invalid id' error message, got: {result.get('error')}")
        
        print("✅ TEST 3 PASSED - Correctly rejected invalid id with 400")
        
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {str(e)}")
        return False
    
    # ========================================================================
    # TEST 4: DELETE with MISSING PASSWORD
    # ========================================================================
    print("\n" + "=" * 80)
    print("🧪 TEST 4: DELETE with missing password")
    print("-" * 80)
    
    try:
        delete_payload = {
            "id": 12345
        }
        print(f"DELETE /daily-debug/api/answers")
        print(f"Body: {{'id': 12345}} (no password field)")
        
        resp = requests.delete(f"{API_BASE}/answers", json=delete_payload, timeout=10)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
        
        if resp.status_code != 401:
            print(f"❌ FAILED: Expected 401, got {resp.status_code}")
            return False
        
        result = resp.json()
        error_msg = result.get('error', '').lower()
        if 'password' not in error_msg:
            print(f"⚠️  Warning: Expected password error message, got: {result.get('error')}")
        
        print("✅ TEST 4 PASSED - Correctly rejected missing password with 401")
        
    except Exception as e:
        print(f"❌ TEST 4 FAILED: {str(e)}")
        return False
    
    # ========================================================================
    # TEST 5: REGRESSION - Verify POST and GET still work
    # ========================================================================
    print("\n" + "=" * 80)
    print("🧪 TEST 5: REGRESSION - Verify POST and GET endpoints still work")
    print("-" * 80)
    
    try:
        # Test POST
        print("Testing POST /daily-debug/api/answers...")
        test_payload = {
            "questionId": question_id,
            "answer": "Regression test answer - verifying POST still works",
            "displayName": "RegressionTester"
        }
        resp = requests.post(f"{API_BASE}/answers", json=test_payload, timeout=10)
        print(f"POST Status: {resp.status_code}")
        
        if resp.status_code != 201:
            print(f"❌ FAILED: POST endpoint broken, expected 201, got {resp.status_code}")
            print(f"Response: {resp.text}")
            return False
        
        regression_answer = resp.json().get('answer', {})
        regression_id = regression_answer.get('id')
        print(f"✅ POST working - Created answer id: {regression_id}")
        
        # Test GET feed
        print("\nTesting GET /daily-debug/api/feed...")
        resp = requests.get(f"{API_BASE}/feed?limit=50", timeout=10)
        print(f"GET Status: {resp.status_code}")
        
        if resp.status_code != 200:
            print(f"❌ FAILED: GET feed endpoint broken, expected 200, got {resp.status_code}")
            print(f"Response: {resp.text}")
            return False
        
        feed_data = resp.json()
        answers = feed_data.get('answers', [])
        print(f"✅ GET working - Retrieved {len(answers)} answers")
        
        # Verify our regression answer is in the feed
        answer_ids = [a.get('id') for a in answers]
        if regression_id in answer_ids:
            print(f"✅ Confirmed: New answer {regression_id} appears in feed")
        else:
            print(f"⚠️  Warning: New answer {regression_id} not found in feed (might be pagination)")
        
        print("✅ TEST 5 PASSED - POST and GET endpoints working correctly")
        
    except Exception as e:
        print(f"❌ TEST 5 FAILED: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 STARTING DELETE ENDPOINT TEST SUITE")
    print("=" * 80)
    
    success = test_delete_endpoint()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
