# BizPilot AI Agent System

BizPilot has been upgraded with a powerful multi-agent AI system that provides real business intelligence and planning assistance, similar to advanced AI chatbots like ChatGPT but specialized for business consulting.

## 🚀 Features

### AI-Powered Agents
- **Business Planner**: Creates comprehensive business plans and strategies
- **Market Researcher**: Conducts real-time market analysis using web search
- **Financial Advisor**: Provides financial planning and investment guidance  
- **Roadmap Generator**: Creates detailed launch timelines and milestones
- **Coordinator**: Manages the team and provides integrated responses

### Smart Query Routing
The system automatically routes queries to the most appropriate specialist agent:
- Business planning → Business Planner
- Market questions → Market Researcher  
- Financial queries → Financial Advisor
- Timeline/roadmap requests → Roadmap Generator
- Complex queries → Coordinator (uses all agents)

## 🛠️ Setup Instructions

### 1. Install Dependencies
```bash
cd D:\BizPilot\BizPilot\server
python setup_bizpilot.py
```

### 2. Configure API Keys
Edit the `.env` file and add your API keys:
```env
OPENAI_API_KEY=sk-your-openai-key-here
GROQ_API_KEY=gsk_your-groq-key-here
```

**Get API Keys:**
- OpenAI: https://platform.openai.com/api-keys
- Groq: https://console.groq.com/keys

### 3. Run the Server
```bash
python manage.py runserver
```

### 4. Test the System
Visit `http://127.0.0.1:8000/` and try these example queries:

**Business Planning:**
- "Help me create a business plan for a food delivery app"
- "What should I include in my startup strategy?"

**Market Research:**
- "What's the market size for AI fitness apps?"
- "Who are the main competitors in the e-commerce space?"

**Financial Planning:**
- "How should I price my SaaS subscription?"
- "What funding options are available for early-stage startups?"

**Roadmap Generation:**
- "Create a 6-month launch roadmap for my tech startup"
- "I need a timeline for launching my online store"

## 🔧 Technical Architecture

### Agent System (`bizpilot_agents.py`)
- **Multi-agent coordination** using the Phi framework
- **Flexible model support** (OpenAI GPT-4 or Groq Llama)
- **Tool integration** (web search, financial data, etc.)
- **Graceful fallbacks** to static responses if agents fail

### Django Integration (`views.py`)
- **Smart routing** between AI agents and static responses
- **Error handling** with automatic fallbacks
- **API compatibility** maintained for frontend
- **Structured data** for roadmap visualization

### Frontend Compatibility
- Existing frontend works without changes
- Enhanced with AI-generated content
- Roadmap visualization for timeline queries
- Debug logging shows whether AI or static responses are used

## 🎯 Usage Examples

### Business Plan Generation
```
User: "I want to start a sustainable fashion brand targeting Gen Z"

AI Response: 
# Sustainable Fashion Brand Business Plan

## Executive Summary
Your sustainable fashion brand targeting Gen Z represents a significant opportunity in the growing conscious consumer market...

## Market Analysis
The sustainable fashion market is valued at $8.25 billion globally and growing at 15% annually...

[Detailed business plan continues...]
```

### Market Research
```
User: "What's the competition like in the meal kit delivery space?"

AI Response:
# Meal Kit Delivery Market Analysis

## Market Leaders
- **HelloFresh**: 43% market share, strong in subscription model
- **Blue Apron**: Focus on organic ingredients, premium positioning
- **Home Chef**: Acquired by Kroger, retail distribution advantage

[Detailed competitive analysis with recent data...]
```

### Financial Planning
```
User: "How should I price my project management SaaS?"

AI Response:
# SaaS Pricing Strategy Analysis

## Recommended Pricing Tiers
| Tier | Price | Features | Target |
|------|-------|----------|--------|
| Starter | $9/month | Basic PM tools | Small teams |
| Professional | $29/month | Advanced features | Growing companies |
| Enterprise | $99/month | Full suite | Large organizations |

[Detailed reasoning and market comparisons...]
```

## 🔄 Fallback System

If AI agents are unavailable (missing API keys, network issues, etc.), the system automatically falls back to enhanced static responses while maintaining full functionality.

## 📊 Monitoring

Check the Django server logs to see which system is being used:
- `DEBUG: Using AI agents for processing` - AI-powered response
- `DEBUG: Using static responses` - Fallback mode

## 🆙 Future Enhancements

- **Custom agent training** on your specific business data
- **Integration with business tools** (CRM, analytics, etc.)
- **Multi-language support**
- **Voice interaction capabilities**
- **Real-time collaboration features**