from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from emergentintegrations.llm.chat import LlmChat, UserMessage
import asyncio
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# OpenAI setup
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Create the main app without a prefix
app = FastAPI(title="Lead Generation System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class PainPoint(BaseModel):
    description: str
    urgency: int = Field(ge=1, le=5)  # 1-5 urgency scale
    category: str

class Lead(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    decision_maker_name: Optional[str] = None
    decision_maker_title: Optional[str] = None
    linkedin_url: Optional[str] = None
    pain_points: List[PainPoint] = []
    recent_activity_summary: Optional[str] = None
    coldness_score: Optional[int] = Field(None, ge=1, le=10)
    total_lead_score: Optional[float] = None
    best_outreach_angle: Optional[str] = None
    contact_info_quality: Optional[int] = Field(None, ge=1, le=5)
    analysis_status: str = "pending"  # pending, analyzing, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LeadCreate(BaseModel):
    company_name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    decision_maker_name: Optional[str] = None
    decision_maker_title: Optional[str] = None
    linkedin_url: Optional[str] = None
    manual_content: Optional[str] = None  # Manual content for analysis

class ActivityData(BaseModel):
    linkedin_posts: Optional[str] = None
    blog_posts: Optional[str] = None
    recent_announcements: Optional[str] = None

async def analyze_with_gpt4(content: str, lead_data: dict) -> Dict[str, Any]:
    """Analyze content using GPT-4o to extract pain points and generate insights"""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        # Create chat instance
        chat = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=f"lead_analysis_{lead_data['id']}",
            system_message="""You are a B2B lead qualification expert. Your job is to analyze company information and identify business pain points, then provide actionable insights for sales outreach.

Your analysis should focus on:
1. Identifying specific business challenges and pain points
2. Ranking pain points by urgency (1-5 scale)
3. Categorizing pain points (operational, financial, technological, strategic, compliance)
4. Determining outreach strategies
5. Assessing lead quality

Be specific and actionable in your analysis."""
        ).with_model("openai", "gpt-4o")
        
        # Construct analysis prompt
        prompt = f"""
Analyze the following lead information and provide a comprehensive assessment:

COMPANY: {lead_data.get('company_name', 'Unknown')}
INDUSTRY: {lead_data.get('industry', 'Unknown')}
COMPANY SIZE: {lead_data.get('company_size', 'Unknown')}
DECISION MAKER: {lead_data.get('decision_maker_name', 'Unknown')} - {lead_data.get('decision_maker_title', 'Unknown')}

CONTENT TO ANALYZE:
{content}

Please provide your analysis in this exact JSON format:
{{
    "pain_points": [
        {{
            "description": "Specific pain point description",
            "urgency": 4,
            "category": "operational"
        }}
    ],
    "coldness_factors": {{
        "recent_activity": "Description of recent activity indicating engagement level",
        "business_challenges": "Current challenges mentioned",
        "growth_indicators": "Signs of growth or change"
    }},
    "coldness_score": 6,
    "best_outreach_angle": "Specific recommendation for initial outreach",
    "lead_quality_assessment": "Overall assessment of lead potential",
    "recommended_action": "immediate_outreach | nurture_campaign | long_term_nurture | skip"
}}

Focus on finding specific, actionable pain points that a B2B solution could address.
"""
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        # Extract JSON from response
        import json
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis_result = json.loads(json_match.group())
                return analysis_result
            else:
                # Fallback parsing
                return {
                    "pain_points": [{"description": "Analysis completed but formatting issue occurred", "urgency": 3, "category": "general"}],
                    "coldness_factors": {"recent_activity": "Unable to parse activity data"},
                    "coldness_score": 5,
                    "best_outreach_angle": response[:200] + "...",
                    "lead_quality_assessment": "Analysis completed with formatting issues",
                    "recommended_action": "nurture_campaign"
                }
        except json.JSONDecodeError:
            # Return basic analysis if JSON parsing fails
            return {
                "pain_points": [{"description": "Business challenges identified in content analysis", "urgency": 3, "category": "general"}],
                "coldness_factors": {"recent_activity": "Content analysis completed"},
                "coldness_score": 5,
                "best_outreach_angle": "Follow up based on content analysis",
                "lead_quality_assessment": "Moderate lead potential",
                "recommended_action": "nurture_campaign"
            }
            
    except Exception as e:
        logging.error(f"Error in GPT analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def calculate_lead_score(pain_point_urgency: float, coldness_score: int, company_fit: int = 7, contact_quality: int = 5) -> float:
    """Calculate total lead score based on the user's framework"""
    # Convert pain point urgency to 0-10 scale
    pain_point_score = (pain_point_urgency / 5) * 10
    
    # Invert coldness score (lower coldness = higher activity = better score)
    activity_score = 11 - coldness_score
    
    # Calculate weighted score
    total_score = (
        (pain_point_score * 0.4) +
        (activity_score * 0.3) +
        (company_fit * 0.2) +
        (contact_quality * 0.1)
    )
    
    return round(total_score, 2)

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Lead Generation System API", "version": "1.0"}

@api_router.post("/leads", response_model=Lead)
async def create_lead(lead_data: LeadCreate):
    """Create a new lead and start analysis"""
    lead_dict = lead_data.dict()
    lead_obj = Lead(**lead_dict)
    
    # Insert into database
    await db.leads.insert_one(lead_obj.dict())
    
    # Start background analysis if content provided
    if lead_data.manual_content:
        asyncio.create_task(analyze_lead_background(lead_obj.id, lead_data.manual_content, lead_obj.dict()))
    
    return lead_obj

async def analyze_lead_background(lead_id: str, content: str, lead_data: dict):
    """Background task to analyze lead"""
    try:
        # Update status to analyzing
        await db.leads.update_one(
            {"id": lead_id},
            {"$set": {"analysis_status": "analyzing", "updated_at": datetime.utcnow()}}
        )
        
        # Perform analysis
        analysis = await analyze_with_gpt4(content, lead_data)
        
        # Convert pain points
        pain_points = []
        for pp in analysis.get("pain_points", []):
            pain_points.append(PainPoint(**pp))
        
        # Calculate average urgency
        avg_urgency = sum(pp.urgency for pp in pain_points) / len(pain_points) if pain_points else 3
        
        # Calculate total score
        coldness_score = analysis.get("coldness_score", 5)
        total_score = calculate_lead_score(avg_urgency, coldness_score)
        
        # Update lead with analysis results
        update_data = {
            "pain_points": [pp.dict() for pp in pain_points],
            "coldness_score": coldness_score,
            "total_lead_score": total_score,
            "best_outreach_angle": analysis.get("best_outreach_angle", ""),
            "recent_activity_summary": analysis.get("coldness_factors", {}).get("recent_activity", ""),
            "analysis_status": "completed",
            "updated_at": datetime.utcnow()
        }
        
        await db.leads.update_one({"id": lead_id}, {"$set": update_data})
        
    except Exception as e:
        logging.error(f"Analysis failed for lead {lead_id}: {str(e)}")
        await db.leads.update_one(
            {"id": lead_id},
            {"$set": {"analysis_status": "failed", "updated_at": datetime.utcnow()}}
        )

@api_router.get("/leads", response_model=List[Lead])
async def get_leads():
    """Get all leads"""
    leads = await db.leads.find().sort("created_at", -1).to_list(1000)
    return [Lead(**lead) for lead in leads]

@api_router.get("/leads/{lead_id}", response_model=Lead)
async def get_lead(lead_id: str):
    """Get specific lead"""
    lead = await db.leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return Lead(**lead)

@api_router.put("/leads/{lead_id}", response_model=Lead)
async def update_lead(lead_id: str, lead_data: LeadCreate):
    """Update lead information"""
    update_data = lead_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.leads.update_one({"id": lead_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    updated_lead = await db.leads.find_one({"id": lead_id})
    return Lead(**updated_lead)

@api_router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str):
    """Delete a lead"""
    result = await db.leads.delete_one({"id": lead_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead deleted successfully"}

@api_router.post("/leads/{lead_id}/analyze")
async def trigger_analysis(lead_id: str, content: str):
    """Manually trigger analysis for a lead"""
    lead = await db.leads.find_one({"id": lead_id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Start background analysis
    asyncio.create_task(analyze_lead_background(lead_id, content, lead))
    
    return {"message": "Analysis started"}

@api_router.get("/leads/stats/summary")
async def get_lead_stats():
    """Get lead statistics"""
    total_leads = await db.leads.count_documents({})
    hot_leads = await db.leads.count_documents({"total_lead_score": {"$gte": 8}})
    warm_leads = await db.leads.count_documents({"total_lead_score": {"$gte": 5, "$lt": 8}})
    cold_leads = await db.leads.count_documents({"total_lead_score": {"$lt": 5}})
    
    return {
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "warm_leads": warm_leads,
        "cold_leads": cold_leads
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()