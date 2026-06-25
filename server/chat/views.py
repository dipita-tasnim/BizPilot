from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
import time
import os

# Try to import the agent system, fall back to static responses if not available
try:
    import sys
    import os
    # Add the server directory to Python path to import bizpilot_agents
    server_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if server_dir not in sys.path:
        sys.path.append(server_dir)
    
    from bizpilot_agents import get_bizpilot_agents
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


def parse_chart_response(response_content: str):
    """Parse chart data from agent response"""
    import json
    
    try:
        print(f"DEBUG: Parsing chart response: {response_content[:200]}...")
        
        # Find CHART_DATA: and extract everything until the next line break or end
        chart_start = response_content.find('CHART_DATA:')
        if chart_start == -1:
            print("DEBUG: No CHART_DATA: found")
            return {
                "reply": response_content,
                "meta": {"agent_powered": True, "model": "ai"}
            }
        
        # Extract from after CHART_DATA: to the end of the JSON object
        json_start = chart_start + len('CHART_DATA:')
        remaining_text = response_content[json_start:].strip()
        
        # Find the JSON object - look for balanced braces
        brace_count = 0
        json_end = -1
        in_string = False
        escape_next = False
        
        for i, char in enumerate(remaining_text):
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
                
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_end = i + 1
                        break
        
        if json_end == -1:
            print("DEBUG: Could not find complete JSON object")
            return {
                "reply": response_content,
                "meta": {"agent_powered": True, "model": "ai"}
            }
        
        chart_json = remaining_text[:json_end]
        print(f"DEBUG: Extracted JSON: {chart_json}")
        
        chart_data = json.loads(chart_json)
        print(f"DEBUG: Parsed chart data successfully")
        
        # Get explanatory text after the JSON
        text_part = remaining_text[json_end:].strip()
        
        return {
            "reply": {
                "type": "chart",
                "title": chart_data.get("title", "Chart"),
                "data": chart_data
            },
            "explanation": text_part,
            "meta": {"agent_powered": True, "model": "ai", "has_chart": True}
        }
            
    except Exception as e:
        print(f"Error parsing chart data: {e}")
        print(f"Raw response: {response_content}")
        # Return as regular text if parsing fails
        return {
            "reply": response_content,
            "meta": {"agent_powered": True, "model": "ai"}
        }


def process_with_agents(message: str):
    """Process message using AI agents"""
    try:
        agents = get_bizpilot_agents(use_openai=False)  # Use Groq (free) instead of OpenAI
        
        # Check if this is a roadmap request for structured response
        msg_lower = message.lower()
        if any(keyword in msg_lower for keyword in ['roadmap', '6-month', '6 month', 'timeline', 'milestone']) and 'chart' not in msg_lower:
            return agents.generate_structured_roadmap(message)
        
        # For other queries, get regular response
        response_content = agents.process_query(message)
        
        # Check if response contains chart data
        if 'CHART_DATA:' in response_content:
            return parse_chart_response(response_content)
        
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


@csrf_exempt
def file_upload_api(request):
    """Handle file upload and analysis"""
    if request.method != 'POST':
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    
    try:
        uploaded_file = request.FILES.get('file')
        message = request.POST.get('message', '')
        
        if not uploaded_file:
            return JsonResponse({"detail": "No file uploaded"}, status=400)
        
        # Extract file content based on type
        file_content = extract_file_content(uploaded_file)
        
        if not file_content:
            return JsonResponse({"detail": "Could not extract file content"}, status=400)
        
        # Check if this is a CSV file with forecasting request
        is_csv = isinstance(file_content, dict) and file_content.get('is_csv', False)
        wants_forecast = any(keyword in message.lower() for keyword in ['forecast', 'predict', 'future', 'trend'])
        
        if is_csv and wants_forecast:
            # Handle forecasting request
            return handle_forecasting_request(file_content['raw_content'], message, uploaded_file.name)
        
        # Check if this is an image file with OCR results
        is_image = isinstance(file_content, dict) and file_content.get('is_image', False)
        
        if is_image:
            # For images, use the pre-formatted analysis from OCR tools
            analysis_prompt = f"""
            User message: {message}
            
            Image file: {uploaded_file.name}
            
            {file_content['summary']}
            
            Please provide additional business insights based on this image analysis and the user's request.
            """
            
            # Process with OCR analyzer agent specifically
            response = process_ocr_with_agents(analysis_prompt, uploaded_file.name, file_content)
        else:
            # Create analysis request for regular file analysis
            content_text = file_content['summary'] if is_csv else file_content
            analysis_prompt = f"""
            User message: {message}
            
            File name: {uploaded_file.name}
            File type: {uploaded_file.content_type}
            File content:
            {content_text}
            
            Please analyze this file and provide insights.
            """
            
            # Process with file analyzer agent
            response = process_file_with_agents(analysis_prompt, uploaded_file.name)
        
        return JsonResponse(response)
        
    except Exception as e:
        print(f"File upload error: {e}")
        return JsonResponse({"detail": "File processing failed"}, status=500)


