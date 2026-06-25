from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
import time


INTENT_RESPONSES = [
    {
        "match": ["roadmap", "6-month", "6 month", "launch", "startup", "want"],
        "response": "We'll set up a customized 6‑month launch roadmap template for you. For now, you can record your idea via voice and we’ll map it into milestones (no simulations yet). You’ll receive: Month‑by‑month tasks, resource checklist, and basic risk tracker."
    },
    {
        "match": ["incubator", "admin", "batch", "cohort", "aggregated", "dashboard"],
        "response": "We’ll batch‑process your cohort’s ideas and produce starter dashboards: submission counts, progress by phase, and top themes. You’ll get a simple group performance view you can filter by team or week."
    },
    {
        "match": ["side-hustler", "side hustler", "alerts", "email", "sms", "market", "trending"],
        "response": "We’ll prepare proactive alert setups (email/SMS). Example: trending shoe styles in Dhaka. You can configure categories, frequency, and channels. No AI detection yet—sources and keywords are defined manually."
    },
]


def detect_intent(message: str):
    msg = (message or "").lower()
    print(f"DEBUG: Processing message: '{msg}'")
    for rule in INTENT_RESPONSES:
        if any(keyword in msg for keyword in rule["match"]):
            # If this is the roadmap intent (by response text), include roadmap
            if rule["response"].startswith("We'll set up a customized 6‑month launch roadmap"):
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
                    "roadmap": roadmap
                }
            return {"reply": rule["response"]}
    return {
        "reply": (
            "Thanks! We’re setting up manual flows now. Tell me if you want a 6‑month "
            "roadmap, a cohort dashboard, or market alerts—I'll draft a starter plan."
        )
    }


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
    # Accepts: title, description, budget (all optional)
    title = data.get('title', '')
    description = data.get('description', '')
    budget = data.get('budget', '')
    # Just echo back for demo
    return JsonResponse({
        "message": "Idea received! (mock)",
        "idea": {
            "title": title,
            "description": description,
            "budget": budget
        },
        "dashboard_url": "/dashboard/"
    })


def pricing_tiers_api(request):
    # Always GET, returns static pricing tiers
    tiers = [
        {
            "name": "Free",
            "price": 0,
            "features": [
                "Basic chat",
                "2 mock startup models",
                "Basic dashboard"
            ],
            "locked": []
        },
        {
            "name": "Pro",
            "price": 19,
            "features": [
                "All Free features",
                "Premium model simulation (mock)",
                "Risk Simulation (locked)",
                "API access (locked)"
            ],
            "locked": ["Risk Simulation", "API access"]
        },
        {
            "name": "Enterprise",
            "price": 99,
            "features": [
                "All Pro features",
                "Custom AI fine-tuning (locked)",
                "Collaboration tools (locked)"
            ],
            "locked": ["Custom AI fine-tuning", "Collaboration tools"]
        }
    ]
    return JsonResponse({"tiers": tiers})


@csrf_exempt
def feedback_api(request):
    if request.method != 'POST':
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "Invalid JSON"}, status=400)
    # Accepts: rating (👍/👎), comment (optional)
    rating = data.get('rating', '')
    comment = data.get('comment', '')
    # Just echo back for demo
    return JsonResponse({
        "message": "Feedback received! (mock)",
        "rating": rating,
        "comment": comment
    })
