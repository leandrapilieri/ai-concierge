#!/usr/bin/env python3
"""
OpenAI Integration Test for Lead Generation System
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://c84c520d-1762-489e-bb0d-6c5ed7a967cd.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

def test_openai_integration():
    """Test OpenAI integration with realistic business content"""
    print("🔍 Testing OpenAI Integration...")
    
    # Create lead with substantial content for AI analysis
    lead_data = {
        "company_name": "DataFlow Analytics",
        "industry": "Data Analytics & Business Intelligence",
        "company_size": "50-200 employees",
        "decision_maker_name": "Jennifer Martinez",
        "decision_maker_title": "Chief Data Officer",
        "linkedin_url": "https://linkedin.com/in/jennifer-martinez-cdo",
        "manual_content": """
        DataFlow Analytics is experiencing rapid growth but facing significant data infrastructure challenges:
        
        Recent company updates:
        - CEO announced 150% revenue growth in Q4 2024
        - Planning to expand data science team by 300% in 2025
        - Struggling with data pipeline reliability issues
        - Current ETL processes taking 12+ hours to complete
        - Data quality issues affecting customer reporting accuracy
        
        Pain points from leadership team:
        1. Legacy data warehouse can't handle current data volumes
        2. Manual data validation processes causing delays
        3. Inconsistent data formats across different sources
        4. Lack of real-time analytics capabilities
        5. Compliance concerns with data governance
        6. High infrastructure costs with current cloud setup
        
        Recent LinkedIn activity shows urgency:
        - CDO posted about "urgent need for scalable data solutions"
        - Engineering team discussing migration to modern data stack
        - Multiple job postings for senior data engineers
        
        This appears to be a high-priority lead with immediate budget and decision-making authority.
        """
    }
    
    try:
        # Create lead
        response = requests.post(f"{API_BASE_URL}/leads", json=lead_data)
        
        if response.status_code == 200:
            data = response.json()
            lead_id = data["id"]
            print(f"✅ Lead created: {lead_id}")
            print(f"   Initial status: {data.get('analysis_status', 'unknown')}")
            
            # Monitor analysis progress
            for i in range(6):  # Check for up to 30 seconds
                time.sleep(5)
                check_response = requests.get(f"{API_BASE_URL}/leads/{lead_id}")
                
                if check_response.status_code == 200:
                    check_data = check_response.json()
                    status = check_data.get('analysis_status', 'unknown')
                    print(f"   Status after {(i+1)*5}s: {status}")
                    
                    if status == "completed":
                        print("✅ AI Analysis completed successfully!")
                        pain_points = check_data.get('pain_points', [])
                        coldness_score = check_data.get('coldness_score')
                        total_score = check_data.get('total_lead_score')
                        outreach_angle = check_data.get('best_outreach_angle', '')
                        
                        print(f"   📊 Results:")
                        print(f"      Pain points identified: {len(pain_points)}")
                        for pp in pain_points[:3]:  # Show first 3
                            print(f"        - {pp.get('description', 'N/A')} (Urgency: {pp.get('urgency', 'N/A')})")
                        print(f"      Coldness score: {coldness_score}")
                        print(f"      Total lead score: {total_score}")
                        print(f"      Outreach angle: {outreach_angle[:100]}...")
                        
                        return True
                        
                    elif status == "failed":
                        print("❌ AI Analysis failed!")
                        return False
                        
            print("⚠️  Analysis did not complete within 30 seconds")
            return False
            
        else:
            print(f"❌ Failed to create lead: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing OpenAI integration: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openai_integration()
    if not success:
        print("\n🚨 OpenAI Integration Issue Detected!")
        print("   This is likely due to an invalid or expired OpenAI API key.")
        print("   Check the OPENAI_API_KEY in /app/backend/.env")