def extract_file_content(uploaded_file):
    """Extract text content from uploaded files"""
    try:
        file_extension = uploaded_file.name.lower().split('.')[-1]
        
        if file_extension == 'txt':
            return uploaded_file.read().decode('utf-8')
        
        elif file_extension == 'pdf':
            try:
                import PyPDF2
                from io import BytesIO
                
                pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except ImportError:
                return "PDF processing requires PyPDF2. Please install it."
        
        elif file_extension in ['doc', 'docx']:
            try:
                import docx
                from io import BytesIO
                
                doc = docx.Document(BytesIO(uploaded_file.read()))
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
            except ImportError:
                return "Word document processing requires python-docx. Please install it."
        
        elif file_extension in ['csv']:
            try:
                import pandas as pd
                from io import StringIO
                
                content = uploaded_file.read().decode('utf-8')
                df = pd.read_csv(StringIO(content))
                
                # Return both summary and raw content for forecasting
                summary = f"CSV Data Summary:\n{df.describe()}\n\nFirst 10 rows:\n{df.head(10).to_string()}\n\nColumns: {list(df.columns)}"
                return {
                    'summary': summary,
                    'raw_content': content,
                    'is_csv': True
                }
            except ImportError:
                return "CSV processing requires pandas. Please install it."
        
        elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp']:
            try:
                from ocr_tools import extract_text_from_image, format_ocr_analysis
                
                # Read image content as bytes
                image_content = uploaded_file.read()
                
                # Extract text using OCR
                ocr_result = extract_text_from_image(image_content)
                
                if ocr_result.get("success"):
                    # Format the analysis
                    analysis = format_ocr_analysis(ocr_result, uploaded_file.name)
                    
                    return {
                        'summary': analysis,
                        'extracted_text': ocr_result['extracted_text'],
                        'ocr_data': ocr_result,
                        'is_image': True
                    }
                else:
                    return f"OCR processing failed: {ocr_result.get('error', 'Unknown error')}"
                    
            except ImportError:
                return "Image processing requires OCR libraries (pytesseract, Pillow, opencv-python). Please install them."
        
        else:
            # Try to read as text
            return uploaded_file.read().decode('utf-8', errors='ignore')
            
    except Exception as e:
        print(f"Error extracting file content: {e}")
        return None


