from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
import time
import os

# Try to import the agent system, fall back to static responses if not available
try:
    from .bizpilot_agents import get_bizpilot_agents
    AGENTS_AVAILABLE = True
    print("BizPilot AI Agents loaded successfully!")
except ImportError as e:
    print(f"Warning: Could not load AI agents ({e}). Falling back to static responses.")
    AGENTS_AVAILABLE = False

# Static fallback responses (used when agents are not available)
STATIC_RESPONSES = [
    {
        "match": ["roadmap", "6-month", "6 month", "launch", "startup", "want"],
        "response": "We'll set up a customized 6‑month launch roadmap template for you. For now, you can record your idea via voice and we'll map it into milestones (no simulations yet). You'll receive: Month‑by‑month tasks, resource checklist, and basic risk tracker."
    },
    {
        "match": ["business plan", "plan", "strategy"],
        "response": "I'll help you create a comprehensive business plan. Please provide more details about your business idea, target market, and goals so I can give you specific guidance."
    },
    {
        "match": ["market", "competition", "competitor", "industry"],
        "response": "I can help with market analysis and competitive research. What industry or market are you looking to enter? I'll provide insights on market size, trends, and key competitors."
    },
    {
        "match": ["financial", "funding", "investment", "money", "revenue", "pricing"],
        "response": "I'll assist with financial planning and funding strategies. What specific financial aspect would you like help with? Revenue projections, funding requirements, or pricing strategy?"
    },
    {
        "match": ["incubator", "admin", "batch", "cohort", "aggregated", "dashboard"],
        "response": "We'll batch‑process your cohort's ideas and produce starter dashboards: submission counts, progress by phase, and top themes. You'll get a simple group performance view you can filter by team or week."
    }
]


def process_with_agents(message: str):
    """Process message using AI agents"""
    try:
        agents = get_bizpilot_agents(use_openai=True)  # Try OpenAI first
        
        # Check if this is a roadmap request for structured response
        msg_lower = message.lower()
        if any(keyword in msg_lower for keyword in ['roadmap', '6-month', '6 month', 'timeline', 'milestone']):
            return agents.generate_structured_roadmap(message)
        
        # For other queries, get regular response
        response_content = agents.process_query(message)
        
        return {
            "reply": response_content,
            "meta": {"agent_powered": True, "model": "ai"}
        }
        
    except Exception as e:
        print(f"Error with AI agents: {e}")
        # Fall back to static responses
        return process_with_static_responses(message)


def process_with_static_responses(message: str):
    """Process message using static responses (fallback)"""
    msg = (message or "").lower()
    print(f"DEBUG: Processing message with static responses: '{msg}'")
    
    for rule in STATIC_RESPONSES:
        if any(keyword in msg for keyword in rule["match"]):
            # If this is the roadmap intent, include structured roadmap
            if any(keyword in msg for keyword in ["roadmap", "6-month", "6 month", "timeline"]):
                roadmap = [
                    {"month": 1, "tasks": ["Define business idea", "Market research", "Set up legal structure"]},
                    {"month": 2, "tasks": ["Build MVP", "Create brand assets", "Open business accounts"]},
                    {"month": 3, "tasks": ["Launch MVP to early users", "Collect feedback", "Iterate product"]},
                    {"month": 4, "tasks": ["Start marketing campaigns", "Onboard first customers", "Track KPIs"]},
                    {"month": 5, "tasks": ["Expand features", "Partnership outreach", "Prepare for scale"]},
                    {"month": 6, "tasks": ["Full launch", "Analyze results", "Plan next phase"]}
                ]
                return {
                    "reply": rule["response"],
                    "roadmap": roadmap,
                    "meta": {"agent_powered": False, "model": "static"}
                }
            return {
                "reply": rule["response"],
                "meta": {"agent_powered": False, "model": "static"}
            }
    
    return {
        "reply": (
            "I'm here to help with your business planning needs! I can assist with:\n\n"
            "🗺️ **Roadmaps & Planning** - 6-month launch timelines and milestones\n"
            "📋 **Business Plans** - Comprehensive strategy and planning\n"
            "📊 **Market Analysis** - Industry research and competitive insights\n"
            "💰 **Financial Planning** - Funding strategies and revenue models\n\n"
            "What would you like to explore?"
        ),
        "meta": {"agent_powered": False, "model": "static"}
    }


def detect_intent(message: str):
    """Main intent detection and processing function"""
    print(f"DEBUG: Processing message: '{message}'")
    
    if AGENTS_AVAILABLE:
        print("DEBUG: Using AI agents for processing")
        return process_with_agents(message)
    else:
        print("DEBUG: Using static responses (agents not available)")
        return process_with_static_responses(message)


@csrf_exempt
def chat_api(request):
    print("=== CHAT_API CALLED ===")  # This should always show
    if request.method != 'POST':
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    user_message = data.get('message', '')
    print(f"CHAT_API: Received message: '{user_message}' at {time.time()}")

    response = detect_intent(user_message)
    print(f"CHAT_API: detect_intent returned: {response}")
    # Always include meta for compatibility
    if "meta" not in response:
        response["meta"] = {"matched": "roadmap" in user_message.lower() or "6-month" in user_message.lower() or "6 month" in user_message.lower()}
    print(f"CHAT_API: Final response with meta: {response}")
    return JsonResponse(response)


def chatbot_view(request):
    """Render the chatbot interface"""
    return render(request, 'chatbot.html')


# --- Hackathon: Mock endpoints for idea ingestion, pricing tiers, feedback ---
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def idea_ingest_api(request):
    if request.method != 'POST':
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    idea_text = data.get('idea', '')

    # Mock processing
    response = {
        "status": "received",
        "idea_id": "idea_12345",
        "summary": f"Received your idea: '{idea_text[:50]}...'. We'll analyze market fit and provide feedback within 24 hours.",
        "next_steps": ["Market validation", "Competitive analysis", "Business model design"]
    }

    return JsonResponse(response)

@csrf_exempt
def pricing_tiers_api(request):
    """Mock pricing tiers endpoint"""
    if request.method != 'GET':
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    tiers = {
        "free": {
            "name": "Starter",
            "price": 0,
            "features": ["Basic business plan template", "1 roadmap per month", "Email support"]
        },
        "pro": {
            "name": "Professional",
            "price": 29,
            "features": ["AI-powered business plans", "Unlimited roadmaps", "Market analysis", "Priority support"]
        },
        "enterprise": {
            "name": "Enterprise",
            "price": 99,
            "features": ["Custom AI agents", "Team collaboration", "Advanced analytics", "Dedicated account manager"]
        }
    }

    return JsonResponse({"tiers": tiers})

@csrf_exempt
def feedback_api(request):
    """Mock feedback collection endpoint"""
    if request.method != 'POST':
        return JsonResponse({"detail": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)

    feedback_text = data.get('feedback', '')
    rating = data.get('rating', 0)

    response = {
        "status": "received",
        "feedback_id": "fb_67890",
        "message": "Thank you for your feedback! We'll use it to improve BizPilot.",
        "rating": rating
    }

    return JsonResponse(response)