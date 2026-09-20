#!/usr/bin/env python3
"""
Backend API tests for Daily Warmup application
Tests all three endpoints with various scenarios
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = os.getenv('NEXT_PUBLIC_BASE_URL', 'https://question-of-day-3.preview.emergentagent.com')
API_BASE = f"{BASE_URL}/api"

print(f"Testing backend at: {API_BASE}\n")
print("=" * 80)

# Track test results
test_results = {
    'passed': 0,
    'failed': 0,
    'errors': []
}

def log_test(name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if details:
        print(f"  Details: {details}")
    if passed:
        test_results['passed'] += 1
    else:
        test_results['failed'] += 1
        test_results['errors'].append(f"{name}: {details}")
    print()

# ============================================================================
# TEST 1: GET /api/daily-question - Call twice, verify same question_id
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: GET /api/daily-question - Stability check (same question_id)")
print("=" * 80)

try:
    # First call
    response1 = requests.get(f"{API_BASE}/daily-question", timeout=10)
    print(f"First call - Status: {response1.status_code}")
    print(f"Response: {response1.text[:500]}")
    
    if response1.status_code != 200:
        log_test("GET /api/daily-question (first call)", False, 
                f"Expected 200, got {response1.status_code}")
    else:
        data1 = response1.json()
        daily_q1 = data1.get('dailyQuestion')
        
        if not daily_q1:
            log_test("GET /api/daily-question (first call)", False, 
                    "dailyQuestion is null or missing")
        elif 'question_id' not in daily_q1:
            log_test("GET /api/daily-question (first call)", False, 
                    "question_id missing from dailyQuestion")
        elif 'questions' not in daily_q1 or not daily_q1['questions']:
            log_test("GET /api/daily-question (first call)", False, 
                    "questions nested object missing or null")
        elif 'prompt' not in daily_q1['questions']:
            log_test("GET /api/daily-question (first call)", False, 
                    "prompt missing from questions object")
        else:
            question_id_1 = daily_q1['question_id']
            prompt_1 = daily_q1['questions']['prompt']
            log_test("GET /api/daily-question (first call)", True, 
                    f"question_id={question_id_1}, prompt='{prompt_1[:50]}...'")
            
            # Second call
            response2 = requests.get(f"{API_BASE}/daily-question", timeout=10)
            print(f"Second call - Status: {response2.status_code}")
            print(f"Response: {response2.text[:500]}")
            
            if response2.status_code != 200:
                log_test("GET /api/daily-question (second call)", False, 
                        f"Expected 200, got {response2.status_code}")
            else:
                data2 = response2.json()
                daily_q2 = data2.get('dailyQuestion')
                
                if not daily_q2 or 'question_id' not in daily_q2:
                    log_test("GET /api/daily-question (second call)", False, 
                            "dailyQuestion or question_id missing")
                else:
                    question_id_2 = daily_q2['question_id']
                    
                    if question_id_1 == question_id_2:
                        log_test("GET /api/daily-question (stability)", True, 
                                f"Both calls returned same question_id: {question_id_1}")
                        # Save for later tests
                        TODAY_QUESTION_ID = question_id_1
                    else:
                        log_test("GET /api/daily-question (stability)", False, 
                                f"question_id changed: {question_id_1} -> {question_id_2}")
                        TODAY_QUESTION_ID = question_id_1  # Use first one anyway

except Exception as e:
    log_test("GET /api/daily-question", False, f"Exception: {str(e)}")
    TODAY_QUESTION_ID = None

# ============================================================================
# TEST 2: POST /api/answers - Valid submission
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: POST /api/answers - Valid submission")
print("=" * 80)

if TODAY_QUESTION_ID is None:
    log_test("POST /api/answers (valid)", False, 
            "Skipped - no question_id from previous test")
else:
    try:
        payload = {
            "questionId": TODAY_QUESTION_ID,
            "answer": "This is a test answer for the daily warmup question. I'm testing the backend API.",
            "displayName": "Alex"
        }
        
        response = requests.post(f"{API_BASE}/answers", json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code != 201:
            log_test("POST /api/answers (valid)", False, 
                    f"Expected 201, got {response.status_code}. Response: {response.text}")
        else:
            data = response.json()
            answer_obj = data.get('answer')
            
            if not answer_obj:
                log_test("POST /api/answers (valid)", False, 
                        "No 'answer' object in response")
            elif answer_obj.get('question_id') != TODAY_QUESTION_ID:
                log_test("POST /api/answers (valid)", False, 
                        f"question_id mismatch: expected {TODAY_QUESTION_ID}, got {answer_obj.get('question_id')}")
            elif answer_obj.get('answer') != payload['answer']:
                log_test("POST /api/answers (valid)", False, 
                        "Answer text doesn't match")
            elif answer_obj.get('display_name') != payload['displayName']:
                log_test("POST /api/answers (valid)", False, 
                        "display_name doesn't match")
            else:
                log_test("POST /api/answers (valid)", True, 
                        f"Created answer with id={answer_obj.get('id')}")
                CREATED_ANSWER_ID = answer_obj.get('id')
                
    except Exception as e:
        log_test("POST /api/answers (valid)", False, f"Exception: {str(e)}")
        CREATED_ANSWER_ID = None

# ============================================================================
# TEST 3: GET /api/feed - Verify answer appears at top
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: GET /api/feed - Verify posted answer appears at top")
print("=" * 80)

try:
    response = requests.get(f"{API_BASE}/feed?limit=200", timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response preview: {response.text[:300]}")
    
    if response.status_code != 200:
        log_test("GET /api/feed", False, 
                f"Expected 200, got {response.status_code}")
    else:
        data = response.json()
        answers = data.get('answers', [])
        
        if not isinstance(answers, list):
            log_test("GET /api/feed", False, 
                    "answers is not a list")
        elif len(answers) == 0:
            log_test("GET /api/feed", False, 
                    "No answers in feed (expected at least the one we just posted)")
        else:
            # Check if our answer is at the top
            top_answer = answers[0]
            if 'CREATED_ANSWER_ID' in globals() and CREATED_ANSWER_ID:
                if top_answer.get('id') == CREATED_ANSWER_ID:
                    log_test("GET /api/feed", True, 
                            f"Posted answer appears at top (id={CREATED_ANSWER_ID})")
                else:
                    # It might not be at the very top if other tests ran, but should be recent
                    found = any(a.get('id') == CREATED_ANSWER_ID for a in answers[:10])
                    if found:
                        log_test("GET /api/feed", True, 
                                f"Posted answer found in top 10 (id={CREATED_ANSWER_ID})")
                    else:
                        log_test("GET /api/feed", False, 
                                f"Posted answer not found in top 10 results")
            else:
                log_test("GET /api/feed", True, 
                        f"Feed returned {len(answers)} answers")
                
except Exception as e:
    log_test("GET /api/feed", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 4: Validation tests - expect 400 errors
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: Validation tests (expect 400 errors)")
print("=" * 80)

if TODAY_QUESTION_ID is None:
    print("Skipping validation tests - no question_id available")
else:
    # 4a: Empty answer
    try:
        payload = {
            "questionId": TODAY_QUESTION_ID,
            "answer": "   ",  # whitespace only
            "displayName": "TestUser"
        }
        response = requests.post(f"{API_BASE}/answers", json=payload, timeout=10)
        print(f"4a. Empty answer - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            log_test("Validation: empty answer", True, 
                    f"Correctly rejected with 400: {response.json().get('error', '')}")
        else:
            log_test("Validation: empty answer", False, 
                    f"Expected 400, got {response.status_code}")
    except Exception as e:
        log_test("Validation: empty answer", False, f"Exception: {str(e)}")
    
    # 4b: Answer > 2000 chars
    try:
        payload = {
            "questionId": TODAY_QUESTION_ID,
            "answer": "A" * 2001,  # 2001 characters
            "displayName": "TestUser"
        }
        response = requests.post(f"{API_BASE}/answers", json=payload, timeout=10)
        print(f"4b. Long answer - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            log_test("Validation: answer > 2000 chars", True, 
                    f"Correctly rejected with 400: {response.json().get('error', '')}")
        else:
            log_test("Validation: answer > 2000 chars", False, 
                    f"Expected 400, got {response.status_code}")
    except Exception as e:
        log_test("Validation: answer > 2000 chars", False, f"Exception: {str(e)}")
    
    # 4c: Missing questionId
    try:
        payload = {
            "answer": "Valid answer",
            "displayName": "TestUser"
        }
        response = requests.post(f"{API_BASE}/answers", json=payload, timeout=10)
        print(f"4c. Missing questionId - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            log_test("Validation: missing questionId", True, 
                    f"Correctly rejected with 400: {response.json().get('error', '')}")
        else:
            log_test("Validation: missing questionId", False, 
                    f"Expected 400, got {response.status_code}")
    except Exception as e:
        log_test("Validation: missing questionId", False, f"Exception: {str(e)}")
    
    # 4d: Non-integer questionId
    try:
        payload = {
            "questionId": "not-a-number",
            "answer": "Valid answer",
            "displayName": "TestUser"
        }
        response = requests.post(f"{API_BASE}/answers", json=payload, timeout=10)
        print(f"4d. Non-integer questionId - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            log_test("Validation: non-integer questionId", True, 
                    f"Correctly rejected with 400: {response.json().get('error', '')}")
        else:
            log_test("Validation: non-integer questionId", False, 
                    f"Expected 400, got {response.status_code}")
    except Exception as e:
        log_test("Validation: non-integer questionId", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 5: Wrong question - questionId not today's question
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: Wrong question test")
print("=" * 80)

if TODAY_QUESTION_ID is None:
    print("Skipping wrong question test - no question_id available")
else:
    try:
        wrong_id = TODAY_QUESTION_ID + 9999
        payload = {
            "questionId": wrong_id,
            "answer": "This is a valid answer but for the wrong question",
            "displayName": "TestUser"
        }
        response = requests.post(f"{API_BASE}/answers", json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            error_msg = response.json().get('error', '').lower()
            if 'today' in error_msg or 'question' in error_msg:
                log_test("Wrong question validation", True, 
                        f"Correctly rejected with 400: {response.json().get('error', '')}")
            else:
                log_test("Wrong question validation", False, 
                        f"Got 400 but error message unclear: {response.json().get('error', '')}")
        else:
            log_test("Wrong question validation", False, 
                    f"Expected 400, got {response.status_code}")
    except Exception as e:
        log_test("Wrong question validation", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 6: Profanity filter
# ============================================================================
print("\n" + "=" * 80)
print("TEST 6: Profanity/appropriateness filter")
print("=" * 80)

if TODAY_QUESTION_ID is None:
    print("Skipping profanity test - no question_id available")
else:
    # 6a: Inappropriate displayName
    try:
        payload = {
            "questionId": TODAY_QUESTION_ID,
            "answer": "This is a perfectly valid answer",
            "displayName": "shithead"
        }
        response = requests.post(f"{API_BASE}/answers", json=payload, timeout=10)
        print(f"6a. Inappropriate name - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            error_msg = response.json().get('error', '').lower()
            if 'appropriate' in error_msg or 'display name' in error_msg or 'name' in error_msg:
                log_test("Profanity filter: inappropriate name", True, 
                        f"Correctly rejected with 400: {response.json().get('error', '')}")
            else:
                log_test("Profanity filter: inappropriate name", False, 
                        f"Got 400 but error message unclear: {response.json().get('error', '')}")
        else:
            log_test("Profanity filter: inappropriate name", False, 
                    f"Expected 400, got {response.status_code}")
    except Exception as e:
        log_test("Profanity filter: inappropriate name", False, f"Exception: {str(e)}")
    
    # 6b: Clean displayName should work
    try:
        payload = {
            "questionId": TODAY_QUESTION_ID,
            "answer": "This is another test answer with a clean name",
            "displayName": "Sam"
        }
        response = requests.post(f"{API_BASE}/answers", json=payload, timeout=10)
        print(f"6b. Clean name - Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 201:
            log_test("Profanity filter: clean name accepted", True, 
                    f"Clean name 'Sam' correctly accepted")
        else:
            log_test("Profanity filter: clean name accepted", False, 
                    f"Expected 201, got {response.status_code}. Response: {response.text}")
    except Exception as e:
        log_test("Profanity filter: clean name accepted", False, f"Exception: {str(e)}")

# ============================================================================
# TEST 7: Honeypot field
# ============================================================================
print("\n" + "=" * 80)
print("TEST 7: Honeypot field test")
print("=" * 80)

if TODAY_QUESTION_ID is None:
    print("Skipping honeypot test - no question_id available")
else:
    try:
        # Get current feed count
        feed_before = requests.get(f"{API_BASE}/feed?limit=200", timeout=10)
        answers_before = feed_before.json().get('answers', [])
        count_before = len(answers_before)
        
        # Submit with honeypot field
        payload = {
            "questionId": TODAY_QUESTION_ID,
            "answer": "bot answer",
            "displayName": "Bot",
            "website": "spam"  # Honeypot field
        }
        response = requests.post(f"{API_BASE}/answers", json=payload, timeout=10)
        print(f"Honeypot submission - Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Should return 200 (ok) but not create answer
        if response.status_code == 200:
            # Check feed to verify no new answer
            feed_after = requests.get(f"{API_BASE}/feed?limit=200", timeout=10)
            answers_after = feed_after.json().get('answers', [])
            count_after = len(answers_after)
            
            if count_after == count_before:
                log_test("Honeypot: silently rejected", True, 
                        f"Returned 200 but did not create answer (feed count unchanged: {count_before})")
            else:
                # Check if the bot answer actually appears
                bot_answer_found = any(
                    a.get('display_name') == 'Bot' and a.get('answer') == 'bot answer' 
                    for a in answers_after[:5]
                )
                if bot_answer_found:
                    log_test("Honeypot: silently rejected", False, 
                            "Bot answer appears in feed - honeypot failed")
                else:
                    log_test("Honeypot: silently rejected", True, 
                            f"Returned 200, feed count changed but bot answer not visible")
        else:
            log_test("Honeypot: silently rejected", False, 
                    f"Expected 200, got {response.status_code}")
    except Exception as e:
        log_test("Honeypot: silently rejected", False, f"Exception: {str(e)}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total Passed: {test_results['passed']}")
print(f"Total Failed: {test_results['failed']}")

if test_results['failed'] > 0:
    print("\nFailed Tests:")
    for error in test_results['errors']:
        print(f"  - {error}")
    exit(1)
else:
    print("\n✅ All tests passed!")
    exit(0)
