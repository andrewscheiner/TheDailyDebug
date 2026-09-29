#!/usr/bin/env python3
"""
Backend API Test Suite for The Daily Debug
Tests the new BULK CLEAR capability on DELETE /api/answers endpoint
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/.env')

BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'https://question-of-day-3.preview.emergentagent.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '!shine68PIECE')
BASE_PATH = '/daily-debug'

# API endpoints
API_BASE = f"{BASE_URL}{BASE_PATH}/api"
DAILY_QUESTION_URL = f"{API_BASE}/daily-question"
ANSWERS_URL = f"{API_BASE}/answers"
FEED_URL = f"{API_BASE}/feed"

print("=" * 80)
print("BACKEND API TEST SUITE - BULK CLEAR CAPABILITY")
print("=" * 80)
print(f"Base URL: {BASE_URL}")
print(f"Base Path: {BASE_PATH}")
print(f"API Base: {API_BASE}")
print(f"Admin Password: {'*' * len(ADMIN_PASSWORD)}")
print("=" * 80)

def test_setup():
    """Setup: Get today's question and post 3 test answers"""
    print("\n[SETUP] Getting today's question and posting 3 test answers...")
    
    # Get today's question
    try:
        response = requests.get(DAILY_QUESTION_URL)
        print(f"GET {DAILY_QUESTION_URL}")
        print(f"Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ SETUP FAILED: Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        question_id = data.get('dailyQuestion', {}).get('question_id')
        question_prompt = data.get('dailyQuestion', {}).get('questions', {}).get('prompt')
        
        if not question_id:
            print(f"❌ SETUP FAILED: No question_id in response")
            print(f"Response: {json.dumps(data, indent=2)}")
            return None
        
        print(f"✅ Got today's question: ID={question_id}, Prompt='{question_prompt}'")
        
    except Exception as e:
        print(f"❌ SETUP FAILED: Error getting daily question: {e}")
        return None
    
    # Post 3 test answers
    posted_ids = []
    for i in range(1, 4):
        try:
            payload = {
                "questionId": question_id,
                "answer": f"Bulk clear test answer {i} - This is a test answer for testing the bulk clear functionality.",
                "displayName": f"TestUser{i}"
            }
            response = requests.post(ANSWERS_URL, json=payload)
            print(f"\nPOST {ANSWERS_URL}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            print(f"Status: {response.status_code}")
            
            if response.status_code != 201:
                print(f"❌ SETUP WARNING: Expected 201, got {response.status_code}")
                print(f"Response: {response.text}")
            else:
                data = response.json()
                answer_id = data.get('answer', {}).get('id')
                posted_ids.append(answer_id)
                print(f"✅ Posted answer {i}: ID={answer_id}")
                
        except Exception as e:
            print(f"❌ SETUP WARNING: Error posting answer {i}: {e}")
    
    print(f"\n✅ SETUP COMPLETE: Posted {len(posted_ids)} answers")
    return question_id

def test_bulk_clear_success():
    """Test 1: Bulk clear with correct password should clear all answers"""
    print("\n" + "=" * 80)
    print("[TEST 1] BULK CLEAR SUCCESS - Correct Password")
    print("=" * 80)
    
    try:
        payload = {
            "all": True,
            "password": ADMIN_PASSWORD
        }
        
        print(f"\nDELETE {ANSWERS_URL}")
        print(f"Payload: {json.dumps({'all': True, 'password': '***'}, indent=2)}")
        
        response = requests.delete(ANSWERS_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print(f"❌ TEST 1 FAILED: Expected 200, got {response.status_code}")
            return False
        
        data = response.json()
        if not data.get('ok') or not data.get('cleared'):
            print(f"❌ TEST 1 FAILED: Expected {{ok: true, cleared: true}}, got {json.dumps(data)}")
            return False
        
        print(f"✅ Bulk clear returned correct response: {json.dumps(data)}")
        
        # Verify feed is empty
        print(f"\nVerifying feed is empty...")
        print(f"GET {FEED_URL}?limit=200")
        
        feed_response = requests.get(f"{FEED_URL}?limit=200")
        print(f"Status: {feed_response.status_code}")
        
        if feed_response.status_code != 200:
            print(f"❌ TEST 1 FAILED: Feed check failed with status {feed_response.status_code}")
            return False
        
        feed_data = feed_response.json()
        answers = feed_data.get('answers', [])
        print(f"Feed contains {len(answers)} answers")
        
        if len(answers) != 0:
            print(f"❌ TEST 1 FAILED: Expected empty feed, but found {len(answers)} answers")
            print(f"Answers: {json.dumps(answers, indent=2)}")
            return False
        
        print(f"✅ Feed is empty as expected")
        print("\n✅ TEST 1 PASSED: Bulk clear with correct password works correctly")
        return True
        
    except Exception as e:
        print(f"❌ TEST 1 FAILED: Exception occurred: {e}")
        return False

def test_bulk_clear_wrong_password(question_id):
    """Test 2: Bulk clear with wrong password should return 401 and not clear anything"""
    print("\n" + "=" * 80)
    print("[TEST 2] BULK CLEAR WRONG PASSWORD - Should Return 401")
    print("=" * 80)
    
    # First, post one answer to have something in the feed
    try:
        payload = {
            "questionId": question_id,
            "answer": "Test answer for wrong password scenario - should NOT be deleted",
            "displayName": "PasswordTestUser"
        }
        
        print(f"\nPosting test answer first...")
        print(f"POST {ANSWERS_URL}")
        response = requests.post(ANSWERS_URL, json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 201:
            print(f"❌ TEST 2 SETUP FAILED: Could not post test answer")
            return False
        
        data = response.json()
        answer_id = data.get('answer', {}).get('id')
        print(f"✅ Posted test answer: ID={answer_id}")
        
    except Exception as e:
        print(f"❌ TEST 2 SETUP FAILED: {e}")
        return False
    
    # Now try bulk clear with wrong password
    try:
        payload = {
            "all": True,
            "password": "wrong-pw"
        }
        
        print(f"\nAttempting bulk clear with wrong password...")
        print(f"DELETE {ANSWERS_URL}")
        print(f"Payload: {json.dumps({'all': True, 'password': 'wrong-pw'}, indent=2)}")
        
        response = requests.delete(ANSWERS_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 401:
            print(f"❌ TEST 2 FAILED: Expected 401, got {response.status_code}")
            return False
        
        data = response.json()
        if 'error' not in data:
            print(f"❌ TEST 2 FAILED: Expected error message in response")
            return False
        
        print(f"✅ Correctly returned 401 with error: {data.get('error')}")
        
        # Verify the answer is still present
        print(f"\nVerifying answer is still present in feed...")
        print(f"GET {FEED_URL}?limit=200")
        
        feed_response = requests.get(f"{FEED_URL}?limit=200")
        print(f"Status: {feed_response.status_code}")
        
        if feed_response.status_code != 200:
            print(f"❌ TEST 2 FAILED: Feed check failed")
            return False
        
        feed_data = feed_response.json()
        answers = feed_data.get('answers', [])
        print(f"Feed contains {len(answers)} answers")
        
        if len(answers) == 0:
            print(f"❌ TEST 2 FAILED: Answer was deleted despite wrong password!")
            return False
        
        # Check if our specific answer is present
        found = any(a.get('id') == answer_id for a in answers)
        if not found:
            print(f"❌ TEST 2 FAILED: Our test answer (ID={answer_id}) not found in feed")
            return False
        
        print(f"✅ Answer still present in feed (ID={answer_id})")
        print("\n✅ TEST 2 PASSED: Bulk clear with wrong password correctly rejected")
        return True
        
    except Exception as e:
        print(f"❌ TEST 2 FAILED: Exception occurred: {e}")
        return False

def test_regression_single_delete(question_id):
    """Test 3: Regression - Single delete should still work"""
    print("\n" + "=" * 80)
    print("[TEST 3] REGRESSION - Single Delete Still Works")
    print("=" * 80)
    
    # Post a test answer
    try:
        payload = {
            "questionId": question_id,
            "answer": "Test answer for single delete regression test",
            "displayName": "RegressionTestUser"
        }
        
        print(f"\nPosting test answer...")
        print(f"POST {ANSWERS_URL}")
        response = requests.post(ANSWERS_URL, json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code != 201:
            print(f"❌ TEST 3 SETUP FAILED: Could not post test answer")
            return False
        
        data = response.json()
        answer_id = data.get('answer', {}).get('id')
        print(f"✅ Posted test answer: ID={answer_id}")
        
    except Exception as e:
        print(f"❌ TEST 3 SETUP FAILED: {e}")
        return False
    
    # Delete the specific answer
    try:
        payload = {
            "id": answer_id,
            "password": ADMIN_PASSWORD
        }
        
        print(f"\nDeleting specific answer...")
        print(f"DELETE {ANSWERS_URL}")
        print(f"Payload: {json.dumps({'id': answer_id, 'password': '***'}, indent=2)}")
        
        response = requests.delete(ANSWERS_URL, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code != 200:
            print(f"❌ TEST 3 FAILED: Expected 200, got {response.status_code}")
            return False
        
        data = response.json()
        if not data.get('ok') or data.get('id') != answer_id:
            print(f"❌ TEST 3 FAILED: Expected {{ok: true, id: {answer_id}}}, got {json.dumps(data)}")
            return False
        
        print(f"✅ Single delete returned correct response: {json.dumps(data)}")
        
        # Verify the answer is gone from feed
        print(f"\nVerifying answer is removed from feed...")
        print(f"GET {FEED_URL}?limit=200")
        
        feed_response = requests.get(f"{FEED_URL}?limit=200")
        print(f"Status: {feed_response.status_code}")
        
        if feed_response.status_code != 200:
            print(f"❌ TEST 3 FAILED: Feed check failed")
            return False
        
        feed_data = feed_response.json()
        answers = feed_data.get('answers', [])
        print(f"Feed contains {len(answers)} answers")
        
        # Check if our specific answer is NOT present
        found = any(a.get('id') == answer_id for a in answers)
        if found:
            print(f"❌ TEST 3 FAILED: Answer (ID={answer_id}) still present in feed after deletion")
            return False
        
        print(f"✅ Answer correctly removed from feed (ID={answer_id})")
        print("\n✅ TEST 3 PASSED: Single delete regression test passed")
        return True
        
    except Exception as e:
        print(f"❌ TEST 3 FAILED: Exception occurred: {e}")
        return False

def main():
    """Run all tests"""
    results = {
        'setup': False,
        'bulk_clear_success': False,
        'bulk_clear_wrong_password': False,
        'regression_single_delete': False
    }
    
    # Setup
    question_id = test_setup()
    if question_id:
        results['setup'] = True
    else:
        print("\n❌ SETUP FAILED - Cannot proceed with tests")
        return results
    
    # Test 1: Bulk clear success
    results['bulk_clear_success'] = test_bulk_clear_success()
    
    # Test 2: Bulk clear wrong password
    results['bulk_clear_wrong_password'] = test_bulk_clear_wrong_password(question_id)
    
    # Test 3: Regression - single delete
    results['regression_single_delete'] = test_regression_single_delete(question_id)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, passed_flag in results.items():
        status = "✅ PASSED" if passed_flag else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print("=" * 80)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    main()
