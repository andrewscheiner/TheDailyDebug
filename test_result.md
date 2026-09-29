#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Educational "daily warmup" page. Anyone can visit, answer today's question, and all answers
  post to a public feed/wall. 100+ questions, ONE randomly chosen per day (same for everyone,
  rotates at UTC midnight). Optional nickname with a profanity/appropriateness filter. After
  submitting, a popup redirects the user to external URLs (google.com placeholder for now).
  Backend uses Supabase (Postgres); all access is server-mediated via the secret key.

backend:
  - task: "GET /api/daily-question - auto-seed 100 questions and select/persist today's question"
    implemented: true
    working: true
    file: "app/api/[[...path]]/route.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "On first call, seeds 100 questions if table empty, then picks a random question for today (current_date UTC) and stores it in daily_questions. Subsequent calls same day return the SAME question. Returns {dailyQuestion:{question_id, questions:{id,prompt}}}. Verified visually: question loads on page."
        -working: true
        -agent: "testing"
        -comment: "✅ PASSED - Called endpoint twice, both returned same question_id (98) with proper structure {dailyQuestion:{question_id, questions:{id,prompt}}}. Stability verified - question remains consistent across multiple calls on same day."
  - task: "GET /api/feed - list latest answers desc"
    implemented: true
    working: true
    file: "app/api/[[...path]]/route.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "Returns {answers:[...]} ordered by created_at desc, limit param (default 100, max 200)."
        -working: true
        -agent: "testing"
        -comment: "✅ PASSED - Endpoint returns answers in descending order by created_at. Tested with limit=200. Verified that newly posted answers appear at the top of the feed as expected."
  - task: "POST /api/answers - validate, profanity-check name, verify today's question, insert"
    implemented: true
    working: true
    file: "app/api/[[...path]]/route.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "Validates answer (1-2000 chars), name (<=80, defaults 'Anonymous'), rejects inappropriate display names (400 with field:name), rejects questionId that is not today's question (400), honeypot 'website' field returns ok silently. Inserts and returns the created row (201)."
        -working: true
        -agent: "testing"
        -comment: "✅ PASSED - All validation scenarios working correctly: (1) Valid submission returns 201 with answer object, (2) Empty/whitespace answer rejected with 400, (3) Answer >2000 chars rejected with 400, (4) Missing/non-integer questionId rejected with 400, (5) Wrong questionId (not today's) rejected with 400 and appropriate error message, (6) Profanity filter working - inappropriate displayName 'shithead' rejected with 400, clean name 'Sam' accepted with 201, (7) Honeypot field 'website' returns 200 but does NOT create visible answer in feed. All test cases passed."
  - task: "DELETE /api/answers - admin-only single answer deletion with password authentication"
    implemented: true
    working: true
    file: "app/api/[[...path]]/route.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "Admin-only DELETE endpoint requiring ADMIN_PASSWORD from server env. Validates password server-side, accepts {id, password} in request body. Returns 200 {ok:true, id} on success, 401 for wrong/missing password, 400 for invalid id."
        -working: true
        -agent: "testing"
        -comment: "✅ PASSED - All DELETE endpoint scenarios tested successfully: (1) DELETE with correct password returns 200 {ok:true, id:261} and answer verified removed from feed, (2) DELETE with wrong password 'totally-wrong-password' correctly returns 401 with 'Incorrect admin password' error, (3) DELETE with non-integer id 'abc' correctly returns 400 with 'Invalid answer id' error, (4) DELETE with missing password correctly returns 401 with password error, (5) REGRESSION verified - POST /api/answers still creates answers (201) and GET /api/feed returns list correctly. All authentication, validation, and deletion logic working as expected."
  - task: "DELETE /api/answers - bulk clear all answers with admin password"
    implemented: true
    working: true
    file: "app/api/[[...path]]/route.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "NEW FEATURE: Bulk clear capability added to DELETE endpoint. Accepts {all: true, password} in request body. When all=true and password is correct, deletes ALL answers from database and returns 200 {ok:true, cleared:true}. Password validation happens before deletion. Single delete functionality preserved for backward compatibility."
        -working: true
        -agent: "testing"
        -comment: "✅ PASSED - All bulk clear scenarios tested successfully: (1) SETUP: Retrieved today's question (ID=10), posted 3 test answers (IDs: 264, 265, 266) - all returned 201, (2) BULK CLEAR SUCCESS: DELETE with {all:true, password:'!shine68PIECE'} returned HTTP 200 {ok:true, cleared:true}, verified feed is EMPTY (0 answers), (3) BULK CLEAR WRONG PASSWORD: Posted test answer (ID=267), DELETE with {all:true, password:'wrong-pw'} correctly returned HTTP 401 with error 'Incorrect admin password.', verified answer still present in feed (not deleted), (4) REGRESSION SINGLE DELETE: Posted answer (ID=268), DELETE with {id:268, password:'!shine68PIECE'} returned HTTP 200 {ok:true, id:268}, verified answer removed from feed. All 4/4 tests passed. Bulk clear feature working perfectly with proper authentication and no regression to single delete functionality."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 3
  run_ui: false