def handle_forecasting_request(csv_content: str, message: str, filename: str):
    """Handle sales forecasting requests for CSV files"""
    try:
        from forecasting_tools import forecast_sales_data, create_scenario_analysis, generate_forecast_chart_data, intelligent_recommendations, comprehensive_business_analysis
        
        # Extract forecast parameters from message
        forecast_days = 30  # default
        simulation_factor = 1.0  # default
        
        # Parse message for custom parameters
        if 'days' in message.lower():
            import re
            days_match = re.search(r'(\d+)\s*days?', message.lower())
            if days_match:
                forecast_days = int(days_match.group(1))
        
        # Extract business parameters from message if provided
        current_inventory = 500  # default
        avg_price = 20  # default
        production_cost = 10  # default
        salary_per_employee = 300  # default
        
        # Parse business parameters from message
        import re
        if 'inventory' in message.lower():
            inventory_match = re.search(r'inventory[:\s]*(\d+)', message.lower())
            if inventory_match:
                current_inventory = int(inventory_match.group(1))
        
        if 'price' in message.lower():
            price_match = re.search(r'price[:\s]*\$?(\d+(?:\.\d+)?)', message.lower())
            if price_match:
                avg_price = float(price_match.group(1))
        
        if 'cost' in message.lower():
            cost_match = re.search(r'cost[:\s]*\$?(\d+(?:\.\d+)?)', message.lower())
            if cost_match:
                production_cost = float(cost_match.group(1))
        
        if 'salary' in message.lower():
            salary_match = re.search(r'salary[:\s]*\$?(\d+(?:\.\d+)?)', message.lower())
            if salary_match:
                salary_per_employee = float(salary_match.group(1))
        
        # Check for comprehensive analysis request
        wants_recommendations = any(term in message.lower() for term in ['recommendation', 'suggest', 'advice', 'strategy', 'plan', 'business analysis', 'comprehensive'])
        
        if any(term in message.lower() for term in ['optimistic', 'best case', 'growth']):
            simulation_factor = 1.2
        elif any(term in message.lower() for term in ['pessimistic', 'worst case', 'decline']):
            simulation_factor = 0.8
        elif 'scenario' in message.lower():
            # Generate all scenarios
            scenarios = create_scenario_analysis(csv_content, forecast_days)
            return JsonResponse({
                "reply": format_scenario_analysis(scenarios),
                "filename": filename,
                "meta": {"agent_powered": True, "model": "prophet", "file_processed": True, "has_forecast": True}
            })
        
        # Generate comprehensive business analysis if requested
        if wants_recommendations:
            analysis_result = comprehensive_business_analysis(
                csv_content, forecast_days, current_inventory, 
                avg_price, production_cost, salary_per_employee
            )
            
            if not analysis_result.get("success"):
                return JsonResponse({
                    "reply": f"Business analysis failed for {filename}: {analysis_result.get('error', 'Unknown error')}",
                    "filename": filename,
                    "meta": {"agent_powered": False, "model": "error", "file_processed": False}
                })
            
            # Format comprehensive response
            response_text = format_comprehensive_analysis(analysis_result, filename)
            
            # Check if user wants chart
            wants_chart = any(keyword in message.lower() for keyword in ['chart', 'graph', 'visualization', 'plot'])
            
            if wants_chart and analysis_result.get("chart_data"):
                return JsonResponse({
                    "reply": {
                        "type": "chart",
                        "title": analysis_result["chart_data"]["title"],
                        "data": analysis_result["chart_data"]
                    },
                    "explanation": response_text,
                    "filename": filename,
                    "meta": {"agent_powered": True, "model": "prophet", "file_processed": True, "has_chart": True, "has_forecast": True, "has_recommendations": True}
                })
            
            return JsonResponse({
                "reply": response_text,
                "filename": filename,
                "meta": {"agent_powered": True, "model": "prophet", "file_processed": True, "has_forecast": True, "has_recommendations": True}
            })
        
        # Generate single forecast
        forecast_result = forecast_sales_data(csv_content, forecast_days, simulation_factor)
        
        if not forecast_result.get("success"):
            return JsonResponse({
                "reply": f"Forecasting failed for {filename}: {forecast_result.get('error', 'Unknown error')}",
                "filename": filename,
                "meta": {"agent_powered": False, "model": "error", "file_processed": False}
            })
        
        # Format response
        response_text = format_forecast_response(forecast_result, filename)
        
        # Check if user wants chart
        wants_chart = any(keyword in message.lower() for keyword in ['chart', 'graph', 'visualization', 'plot'])
        
        if wants_chart:
            chart_data = generate_forecast_chart_data(forecast_result)
            if chart_data:
                return JsonResponse({
                    "reply": {
                        "type": "chart",
                        "title": chart_data["title"],
                        "data": chart_data
                    },
                    "explanation": response_text,
                    "filename": filename,
                    "meta": {"agent_powered": True, "model": "prophet", "file_processed": True, "has_chart": True, "has_forecast": True}
                })
        
        return JsonResponse({
            "reply": response_text,
            "filename": filename,
            "meta": {"agent_powered": True, "model": "prophet", "file_processed": True, "has_forecast": True}
        })
        
    except Exception as e:
        print(f"Forecasting error: {e}")
        return JsonResponse({
            "reply": f"Error processing forecast for {filename}: {str(e)}",
            "filename": filename,
            "meta": {"agent_powered": False, "model": "error", "file_processed": False}
        })


