#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Virtuoso Violin Learning App
Tests all endpoints defined in the backend server.py
"""

import requests
import json
import sys
from datetime import datetime, timezone

class VirtuosoAPITester:
    def __init__(self):
        self.base_url = "https://131f1459-9b96-467c-b28d-f74aef841d88.preview.emergentagent.com"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def run_test(self, name, method, endpoint, expected_status=200, data=None, validate_response=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                self.log(f"❌ Unsupported method: {method}")
                return False, None

            success = response.status_code == expected_status
            response_data = None
            
            try:
                response_data = response.json()
            except:
                response_data = None

            if success:
                # Additional validation if provided
                if validate_response and response_data:
                    validation_result = validate_response(response_data)
                    if not validation_result:
                        success = False
                        self.log(f"❌ Response validation failed for {name}")
                
                if success:
                    self.tests_passed += 1
                    self.log(f"✅ {name} - Status: {response.status_code}")
                else:
                    self.failed_tests.append(f"{name} - Validation failed")
                    self.log(f"❌ {name} - Validation failed")
            else:
                self.failed_tests.append(f"{name} - Expected {expected_status}, got {response.status_code}")
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                if response_data:
                    self.log(f"    Response: {response_data}")

            return success, response_data

        except Exception as e:
            self.failed_tests.append(f"{name} - Error: {str(e)}")
            self.log(f"❌ {name} - Error: {str(e)}")
            return False, None

    def test_health_endpoint(self):
        """Test health endpoint"""
        def validate_health(data):
            return data.get('status') == 'ok' and 'service' in data
        
        return self.run_test("Health Check", "GET", "/api/health", 200, validate_response=validate_health)

    def test_lessons_endpoints(self):
        """Test lessons endpoints"""
        self.log("\n=== TESTING LESSONS ENDPOINTS ===")
        
        # Get all lessons
        def validate_lessons(data):
            return isinstance(data, list) and len(data) == 10
        
        success, lessons_data = self.run_test(
            "Get All Lessons", "GET", "/api/lessons", 200, validate_response=validate_lessons
        )
        
        if success and lessons_data:
            # Test specific lesson detail
            first_lesson_id = lessons_data[0].get('id', 'lesson-1')
            
            def validate_lesson_detail(data):
                return (data.get('id') == first_lesson_id and 
                       'content' in data and isinstance(data['content'], list) and
                       'youtube_id' in data)
            
            self.run_test(
                f"Get Lesson Detail ({first_lesson_id})", "GET", f"/api/lessons/{first_lesson_id}", 
                200, validate_response=validate_lesson_detail
            )

    def test_theory_endpoints(self):
        """Test theory endpoints"""
        self.log("\n=== TESTING THEORY ENDPOINTS ===")
        
        # Get all theory topics
        def validate_theory(data):
            return isinstance(data, list) and len(data) == 6
        
        success, theory_data = self.run_test(
            "Get All Theory Topics", "GET", "/api/theory", 200, validate_response=validate_theory
        )
        
        if success and theory_data:
            # Test specific theory topic detail
            first_topic_id = theory_data[0].get('id', 'theory-1')
            
            def validate_theory_detail(data):
                return (data.get('id') == first_topic_id and 
                       'content' in data and isinstance(data['content'], list))
            
            self.run_test(
                f"Get Theory Topic Detail ({first_topic_id})", "GET", f"/api/theory/{first_topic_id}", 
                200, validate_response=validate_theory_detail
            )

    def test_sheet_music_endpoints(self):
        """Test sheet music endpoints"""
        self.log("\n=== TESTING SHEET MUSIC ENDPOINTS ===")
        
        # Get all sheet music
        def validate_sheet_music(data):
            return isinstance(data, list) and len(data) == 12
        
        success, sheet_data = self.run_test(
            "Get All Sheet Music", "GET", "/api/sheet-music", 200, validate_response=validate_sheet_music
        )
        
        # Test filtering by difficulty
        def validate_beginner_sheets(data):
            return isinstance(data, list) and all(item.get('difficulty') == 'beginner' for item in data)
        
        self.run_test(
            "Get Beginner Sheet Music", "GET", "/api/sheet-music?difficulty=beginner", 
            200, validate_response=validate_beginner_sheets
        )
        
        if success and sheet_data:
            # Test specific sheet music detail
            first_piece_id = sheet_data[0].get('id', 'sm-1')
            
            def validate_sheet_detail(data):
                return (data.get('id') == first_piece_id and 
                       'notes' in data and 'composer' in data)
            
            self.run_test(
                f"Get Sheet Music Detail ({first_piece_id})", "GET", f"/api/sheet-music/{first_piece_id}", 
                200, validate_response=validate_sheet_detail
            )

    def test_care_guides_endpoints(self):
        """Test care guides endpoints"""
        self.log("\n=== TESTING CARE GUIDES ENDPOINTS ===")
        
        # Get all care guides
        def validate_care_guides(data):
            return isinstance(data, list) and len(data) == 5
        
        success, care_data = self.run_test(
            "Get All Care Guides", "GET", "/api/care-guides", 200, validate_response=validate_care_guides
        )
        
        if success and care_data:
            # Test specific care guide detail
            first_guide_id = care_data[0].get('id', 'care-1')
            
            def validate_care_detail(data):
                return (data.get('id') == first_guide_id and 
                       'content' in data and isinstance(data['content'], list))
            
            self.run_test(
                f"Get Care Guide Detail ({first_guide_id})", "GET", f"/api/care-guides/{first_guide_id}", 
                200, validate_response=validate_care_detail
            )

    def test_practice_logs_endpoints(self):
        """Test practice logs endpoints"""
        self.log("\n=== TESTING PRACTICE LOGS ENDPOINTS ===")
        
        # Get existing practice logs
        success, logs_data = self.run_test("Get Practice Logs", "GET", "/api/practice-logs", 200)
        
        # Create a new practice log
        new_log_data = {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "duration_minutes": 30,
            "notes": "Test practice session",
            "lesson_id": "lesson-1"
        }
        
        def validate_new_log(data):
            return (data.get('date') == new_log_data['date'] and 
                   data.get('duration_minutes') == 30 and 
                   'id' in data)
        
        success, created_log = self.run_test(
            "Create Practice Log", "POST", "/api/practice-logs", 
            201, data=new_log_data, validate_response=validate_new_log
        )
        
        # Delete the created log if successful
        if success and created_log and 'id' in created_log:
            self.run_test(
                f"Delete Practice Log", "DELETE", f"/api/practice-logs/{created_log['id']}", 200
            )

    def test_bookmarks_endpoints(self):
        """Test bookmarks endpoints"""
        self.log("\n=== TESTING BOOKMARKS ENDPOINTS ===")
        
        # Get existing bookmarks
        success, bookmarks_data = self.run_test("Get Bookmarks", "GET", "/api/bookmarks", 200)
        
        # Create a new bookmark
        new_bookmark_data = {
            "item_id": "lesson-1",
            "item_type": "lesson",
            "title": "Test Bookmark"
        }
        
        def validate_new_bookmark(data):
            return (data.get('item_id') == 'lesson-1' and 
                   data.get('item_type') == 'lesson' and 
                   'id' in data)
        
        success, created_bookmark = self.run_test(
            "Create Bookmark", "POST", "/api/bookmarks", 
            201, data=new_bookmark_data, validate_response=validate_new_bookmark
        )
        
        # Delete the created bookmark if successful
        if success and created_bookmark and 'id' in created_bookmark:
            self.run_test(
                f"Delete Bookmark", "DELETE", f"/api/bookmarks/{created_bookmark['id']}", 200
            )

    def test_progress_endpoints(self):
        """Test progress endpoints"""
        self.log("\n=== TESTING PROGRESS ENDPOINTS ===")
        
        # Get existing progress
        success, progress_data = self.run_test("Get Progress", "GET", "/api/progress", 200)
        
        # Update progress
        progress_update_data = {
            "item_id": "lesson-1",
            "item_type": "lesson",
            "completed": True
        }
        
        def validate_progress_update(data):
            return (data.get('item_id') == 'lesson-1' and 
                   data.get('completed') == True)
        
        self.run_test(
            "Update Progress", "POST", "/api/progress", 
            200, data=progress_update_data, validate_response=validate_progress_update
        )

    def test_schedule_endpoints(self):
        """Test schedule endpoints"""
        self.log("\n=== TESTING SCHEDULE ENDPOINTS ===")
        
        # Get existing schedule
        success, schedule_data = self.run_test("Get Schedule", "GET", "/api/schedule", 200)
        
        # Create a new schedule entry
        new_schedule_data = {
            "day_of_week": 1,  # Monday
            "time": "10:00",
            "duration_minutes": 45,
            "focus_area": "Scales Practice"
        }
        
        def validate_new_schedule(data):
            return (data.get('day_of_week') == 1 and 
                   data.get('time') == '10:00' and 
                   'id' in data)
        
        success, created_schedule = self.run_test(
            "Create Schedule Entry", "POST", "/api/schedule", 
            201, data=new_schedule_data, validate_response=validate_new_schedule
        )
        
        # Delete the created schedule if successful
        if success and created_schedule and 'id' in created_schedule:
            self.run_test(
                f"Delete Schedule Entry", "DELETE", f"/api/schedule/{created_schedule['id']}", 200
            )

    def test_stats_endpoint(self):
        """Test stats endpoint"""
        self.log("\n=== TESTING STATS ENDPOINT ===")
        
        def validate_stats(data):
            required_fields = ['total_lessons', 'completed_lessons', 'total_theory', 
                             'completed_theory', 'total_practice_minutes', 'practice_streak', 
                             'total_sheet_music', 'bookmarks_count']
            return all(field in data for field in required_fields)
        
        self.run_test(
            "Get Stats", "GET", "/api/stats", 200, validate_response=validate_stats
        )

    def run_all_tests(self):
        """Run all backend tests"""
        self.log("🎻 Starting Virtuoso Backend API Tests...")
        self.log(f"Testing against: {self.base_url}")
        
        # Test all endpoints
        self.test_health_endpoint()
        self.test_lessons_endpoints()
        self.test_theory_endpoints()
        self.test_sheet_music_endpoints()
        self.test_care_guides_endpoints()
        self.test_practice_logs_endpoints()
        self.test_bookmarks_endpoints()
        self.test_progress_endpoints()
        self.test_schedule_endpoints()
        self.test_stats_endpoint()
        
        # Print results
        self.log(f"\n📊 RESULTS: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.failed_tests:
            self.log("\n❌ FAILED TESTS:")
            for failure in self.failed_tests:
                self.log(f"  - {failure}")
        
        return self.tests_passed == self.tests_run

def main():
    tester = VirtuosoAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())