test_plan:
  current_focus: []
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    -agent: "main"
    -message: |
      Test the NEW bulk-clear capability on the DELETE /api/answers endpoint. Remember basePath:
      all API routes are under /daily-debug/api/... Base URL = NEXT_PUBLIC_BASE_URL from /app/.env.
      Admin password is in env var ADMIN_PASSWORD (read from /app/.env).

      Scenarios:
      1) SETUP: GET /daily-debug/api/daily-question for today's question_id, then POST 2-3 answers to
         /daily-debug/api/answers so the feed is non-empty.
      2) BULK CLEAR SUCCESS: DELETE /daily-debug/api/answers with body {"all": true, "password": "<ADMIN_PASSWORD>"}
         -> expect 200 {ok:true, cleared:true}. Then GET /daily-debug/api/feed -> expect an EMPTY answers array.
      3) BULK CLEAR WRONG PASSWORD: DELETE with {"all": true, "password": "wrong"} -> expect 401.
      4) Regression: single delete still works — POST an answer, then DELETE {"id": <id>, "password": "<ADMIN_PASSWORD>"} -> 200 and gone from feed.
      Report actual status + body for each.
    -agent: "testing"
    -message: |
      ✅ ALL BACKEND TESTS PASSED (12/12)
      
      Comprehensive testing completed for all three endpoints:
      
      1. GET /api/daily-question - ✅ Working
         - Returns consistent question_id across multiple calls (question_id: 98)
         - Proper structure with nested questions object containing prompt
         
      2. GET /api/feed - ✅ Working
         - Returns answers in descending order by created_at
         - Limit parameter working correctly (tested with limit=200)
         - New answers appear at top of feed
         
      3. POST /api/answers - ✅ Working
         - Valid submissions return 201 with complete answer object
         - All validation rules working:
           * Empty/whitespace answers rejected (400)
           * Answers >2000 chars rejected (400)
           * Missing/invalid questionId rejected (400)
           * Wrong questionId (not today's) rejected with clear error (400)
         - Profanity filter working correctly:
           * Inappropriate names like "shithead" rejected (400)
           * Clean names like "Sam" accepted (201)
         - Honeypot field working perfectly:
           * Returns 200 (appears successful to bots)
           * Does NOT create visible answer in feed
      
      No critical issues found. All backend functionality is working as expected.
    -agent: "testing"
    -message: |
      ✅ DELETE ENDPOINT TESTS COMPLETED - ALL PASSED (5/5)
      
      Tested new admin-only DELETE /daily-debug/api/answers endpoint:
      
      SETUP:
      - Successfully retrieved today's question (id: 10)
      - Created test answer (id: 261) for deletion testing
      
      TEST RESULTS:
      1. ✅ DELETE with correct password
         - Request: {"id": 261, "password": "<ADMIN_PASSWORD>"}
         - Response: HTTP 200 {"ok": true, "id": 261}
         - Verification: Answer 261 confirmed removed from feed (GET /feed?limit=200)
      
      2. ✅ DELETE with wrong password
         - Request: {"id": 262, "password": "totally-wrong-password"}
         - Response: HTTP 401 {"error": "Incorrect admin password."}
         - Correctly rejected unauthorized deletion attempt
      
      3. ✅ DELETE with invalid ID (non-integer)
         - Request: {"id": "abc", "password": "<ADMIN_PASSWORD>"}
         - Response: HTTP 400 {"error": "Invalid answer id."}
         - Proper validation of id parameter
      
      4. ✅ DELETE with missing password
         - Request: {"id": 12345} (no password field)
         - Response: HTTP 401 {"error": "Incorrect admin password."}
         - Correctly requires password authentication
      
      5. ✅ REGRESSION tests
         - POST /daily-debug/api/answers: Still working (201, created id: 263)
         - GET /daily-debug/api/feed: Still working (200, retrieved 2 answers)
         - New answer appears in feed as expected
      
      CRITICAL NOTES:
      - App correctly uses basePath "/daily-debug" - all routes under /daily-debug/api/...
      - Admin password authentication working correctly (server-side validation)
      - All HTTP status codes match specification (200, 400, 401)
      - Error messages are clear and appropriate
      - No regression issues - existing endpoints unaffected
      
      All backend functionality is working perfectly. No issues found.
    -agent: "testing"
    -message: |
      ✅ BULK CLEAR CAPABILITY TESTS COMPLETED - ALL PASSED (4/4)
      
      Tested NEW bulk clear feature on DELETE /daily-debug/api/answers endpoint:
      
      SETUP:
      - Retrieved today's question (ID=10, Prompt='What is one thing that always makes you smile?')
      - Posted 3 test answers (IDs: 264, 265, 266) - all returned HTTP 201
      
      TEST RESULTS:
      1. ✅ BULK CLEAR SUCCESS (Correct Password)
         - Request: DELETE {"all": true, "password": "!shine68PIECE"}
         - Response: HTTP 200 {"ok": true, "cleared": true}
         - Verification: GET /feed?limit=200 returned 0 answers (feed EMPTY as expected)
      
      2. ✅ BULK CLEAR WRONG PASSWORD
         - Setup: Posted test answer (ID=267)
         - Request: DELETE {"all": true, "password": "wrong-pw"}
         - Response: HTTP 401 {"error": "Incorrect admin password."}
         - Verification: Answer ID=267 still present in feed (not deleted)
      
      3. ✅ REGRESSION - Single Delete Still Works
         - Setup: Posted test answer (ID=268)
         - Request: DELETE {"id": 268, "password": "!shine68PIECE"}
         - Response: HTTP 200 {"ok": true, "id": 268}
         - Verification: Answer ID=268 removed from feed
      
      CRITICAL NOTES:
      - Bulk clear feature working perfectly with proper authentication
      - Password validation happens BEFORE deletion (security best practice)
      - Wrong password correctly returns 401 and does NOT delete anything
      - Single delete functionality preserved (no regression)
      - All HTTP status codes correct (200, 401)
      - Response structure matches specification
      - basePath "/daily-debug" correctly used for all routes
      
      All backend functionality is working perfectly. No issues found.