def format_forecast_response(forecast_result, filename):
    """Format forecast results into readable response"""
    data_info = forecast_result["data_info"]
    forecast_summary = forecast_result["forecast_summary"]
    insights = forecast_result["insights"]
    
    response = f"""# 📊 Sales Forecast Analysis for {filename}

## Data Overview
- **Records Analyzed**: {data_info['total_records']}
- **Date Range**: {data_info['date_range']}
- **Historical Average**: ${data_info['historical_average']:,.2f}
- **Last Actual Value**: ${data_info['last_actual_value']:,.2f}

## Forecast Summary
- **Forecast Period**: {forecast_summary['forecast_days']} days
- **Predicted Average**: ${forecast_summary['forecast_average']:,.2f}
- **Expected Growth**: {forecast_summary['expected_growth_rate']:+.1f}%
- **Immediate Change**: {forecast_summary['immediate_change']:+.1f}%

## Key Insights
"""
    
    for insight in insights:
        response += f"- {insight}\n"
    
    # Add top 5 forecast values
    response += "\n## Next 5 Days Forecast\n"
    for i, item in enumerate(forecast_result["forecast_data"][:5]):
        response += f"**{item['date']}**: ${item['predicted_value']:,.2f} (${item['lower_bound']:,.2f} - ${item['upper_bound']:,.2f})\n"
    
    return response


def format_scenario_analysis(scenarios):
    """Format scenario analysis results"""
    response = "# 📈 Sales Forecast Scenario Analysis\n\n"
    
    for scenario_name, result in scenarios.items():
        if result.get("success"):
            summary = result["forecast_summary"]
            response += f"## {scenario_name.title()} Scenario\n"
            response += f"- **Growth Rate**: {summary['expected_growth_rate']:+.1f}%\n"
            response += f"- **Average Forecast**: ${summary['forecast_average']:,.2f}\n"
            response += f"- **Simulation Factor**: {summary['simulation_factor']:.1f}x\n\n"
    
    return response


def format_comprehensive_analysis(analysis_result, filename):
    """Format comprehensive business analysis results"""
    forecast = analysis_result["forecast"]
    recommendations = analysis_result["recommendations"]
    
    # Basic forecast info
    data_info = forecast["data_info"]
    forecast_summary = forecast["forecast_summary"]
    
    response = f"""# 🚀 Comprehensive Business Analysis for {filename}

## 📊 Sales Forecast Overview
- **Data Period**: {data_info['date_range']}
- **Records Analyzed**: {data_info['total_records']}
- **Forecast Period**: {forecast_summary['forecast_days']} days
- **Historical Average**: ${data_info['historical_average']:,.2f}
- **Forecast Average**: ${forecast_summary['forecast_average']:,.2f}
- **Expected Growth**: {forecast_summary['expected_growth_rate']:+.1f}%

## 📦 Inventory Management
- **Current Stock**: {recommendations['inventory']['current_inventory']} units
- **Forecasted Demand**: {recommendations['inventory']['forecasted_demand']} units
- **Restock Status**: {'🔴 RESTOCK NEEDED' if recommendations['inventory']['restock_needed'] else '🟢 SUFFICIENT STOCK'}

## 🏭 Production Planning
- **Recommended Production**: {recommendations['production']['recommended_volume']} units
- **Buffer Strategy**: {recommendations['production']['note']}

## 👥 Hiring Recommendations
- **Staff Needed**: {recommendations['hiring']['employees_needed']} employees
- **Suggested Roles**: {', '.join(recommendations['hiring']['roles'])}
- **Monthly Salary Budget**: ${recommendations['hiring']['total_salary_cost']:,.2f}

## 💰 Financial Projections
- **Expected Revenue**: ${recommendations['cashflow']['expected_revenue']:,.2f}
- **Expected Costs**: ${recommendations['cashflow']['expected_costs']:,.2f}
- **Projected Profit**: ${recommendations['cashflow']['expected_profit']:,.2f}
- **Profit Margin**: {(recommendations['cashflow']['expected_profit'] / recommendations['cashflow']['expected_revenue'] * 100):+.1f}%

## 🎯 Key Insights & Actions
"""
    
    for insight in recommendations['insights']:
        response += f"- {insight}\n"
    
    # Add forecast insights if available
    if 'insights' in forecast:
        response += "\n## 📈 Forecast Insights\n"
        for insight in forecast['insights']:
            response += f"- {insight}\n"
    
    # Add next 5 forecast values
    response += f"\n## 📅 Next 5 Days Forecast\n"
    for i, item in enumerate(forecast["forecast_data"][:5]):
        response += f"**{item['date']}**: ${item['predicted_value']:,.2f} (${item['lower_bound']:,.2f} - ${item['upper_bound']:,.2f})\n"
    
    return response


