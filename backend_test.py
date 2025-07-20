#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Lead Generation System
Tests all API endpoints with realistic business data
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://c84c520d-1762-489e-bb0d-6c5ed7a967cd.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

print(f"Testing backend API at: {API_BASE_URL}")

class LeadGenerationAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.test_lead_id = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if response and not success:
            print(f"   Response: {response.status_code} - {response.text[:200]}")
        
        if success:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
        print()
    
    def test_api_health_check(self):
        """Test 1: Basic API Health Check"""
        print("=== Test 1: API Health Check ===")
        try:
            response = self.session.get(f"{API_BASE_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "Lead Generation System API" in data["message"]:
                    self.log_result("API Health Check", True, f"API is running: {data['message']}")
                    return True
                else:
                    self.log_result("API Health Check", False, "Unexpected response format", response)
            else:
                self.log_result("API Health Check", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("API Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_create_lead_basic(self):
        """Test 2: Create Lead - Basic Data"""
        print("=== Test 2: Create Lead (Basic) ===")
        try:
            lead_data = {
                "company_name": "TechCorp Solutions",
                "industry": "Software Development",
                "company_size": "50-200 employees",
                "decision_maker_name": "Sarah Johnson",
                "decision_maker_title": "CTO",
                "linkedin_url": "https://linkedin.com/in/sarah-johnson-cto"
            }
            
            response = self.session.post(f"{API_BASE_URL}/leads", json=lead_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["company_name"] == lead_data["company_name"]:
                    self.test_lead_id = data["id"]
                    self.log_result("Create Lead (Basic)", True, f"Lead created with ID: {self.test_lead_id}")
                    return True
                else:
                    self.log_result("Create Lead (Basic)", False, "Invalid response structure", response)
            else:
                self.log_result("Create Lead (Basic)", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Lead (Basic)", False, f"Error: {str(e)}")
        return False
    
    def test_create_lead_with_ai_analysis(self):
        """Test 3: Create Lead with AI Analysis Content"""
        print("=== Test 3: Create Lead with AI Analysis ===")
        try:
            # Realistic business content for AI analysis
            manual_content = """
            TechCorp Solutions is a mid-sized software development company struggling with several operational challenges:
            
            Recent LinkedIn posts from their CTO Sarah Johnson indicate:
            - "Our development team is spending 40% of their time on manual testing processes"
            - "We're looking to scale our DevOps practices but lack the right automation tools"
            - "Client delivery timelines are being impacted by our current CI/CD pipeline limitations"
            
            Company announcements show:
            - Recently secured $2M Series A funding for expansion
            - Planning to double their engineering team in the next 6 months
            - Struggling with code quality consistency across multiple projects
            - Looking to implement better project management and collaboration tools
            
            Pain points identified:
            1. Manual testing processes causing delays
            2. Inadequate DevOps automation
            3. CI/CD pipeline bottlenecks
            4. Code quality inconsistencies
            5. Need for better project management tools
            6. Scaling challenges with rapid team growth
            
            The company appears to be in a growth phase with immediate needs for development tooling and process automation.
            """
            
            lead_data = {
                "company_name": "InnovateTech Industries",
                "industry": "Technology Services",
                "company_size": "100-500 employees",
                "decision_maker_name": "Michael Chen",
                "decision_maker_title": "VP of Engineering",
                "linkedin_url": "https://linkedin.com/in/michael-chen-vp-eng",
                "manual_content": manual_content
            }
            
            response = self.session.post(f"{API_BASE_URL}/leads", json=lead_data)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["company_name"] == lead_data["company_name"]:
                    ai_lead_id = data["id"]
                    self.log_result("Create Lead with AI Analysis", True, 
                                  f"Lead created with AI analysis trigger. ID: {ai_lead_id}, Status: {data.get('analysis_status', 'unknown')}")
                    
                    # Wait a moment and check if analysis started
                    time.sleep(2)
                    check_response = self.session.get(f"{API_BASE_URL}/leads/{ai_lead_id}")
                    if check_response.status_code == 200:
                        check_data = check_response.json()
                        analysis_status = check_data.get('analysis_status', 'unknown')
                        print(f"   Analysis status after 2s: {analysis_status}")
                        
                        # Wait longer for analysis to complete
                        if analysis_status == "analyzing":
                            print("   Waiting for AI analysis to complete...")
                            time.sleep(10)
                            final_check = self.session.get(f"{API_BASE_URL}/leads/{ai_lead_id}")
                            if final_check.status_code == 200:
                                final_data = final_check.json()
                                final_status = final_data.get('analysis_status', 'unknown')
                                print(f"   Final analysis status: {final_status}")
                                if final_status == "completed":
                                    pain_points = final_data.get('pain_points', [])
                                    coldness_score = final_data.get('coldness_score')
                                    total_score = final_data.get('total_lead_score')
                                    print(f"   Pain points found: {len(pain_points)}")
                                    print(f"   Coldness score: {coldness_score}")
                                    print(f"   Total lead score: {total_score}")
                    
                    return True
                else:
                    self.log_result("Create Lead with AI Analysis", False, "Invalid response structure", response)
            else:
                self.log_result("Create Lead with AI Analysis", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Create Lead with AI Analysis", False, f"Error: {str(e)}")
        return False
    
    def test_get_all_leads(self):
        """Test 4: Get All Leads"""
        print("=== Test 4: Get All Leads ===")
        try:
            response = self.session.get(f"{API_BASE_URL}/leads")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get All Leads", True, f"Retrieved {len(data)} leads")
                    return True
                else:
                    self.log_result("Get All Leads", False, "Response is not a list", response)
            else:
                self.log_result("Get All Leads", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get All Leads", False, f"Error: {str(e)}")
        return False
    
    def test_get_specific_lead(self):
        """Test 5: Get Specific Lead"""
        print("=== Test 5: Get Specific Lead ===")
        if not self.test_lead_id:
            self.log_result("Get Specific Lead", False, "No test lead ID available")
            return False
        
        try:
            response = self.session.get(f"{API_BASE_URL}/leads/{self.test_lead_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and data["id"] == self.test_lead_id:
                    self.log_result("Get Specific Lead", True, f"Retrieved lead: {data['company_name']}")
                    return True
                else:
                    self.log_result("Get Specific Lead", False, "Lead ID mismatch", response)
            else:
                self.log_result("Get Specific Lead", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Get Specific Lead", False, f"Error: {str(e)}")
        return False
    
    def test_update_lead(self):
        """Test 6: Update Lead"""
        print("=== Test 6: Update Lead ===")
        if not self.test_lead_id:
            self.log_result("Update Lead", False, "No test lead ID available")
            return False
        
        try:
            update_data = {
                "company_name": "TechCorp Solutions (Updated)",
                "industry": "Software Development & Consulting",
                "company_size": "200-500 employees",
                "decision_maker_name": "Sarah Johnson",
                "decision_maker_title": "Chief Technology Officer",
                "linkedin_url": "https://linkedin.com/in/sarah-johnson-cto"
            }
            
            response = self.session.put(f"{API_BASE_URL}/leads/{self.test_lead_id}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data["company_name"] == update_data["company_name"]:
                    self.log_result("Update Lead", True, f"Lead updated: {data['company_name']}")
                    return True
                else:
                    self.log_result("Update Lead", False, "Update not reflected", response)
            else:
                self.log_result("Update Lead", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Update Lead", False, f"Error: {str(e)}")
        return False
    
    def test_lead_statistics(self):
        """Test 7: Lead Statistics"""
        print("=== Test 7: Lead Statistics ===")
        try:
            response = self.session.get(f"{API_BASE_URL}/leads/stats/summary")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_leads", "hot_leads", "warm_leads", "cold_leads"]
                if all(field in data for field in required_fields):
                    self.log_result("Lead Statistics", True, 
                                  f"Stats: Total={data['total_leads']}, Hot={data['hot_leads']}, Warm={data['warm_leads']}, Cold={data['cold_leads']}")
                    return True
                else:
                    self.log_result("Lead Statistics", False, "Missing required fields", response)
            else:
                self.log_result("Lead Statistics", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Lead Statistics", False, f"Error: {str(e)}")
        return False
    
    def test_invalid_lead_data(self):
        """Test 8: Invalid Lead Data Validation"""
        print("=== Test 8: Data Validation ===")
        try:
            # Test with missing required field
            invalid_data = {
                "industry": "Technology",
                # Missing company_name
            }
            
            response = self.session.post(f"{API_BASE_URL}/leads", json=invalid_data)
            
            if response.status_code == 422:  # Validation error
                self.log_result("Data Validation", True, "Properly rejected invalid data")
                return True
            else:
                self.log_result("Data Validation", False, f"Expected 422, got {response.status_code}", response)
        except Exception as e:
            self.log_result("Data Validation", False, f"Error: {str(e)}")
        return False
    
    def test_nonexistent_lead(self):
        """Test 9: Access Non-existent Lead"""
        print("=== Test 9: Non-existent Lead Access ===")
        try:
            fake_id = str(uuid.uuid4())
            response = self.session.get(f"{API_BASE_URL}/leads/{fake_id}")
            
            if response.status_code == 404:
                self.log_result("Non-existent Lead Access", True, "Properly returned 404 for non-existent lead")
                return True
            else:
                self.log_result("Non-existent Lead Access", False, f"Expected 404, got {response.status_code}", response)
        except Exception as e:
            self.log_result("Non-existent Lead Access", False, f"Error: {str(e)}")
        return False
    
    def test_delete_lead(self):
        """Test 10: Delete Lead"""
        print("=== Test 10: Delete Lead ===")
        if not self.test_lead_id:
            self.log_result("Delete Lead", False, "No test lead ID available")
            return False
        
        try:
            response = self.session.delete(f"{API_BASE_URL}/leads/{self.test_lead_id}")
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "deleted" in data["message"].lower():
                    self.log_result("Delete Lead", True, "Lead deleted successfully")
                    
                    # Verify deletion
                    verify_response = self.session.get(f"{API_BASE_URL}/leads/{self.test_lead_id}")
                    if verify_response.status_code == 404:
                        print("   ✅ Deletion verified - lead no longer exists")
                    else:
                        print("   ⚠️  Warning: Lead still exists after deletion")
                    
                    return True
                else:
                    self.log_result("Delete Lead", False, "Unexpected response format", response)
            else:
                self.log_result("Delete Lead", False, f"HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Delete Lead", False, f"Error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Lead Generation System Backend API Tests")
        print("=" * 60)
        
        # Test sequence
        tests = [
            self.test_api_health_check,
            self.test_create_lead_basic,
            self.test_get_all_leads,
            self.test_get_specific_lead,
            self.test_update_lead,
            self.test_create_lead_with_ai_analysis,
            self.test_lead_statistics,
            self.test_invalid_lead_data,
            self.test_nonexistent_lead,
            self.test_delete_lead
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test.__name__}: {str(e)}")
                self.test_results['failed'] += 1
                self.test_results['errors'].append(f"{test.__name__}: Critical error - {str(e)}")
        
        # Final results
        print("=" * 60)
        print("🏁 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"📊 Success Rate: {(self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100):.1f}%")
        
        if self.test_results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = LeadGenerationAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Backend API is working correctly.")
        exit(0)
    else:
        print(f"\n⚠️  {tester.test_results['failed']} test(s) failed. Check the issues above.")
        exit(1)