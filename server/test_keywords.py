#!/usr/bin/env python

# Test the keyword matching logic
INTENT_RESPONSES = [
    {
        "match": ["roadmap", "6-month", "6 month", "launch", "startup", "want"],
        "response": "We'll set up a customized 6‑month launch roadmap template for you. For now, you can record your idea via voice and we'll map it into milestones (no simulations yet). You'll receive: Month‑by‑month tasks, resource checklist, and basic risk tracker."
    },
]

def detect_intent(message: str):
    msg = (message or "").lower()
    print(f"Testing message: '{msg}'")
    
    for rule in INTENT_RESPONSES:
        print(f"Checking keywords: {rule['match']}")
        for keyword in rule["match"]:
            if keyword in msg:
                print(f"  FOUND keyword '{keyword}' in message")
                return True
        print(f"  No keywords found")
    
    print("No match found")
    return False

# Test messages
test_messages = [
    "I want a 6-month launch roadmap for my startup",
    "help me create a business plan",
    "startup roadmap",
    "6-month plan"
]

for test_msg in test_messages:
    print(f"\n{'='*50}")
    result = detect_intent(test_msg)
    print(f"Result: {result}")
    print(f"{'='*50}")