def process_file_with_agents(analysis_prompt: str, filename: str):
    """Process file content using AI agents"""
    try:
        if AGENTS_AVAILABLE:
            agents = get_bizpilot_agents(use_openai=False)
            
            # Use file analyzer agent specifically
            response_content = agents.file_analyzer.run(analysis_prompt)
            
            return {
                "reply": response_content.content if hasattr(response_content, 'content') else str(response_content),
                "filename": filename,
                "meta": {"agent_powered": True, "model": "ai", "file_processed": True}
            }
        else:
            # Fallback response
            return {
                "reply": f"File '{filename}' has been uploaded successfully. File analysis capabilities are currently unavailable, but your file has been received.",
                "filename": filename,
                "meta": {"agent_powered": False, "model": "static", "file_processed": True}
            }
            
    except Exception as e:
        print(f"Error processing file with agents: {e}")
        return {
            "reply": f"File '{filename}' was uploaded but encountered an error during analysis. Please try again.",
            "filename": filename,
            "meta": {"agent_powered": False, "model": "error", "file_processed": False}
        }


def process_ocr_with_agents(prompt: str, filename: str, ocr_content: dict):
    """Process OCR results using the OCR analyzer agent"""
    try:
        from bizpilot_agents import BizPilotAgents
        
        print(f"DEBUG: Processing OCR content with agents for file: {filename}")
        
        # Initialize agents with Groq (free) instead of OpenAI
        agents = BizPilotAgents(use_openai=False)
        
        # Create enhanced prompt with OCR data
        enhanced_prompt = f"""
        {prompt}
        
        Additional OCR Metadata:
        - Confidence Score: {ocr_content['ocr_data']['confidence']}%
        - Word Count: {ocr_content['ocr_data']['word_count']}
        - Quality Score: {ocr_content['ocr_data']['quality_score']['score']}/100
        - Extracted Text: {ocr_content['extracted_text']}
        
        Please provide comprehensive business analysis based on this image content.
        """
        
        # Get response from agents (OCR analyzer will be prioritized automatically)
        response_content = agents.process_query(enhanced_prompt)
        
        return {
            "reply": response_content,
            "filename": filename,
            "ocr_confidence": ocr_content['ocr_data']['confidence'],
            "meta": {"agent_powered": True, "model": "ai", "file_processed": True, "ocr_processed": True}
        }
        
    except ImportError:
        print("WARNING: BizPilot agents not available, using fallback")
        return {
            "reply": f"Image '{filename}' processed with OCR successfully:\n\n{ocr_content['summary']}\n\nNote: Advanced AI analysis is currently unavailable.",
            "filename": filename,
            "meta": {"agent_powered": False, "model": "static", "file_processed": True, "ocr_processed": True}
        }
        
    except Exception as e:
        print(f"Error processing OCR with agents: {e}")
        return {
            "reply": f"Image '{filename}' was processed but encountered an error during AI analysis:\n\n{ocr_content['summary']}",
            "filename": filename,
            "meta": {"agent_powered": False, "model": "error", "file_processed": True, "ocr_processed": True}
        }