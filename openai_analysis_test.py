#!/usr/bin/env python3
"""
OpenAI Integration and AI Analysis Testing for Lead Generation System
Focuses specifically on testing the new OpenAI API key and AI analysis functionality
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

print(f"Testing OpenAI Integration at: {API_BASE_URL}")

class OpenAIAnalysisTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.analysis_lead_id = None
    
    def log_result(self, test_name, success, message="", response=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if response and not success:
            print(f"   Response: {response.status_code} - {response.text[:300]}")
        
        if success:
            self.test_results['passed'] += 1
        else:
            self.test_results['failed'] += 1
            self.test_results['errors'].append(f"{test_name}: {message}")
        print()
    
    def test_openai_authentication(self):
        """Test 1: OpenAI Authentication Test"""
        print("=== Test 1: OpenAI Authentication Test ===")
        try:
            # Create a simple lead with minimal content to test OpenAI connectivity
            test_content = "Test company looking for business solutions. Recent activity shows growth potential."
            
            lead_data = {
                "company_name": "OpenAI Test Corp",
                "industry": "Technology",
                "company_size": "10-50 employees",
                "decision_maker_name": "Test Manager",
                "decision_maker_title": "CEO",
                "manual_content": test_content
            }
            
            response = self.session.post(f"{API_BASE_URL}/leads", json=lead_data)
            
            if response.status_code == 200:
                data = response.json()
                test_lead_id = data["id"]
                
                # Wait for analysis to complete
                print("   Waiting for OpenAI analysis to complete...")
                max_wait = 30  # 30 seconds max wait
                wait_time = 0
                
                while wait_time < max_wait:
                    time.sleep(2)
                    wait_time += 2
                    
                    check_response = self.session.get(f"{API_BASE_URL}/leads/{test_lead_id}")
                    if check_response.status_code == 200:
                        check_data = check_response.json()
                        analysis_status = check_data.get('analysis_status', 'unknown')
                        print(f"   Analysis status after {wait_time}s: {analysis_status}")
                        
                        if analysis_status == "completed":
                            self.log_result("OpenAI Authentication", True, 
                                          "OpenAI API key is working correctly - analysis completed successfully")
                            # Clean up test lead
                            self.session.delete(f"{API_BASE_URL}/leads/{test_lead_id}")
                            return True
                        elif analysis_status == "failed":
                            self.log_result("OpenAI Authentication", False, 
                                          "OpenAI API authentication failed - analysis status is 'failed'")
                            # Clean up test lead
                            self.session.delete(f"{API_BASE_URL}/leads/{test_lead_id}")
                            return False
                
                # If we get here, analysis didn't complete in time
                final_check = self.session.get(f"{API_BASE_URL}/leads/{test_lead_id}")
                if final_check.status_code == 200:
                    final_data = final_check.json()
                    final_status = final_data.get('analysis_status', 'unknown')
                    self.log_result("OpenAI Authentication", False, 
                                  f"Analysis timed out after {max_wait}s. Final status: {final_status}")
                # Clean up test lead
                self.session.delete(f"{API_BASE_URL}/leads/{test_lead_id}")
                
            else:
                self.log_result("OpenAI Authentication", False, f"Failed to create test lead: HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("OpenAI Authentication", False, f"Error: {str(e)}")
        return False
    
    def test_comprehensive_ai_analysis(self):
        """Test 2: Comprehensive AI Analysis with Realistic Business Scenario"""
        print("=== Test 2: Comprehensive AI Analysis ===")
        try:
            # Use the realistic business scenario from the review request
            business_content = """
            Company: ScaleUp Manufacturing Corp
            Industry: Manufacturing & Logistics
            
            Recent LinkedIn activity shows CEO posting about: 'Our production line efficiency dropped 15% this quarter due to equipment downtime. Looking for predictive maintenance solutions.' Posted 2 weeks ago about supply chain disruptions affecting delivery schedules. 
            
            Company blog mentions expanding to 3 new facilities but struggling with inventory management across locations. Job postings for Operations Manager and IT Director suggest rapid scaling challenges. 
            
            Recent company announcement about $5M investment round to modernize operations.
            
            Additional context:
            - Manufacturing equipment showing signs of aging
            - Supply chain visibility issues causing customer complaints
            - Inventory management systems not integrated across facilities
            - Rapid expansion creating operational bottlenecks
            - Investment funding available for technology solutions
            - Leadership actively seeking solutions (recent LinkedIn posts)
            - Hiring for key operational roles indicates growth phase
            """
            
            lead_data = {
                "company_name": "ScaleUp Manufacturing Corp",
                "industry": "Manufacturing & Logistics",
                "company_size": "200-500 employees",
                "decision_maker_name": "Robert Martinez",
                "decision_maker_title": "CEO",
                "linkedin_url": "https://linkedin.com/in/robert-martinez-ceo",
                "manual_content": business_content
            }
            
            response = self.session.post(f"{API_BASE_URL}/leads", json=lead_data)
            
            if response.status_code == 200:
                data = response.json()
                self.analysis_lead_id = data["id"]
                initial_status = data.get('analysis_status', 'unknown')
                
                self.log_result("Lead Creation for Analysis", True, 
                              f"Lead created successfully. Initial status: {initial_status}")
                
                # Monitor the analysis workflow
                print("   Monitoring analysis workflow...")
                max_wait = 45  # 45 seconds for comprehensive analysis
                wait_time = 0
                status_transitions = []
                
                while wait_time < max_wait:
                    time.sleep(3)
                    wait_time += 3
                    
                    check_response = self.session.get(f"{API_BASE_URL}/leads/{self.analysis_lead_id}")
                    if check_response.status_code == 200:
                        check_data = check_response.json()
                        analysis_status = check_data.get('analysis_status', 'unknown')
                        
                        if not status_transitions or status_transitions[-1] != analysis_status:
                            status_transitions.append(analysis_status)
                            print(f"   Status transition after {wait_time}s: {analysis_status}")
                        
                        if analysis_status == "completed":
                            print("   ✅ Analysis completed successfully!")
                            
                            # Validate the analysis results
                            return self.validate_analysis_results(check_data, status_transitions)
                        elif analysis_status == "failed":
                            self.log_result("Comprehensive AI Analysis", False, 
                                          f"Analysis failed. Status transitions: {' -> '.join(status_transitions)}")
                            return False
                
                # Analysis didn't complete in time
                self.log_result("Comprehensive AI Analysis", False, 
                              f"Analysis timed out after {max_wait}s. Status transitions: {' -> '.join(status_transitions)}")
                return False
                
            else:
                self.log_result("Comprehensive AI Analysis", False, f"Failed to create lead: HTTP {response.status_code}", response)
        except Exception as e:
            self.log_result("Comprehensive AI Analysis", False, f"Error: {str(e)}")
        return False
    
    def validate_analysis_results(self, lead_data, status_transitions):
        """Validate the AI analysis results"""
        print("   === Validating Analysis Results ===")
        
        # Check status transitions
        expected_transitions = ["pending", "analyzing", "completed"]
        if status_transitions == expected_transitions:
            print("   ✅ Status workflow correct: pending -> analyzing -> completed")
        else:
            print(f"   ⚠️  Status workflow: {' -> '.join(status_transitions)} (expected: {' -> '.join(expected_transitions)})")
        
        # Validate pain points
        pain_points = lead_data.get('pain_points', [])
        if len(pain_points) > 0:
            print(f"   ✅ Pain points extracted: {len(pain_points)} found")
            for i, pp in enumerate(pain_points[:3]):  # Show first 3
                urgency = pp.get('urgency', 0)
                category = pp.get('category', 'unknown')
                description = pp.get('description', '')[:100]
                print(f"      {i+1}. Urgency: {urgency}/5, Category: {category}")
                print(f"         Description: {description}...")
                
                # Validate urgency scale
                if 1 <= urgency <= 5:
                    print(f"         ✅ Urgency score valid (1-5 scale)")
                else:
                    print(f"         ❌ Urgency score invalid: {urgency} (should be 1-5)")
        else:
            print("   ❌ No pain points extracted")
            return False
        
        # Validate coldness scoring
        coldness_score = lead_data.get('coldness_score')
        if coldness_score is not None:
            if 1 <= coldness_score <= 10:
                print(f"   ✅ Coldness score: {coldness_score}/10 (valid range)")
            else:
                print(f"   ❌ Coldness score invalid: {coldness_score} (should be 1-10)")
                return False
        else:
            print("   ❌ Coldness score missing")
            return False
        
        # Validate total lead score
        total_score = lead_data.get('total_lead_score')
        if total_score is not None:
            print(f"   ✅ Total lead score: {total_score}/10")
            
            # Validate scoring categorization
            if total_score >= 8:
                category = "HOT"
            elif total_score >= 5:
                category = "WARM"
            else:
                category = "COLD"
            print(f"   ✅ Lead category: {category}")
        else:
            print("   ❌ Total lead score missing")
            return False
        
        # Validate outreach angle
        outreach_angle = lead_data.get('best_outreach_angle', '')
        if outreach_angle and len(outreach_angle) > 10:
            print(f"   ✅ Outreach angle generated: {outreach_angle[:100]}...")
        else:
            print("   ❌ Outreach angle missing or too short")
            return False
        
        # Validate recent activity summary
        activity_summary = lead_data.get('recent_activity_summary', '')
        if activity_summary:
            print(f"   ✅ Activity summary: {activity_summary[:100]}...")
        else:
            print("   ⚠️  Activity summary missing")
        
        self.log_result("Analysis Results Validation", True, 
                      f"All analysis components validated successfully. Score: {total_score}, Category: {category}")
        return True
    
    def test_scoring_system_validation(self):
        """Test 3: Validate Scoring System Formula"""
        print("=== Test 3: Scoring System Validation ===")
        
        if not self.analysis_lead_id:
            self.log_result("Scoring System Validation", False, "No analysis lead available")
            return False
        
        try:
            # Get the analyzed lead
            response = self.session.get(f"{API_BASE_URL}/leads/{self.analysis_lead_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract scoring components
                pain_points = data.get('pain_points', [])
                coldness_score = data.get('coldness_score', 5)
                total_score = data.get('total_lead_score', 0)
                
                if pain_points:
                    # Calculate expected score using the user's formula
                    avg_urgency = sum(pp.get('urgency', 3) for pp in pain_points) / len(pain_points)
                    
                    # User's scoring formula:
                    # Pain Point Urgency × 40% + Platform Activity × 30% + Company Fit × 20% + Contact Quality × 10%
                    pain_point_score = (avg_urgency / 5) * 10  # Convert to 0-10 scale
                    activity_score = 11 - coldness_score  # Invert coldness (lower coldness = higher activity)
                    company_fit = 7  # Default assumption
                    contact_quality = 5  # Default assumption
                    
                    expected_score = (
                        (pain_point_score * 0.4) +
                        (activity_score * 0.3) +
                        (company_fit * 0.2) +
                        (contact_quality * 0.1)
                    )
                    
                    print(f"   Scoring breakdown:")
                    print(f"   - Average pain point urgency: {avg_urgency:.2f}/5")
                    print(f"   - Pain point score (40%): {pain_point_score:.2f} * 0.4 = {pain_point_score * 0.4:.2f}")
                    print(f"   - Coldness score: {coldness_score}/10")
                    print(f"   - Activity score (30%): {activity_score:.2f} * 0.3 = {activity_score * 0.3:.2f}")
                    print(f"   - Company fit (20%): {company_fit} * 0.2 = {company_fit * 0.2:.2f}")
                    print(f"   - Contact quality (10%): {contact_quality} * 0.1 = {contact_quality * 0.1:.2f}")
                    print(f"   - Expected total: {expected_score:.2f}")
                    print(f"   - Actual total: {total_score}")
                    
                    # Allow for small rounding differences
                    if abs(expected_score - total_score) <= 0.1:
                        self.log_result("Scoring System Validation", True, 
                                      f"Scoring formula validated. Expected: {expected_score:.2f}, Actual: {total_score}")
                        return True
                    else:
                        self.log_result("Scoring System Validation", False, 
                                      f"Scoring mismatch. Expected: {expected_score:.2f}, Actual: {total_score}")
                        return False
                else:
                    self.log_result("Scoring System Validation", False, "No pain points available for validation")
                    return False
            else:
                self.log_result("Scoring System Validation", False, f"Failed to retrieve lead: HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Scoring System Validation", False, f"Error: {str(e)}")
        return False
    
    def test_lead_categorization(self):
        """Test 4: Lead Quality Categorization"""
        print("=== Test 4: Lead Quality Categorization ===")
        
        if not self.analysis_lead_id:
            self.log_result("Lead Quality Categorization", False, "No analysis lead available")
            return False
        
        try:
            # Get the analyzed lead
            response = self.session.get(f"{API_BASE_URL}/leads/{self.analysis_lead_id}")
            
            if response.status_code == 200:
                data = response.json()
                total_score = data.get('total_lead_score', 0)
                
                # Test categorization logic
                if total_score >= 8:
                    expected_category = "HOT"
                    expected_range = "8-10"
                elif total_score >= 5:
                    expected_category = "WARM"
                    expected_range = "5-7"
                else:
                    expected_category = "COLD"
                    expected_range = "1-4"
                
                print(f"   Lead score: {total_score}")
                print(f"   Category: {expected_category} (range: {expected_range})")
                
                # Validate the categorization makes sense for our test scenario
                # ScaleUp Manufacturing Corp should be a good lead (WARM or HOT)
                if total_score >= 5:
                    self.log_result("Lead Quality Categorization", True, 
                                  f"Lead properly categorized as {expected_category} with score {total_score}")
                    return True
                else:
                    self.log_result("Lead Quality Categorization", False, 
                                  f"Unexpected low score {total_score} for high-potential manufacturing lead")
                    return False
            else:
                self.log_result("Lead Quality Categorization", False, f"Failed to retrieve lead: HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Lead Quality Categorization", False, f"Error: {str(e)}")
        return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        if self.analysis_lead_id:
            try:
                self.session.delete(f"{API_BASE_URL}/leads/{self.analysis_lead_id}")
                print("   Test data cleaned up")
            except:
                pass
    
    def run_openai_tests(self):
        """Run all OpenAI-focused tests"""
        print("🤖 Starting OpenAI Integration and AI Analysis Tests")
        print("=" * 60)
        
        # Test sequence focused on OpenAI functionality
        tests = [
            self.test_openai_authentication,
            self.test_comprehensive_ai_analysis,
            self.test_scoring_system_validation,
            self.test_lead_categorization
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                print(f"❌ CRITICAL ERROR in {test.__name__}: {str(e)}")
                self.test_results['failed'] += 1
                self.test_results['errors'].append(f"{test.__name__}: Critical error - {str(e)}")
        
        # Clean up
        self.cleanup_test_data()
        
        # Final results
        print("=" * 60)
        print("🏁 OPENAI INTEGRATION TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results['passed'] + self.test_results['failed'] > 0:
            success_rate = (self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed']) * 100)
            print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.test_results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.test_results['errors']:
                print(f"   • {error}")
        
        return self.test_results['failed'] == 0

if __name__ == "__main__":
    tester = OpenAIAnalysisTester()
    success = tester.run_openai_tests()
    
    if success:
        print("\n🎉 All OpenAI integration tests passed! AI analysis is working correctly.")
        exit(0)
    else:
        print(f"\n⚠️  {tester.test_results['failed']} OpenAI test(s) failed. Check the issues above.")
        exit(1)