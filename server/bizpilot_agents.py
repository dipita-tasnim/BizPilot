"""
BizPilot AI Agent System
Multi-agent system for business planning, market analysis, and startup guidance
"""

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from dotenv import load_dotenv
import os
import json
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

class BizPilotAgents:
    """Multi-agent system for business planning and startup guidance"""
    
    def __init__(self, use_openai: bool = True):
        """
        Initialize BizPilot agent system
        
        Args:
            use_openai (bool): If True, use OpenAI GPT-4, else use Groq Llama
        """
        self.use_openai = use_openai
        self.model = self._get_model()
        
        # Initialize specialized agents
        self.business_planner = self._create_business_planner()
        self.market_researcher = self._create_market_researcher()
        self.financial_advisor = self._create_financial_advisor()
        self.roadmap_generator = self._create_roadmap_generator()
        self.chart_generator = self._create_chart_generator()
        self.file_analyzer = self._create_file_analyzer()
        self.eco_advisor = self._create_eco_advisor()
        self.sales_forecaster = self._create_sales_forecaster()
        self.ocr_analyzer = self._create_ocr_analyzer()
        
        # Master coordinator agent
        self.coordinator = self._create_coordinator()
    
    def _get_model(self):
        """Get the appropriate AI model based on configuration"""
        if self.use_openai:
            return OpenAIChat(id="gpt-4o")
        else:
            return Groq(id="llama-3.3-70b-versatile")
    
    def _create_business_planner(self) -> Agent:
        """Create specialized business planning agent"""
        return Agent(
            name="Business Planner",
            role="Expert business plan developer and startup strategist",
            model=self.model,
            instructions=[
                "You are an expert business consultant specializing in startup business plans",
                "Create comprehensive, actionable business plans",
                "Focus on feasibility, market fit, and practical implementation",
                "Always include key sections: Executive Summary, Market Analysis, Business Model, Financial Projections",
                "Use clear, professional language suitable for investors and stakeholders",
                "Provide specific, measurable goals and milestones"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def _create_market_researcher(self) -> Agent:
        """Create market research and analysis agent"""
        return Agent(
            name="Market Researcher",
            role="Market analysis and competitive intelligence specialist",
            model=self.model,
            tools=[DuckDuckGo()],
            instructions=[
                "You are a market research expert with deep knowledge of industry trends",
                "Conduct thorough market analysis using latest available data",
                "Identify target demographics, market size, and growth opportunities",
                "Analyze competitors and market positioning strategies",
                "Always include sources and cite recent data",
                "Present findings in clear, structured format with actionable insights"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def _create_financial_advisor(self) -> Agent:
        """Create financial planning and analysis agent"""
        return Agent(
            name="Financial Advisor",
            role="Startup financial planning and investment analysis expert",
            model=self.model,
            tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
            instructions=[
                "You are a financial advisor specializing in startup finances",
                "Create realistic financial projections and funding strategies",
                "Analyze investment opportunities and financial risks",
                "Provide guidance on pricing strategies and revenue models",
                "Use tables and charts to display financial data clearly",
                "Focus on cash flow, break-even analysis, and funding requirements"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def _create_roadmap_generator(self) -> Agent:
        """Create specialized roadmap and milestone planning agent"""
        return Agent(
            name="Roadmap Generator",
            role="Strategic roadmap and milestone planning specialist",
            model=self.model,
            instructions=[
                "You are an expert in strategic planning and project management",
                "Create detailed, time-bound roadmaps for business launches and growth",
                "Break down complex goals into manageable milestones and tasks",
                "Consider dependencies, resource requirements, and risk factors",
                "Provide specific timelines with monthly/quarterly breakdown",
                "Include key performance indicators (KPIs) for each milestone",
                "Format roadmaps in structured, easy-to-follow layouts"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def _create_chart_generator(self) -> Agent:
        """Create specialized chart and visualization generator"""
        return Agent(
            name="Chart Generator",
            role="Data visualization and chart creation specialist",
            model=self.model,
            instructions=[
                "You are an expert in creating business charts, graphs, and visual representations",
                "Generate charts ONLY when users specifically request 'chart', 'graph', 'visualization', or similar visual terms",
                "You must respond with structured chart data that can be rendered by Chart.js",
                "Your response format is CRITICAL - follow this EXACT format:",
                "CHART_DATA: {\"type\": \"bar\", \"title\": \"Chart Title\", \"labels\": [\"Month 1\", \"Month 2\"], \"datasets\": [{\"label\": \"Revenue ($)\", \"data\": [10000, 15000], \"backgroundColor\": [\"#007bff\", \"#22c55e\"], \"borderColor\": \"#007bff\", \"borderWidth\": 2}]}",
                "",
                "Then add your explanatory text AFTER the JSON.",
                "IMPORTANT: The JSON must be on a SINGLE LINE after 'CHART_DATA:'",
                "Use appropriate chart types: 'bar' for comparisons, 'line' for trends, 'pie' for proportions",
                "For line charts, always include borderColor and borderWidth properties",
                "Use professional colors: #007bff (blue), #22c55e (green), #ef4444 (red), #f59e0b (yellow)",
                "Keep JSON compact and on one line for proper parsing"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def _create_file_analyzer(self) -> Agent:
        """Create specialized file analysis agent"""
        return Agent(
            name="File Analyzer",
            role="Document and file analysis specialist",
            model=self.model,
            instructions=[
                "You are an expert in analyzing business documents and files",
                "Process and analyze uploaded files including PDF, DOC, TXT, and Excel files",
                "Extract key business information: financial data, market insights, business plans, reports",
                "Provide comprehensive analysis with actionable insights",
                "Identify important metrics, trends, and opportunities from documents",
                "Summarize document contents in a structured format",
                "Answer questions about the uploaded file content",
                "Suggest improvements or next steps based on document analysis",
                "Handle various file types: business plans, financial statements, market research, reports",
                "Always provide clear, professional analysis with specific findings"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def _create_eco_advisor(self) -> Agent:
        """Create specialized eco-friendly business advisor agent"""
        return Agent(
            name="Eco-Friendly Business Advisor",
            role="Sustainability and environmental business consultant",
            model=self.model,
            instructions=[
                "You are an expert in sustainable and eco-friendly business practices",
                "Provide guidance ONLY when users specifically ask for 'eco-friendly', 'sustainable', 'green', 'environmental' suggestions",
                "Focus on environmentally responsible business models and practices",
                "Suggest sustainable alternatives to traditional business approaches",
                "Cover areas like: renewable energy, waste reduction, sustainable supply chains, green products",
                "Recommend eco-friendly business ideas: solar energy, recycling, organic products, sustainable fashion",
                "Provide insights on environmental regulations and certifications (LEED, B-Corp, etc.)",
                "Include cost-benefit analysis of sustainable practices",
                "Suggest green financing options and sustainability grants",
                "Focus on circular economy principles and sustainable growth strategies",
                "Always emphasize both environmental and economic benefits",
                "Provide actionable steps for implementing sustainable practices",
                "Include relevant environmental impact metrics and sustainability KPIs"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def _create_sales_forecaster(self) -> Agent:
        """Create specialized sales forecasting and prediction agent"""
        return Agent(
            name="Sales Forecasting Agent",
            role="Sales data analysis and forecasting specialist",
            model=self.model,
            instructions=[
                "You are an expert in sales forecasting and predictive analytics",
                "Analyze CSV files containing sales data with time series information",
                "Use Facebook Prophet for time series forecasting when appropriate",
                "Provide forecasts for different scenarios (growth, decline, seasonal patterns)",
                "Generate predictions for 30, 60, 90 days or custom periods",
                "Identify trends, seasonality, and anomalies in sales data",
                "Provide scenario analysis: optimistic, realistic, pessimistic forecasts",
                "Include confidence intervals and uncertainty ranges",
                "Suggest actionable insights based on forecast results",
                "Handle various CSV formats: sales, revenue, customer data",
                "Create forecast summaries with key metrics and recommendations",
                "Always validate data quality before forecasting",
                "Explain forecasting methodology and assumptions clearly",
                "When users request business recommendations, provide intelligent suggestions for:",
                "- Inventory management (restock alerts, demand planning)",
                "- Production planning (volume recommendations with buffers)",
                "- Hiring strategies (staffing needs based on forecast)",
                "- Financial projections (revenue, costs, profit analysis)",
                "- Strategic business decisions based on forecast trends",
                "Consider business parameters like inventory levels, pricing, costs when making recommendations",
                "Always provide comprehensive business analysis when specifically requested"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def _create_ocr_analyzer(self) -> Agent:
        """Create specialized OCR and image text analysis agent"""
        return Agent(
            name="OCR Text Analyzer",
            role="Image text extraction and analysis specialist",
            model=self.model,
            instructions=[
                "You are an expert in analyzing text extracted from images using OCR (Optical Character Recognition)",
                "Process and analyze text extracted from business documents, receipts, invoices, charts, presentations",
                "Extract key business information: financial data, contact details, product information, metrics",
                "Analyze business cards, invoices, receipts, contracts, presentations, charts, graphs",
                "Provide structured analysis of extracted text with actionable insights",
                "Identify important numbers, dates, company names, and business metrics",
                "Summarize document contents and highlight key findings",
                "Suggest follow-up actions based on the extracted information",
                "Handle various image types: photos of documents, screenshots, scanned papers",
                "Focus on business-relevant information extraction and analysis",
                "Always provide clear, professional analysis with specific findings",
                "If text quality is poor, mention OCR limitations and suggest image improvements"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def _create_coordinator(self) -> Agent:
        """Create master coordinator agent that manages the team"""
        return Agent(
            name="BizPilot Coordinator",
            role="Master business consultant coordinating specialized experts",
            model=self.model,
            team=[self.business_planner, self.market_researcher, self.financial_advisor, self.roadmap_generator, self.chart_generator, self.file_analyzer, self.eco_advisor, self.sales_forecaster, self.ocr_analyzer],
            instructions=[
                "You are the lead business consultant coordinating a team of specialists",
                "Analyze user requests and delegate to appropriate expert agents",
                "Synthesize insights from multiple agents into coherent recommendations",
                "Ensure all responses are practical, actionable, and well-structured",
                "Always provide comprehensive answers that address all aspects of the query",
                "Use clear formatting with headers, bullet points, and tables where appropriate"
            ],
            show_tool_calls=True,
            markdown=True
        )
    
    def get_agent_for_query(self, query: str) -> Agent:
        """
        Determine which agent is best suited for the query
        
        Args:
            query (str): User query
            
        Returns:
            Agent: Most appropriate agent for the query
        """
        query_lower = query.lower()
        
        # Image/OCR analysis requests (HIGHEST PRIORITY - must be checked first)
        if any(keyword in query_lower for keyword in ['image', 'photo', 'picture', 'screenshot', 'ocr', 'extract text', 'read image', 'scan', 'uploaded image']):
            return self.ocr_analyzer
        
        # File analysis requests (SECOND PRIORITY)
        elif any(keyword in query_lower for keyword in ['file', 'document', 'uploaded', 'analyze file', 'analyze document', 'pdf', 'doc', 'excel']):
            return self.file_analyzer
        
        # Sales forecasting requests (THIRD PRIORITY)
        elif any(keyword in query_lower for keyword in ['forecast', 'prediction', 'predict', 'sales forecast', 'future sales', 'trend analysis', 'time series', 'prophet']):
            return self.sales_forecaster
        
        # Eco-friendly requests (THIRD PRIORITY)
        elif any(keyword in query_lower for keyword in ['eco-friendly', 'sustainable', 'green', 'environmental', 'eco friendly', 'sustainability', 'renewable', 'organic']):
            return self.eco_advisor
        
        # Chart/Visualization requests (FOURTH PRIORITY)
        elif any(keyword in query_lower for keyword in ['chart', 'graph', 'visualization', 'visualize', 'diagram', 'plot']):
            return self.chart_generator
        
        # Business plan related queries
        elif any(keyword in query_lower for keyword in ['business plan', 'startup plan', 'business model', 'plan']):
            return self.business_planner
        
        # Market research related queries
        elif any(keyword in query_lower for keyword in ['market', 'competition', 'competitor', 'industry', 'target audience']):
            return self.market_researcher
        
        # Financial related queries
        elif any(keyword in query_lower for keyword in ['financial', 'funding', 'investment', 'money', 'revenue', 'pricing']):
            return self.financial_advisor
        
        # Roadmap related queries (WITHOUT chart keywords)
        elif any(keyword in query_lower for keyword in ['roadmap', 'timeline', 'milestone', 'launch', 'schedule', 'month']):
            return self.roadmap_generator
        
        # For complex queries or general business advice, use coordinator
        else:
            return self.coordinator
    
    def process_query(self, query: str, stream: bool = False) -> str:
        """
        Process user query using the most appropriate agent
        
        Args:
            query (str): User query
            stream (bool): Whether to stream the response
            
        Returns:
            str: Agent response
        """
        try:
            agent = self.get_agent_for_query(query)
            
            if stream:
                response = agent.run(query, stream=True)
                return response
            else:
                response = agent.run(query)
                return response.content if hasattr(response, 'content') else str(response)
                
        except Exception as e:
            return f"I apologize, but I encountered an error processing your request: {str(e)}. Please try again or rephrase your question."
    
    def generate_structured_roadmap(self, query: str) -> Dict[str, Any]:
        """
        Generate a structured roadmap response for frontend display
        
        Args:
            query (str): User query about roadmap
            
        Returns:
            Dict: Structured roadmap data
        """
        try:
            response_content = self.roadmap_generator.run(
                f"""Create a detailed 6-month launch roadmap for: {query}
                
                Please structure your response with:
                1. Executive Summary
                2. Monthly breakdown with specific tasks
                3. Key milestones and deliverables
                4. Resource requirements
                5. Risk factors and mitigation strategies
                
                Format the monthly tasks as clear, actionable items."""
            )
            
            content = response_content.content if hasattr(response_content, 'content') else str(response_content)
            
            # Try to extract structured data (this is a simplified version)
            # In a more sophisticated implementation, you could parse the AI response
            # to extract structured milestone data
            
            return {
                "reply": content,
                "roadmap": [
                    {"month": 1, "tasks": ["Market research and validation", "Define MVP features", "Set up legal structure"]},
                    {"month": 2, "tasks": ["Build core product features", "Develop brand identity", "Create marketing materials"]},
                    {"month": 3, "tasks": ["Launch beta version", "Gather user feedback", "Iterate on product"]},
                    {"month": 4, "tasks": ["Full product launch", "Execute marketing campaign", "Onboard first customers"]},
                    {"month": 5, "tasks": ["Scale operations", "Expand feature set", "Build partnerships"]},
                    {"month": 6, "tasks": ["Analyze performance", "Plan next phase", "Secure additional funding"]}
                ],
                "meta": {"agent_used": "roadmap_generator", "structured": True}
            }
            
        except Exception as e:
            return {
                "reply": f"I apologize, but I encountered an error generating your roadmap: {str(e)}",
                "meta": {"error": True}
            }


# Global instance
bizpilot_agents = None

def get_bizpilot_agents(use_openai: bool = True) -> BizPilotAgents:
    """Get or create BizPilot agents instance"""
    global bizpilot_agents
    if bizpilot_agents is None:
        bizpilot_agents = BizPilotAgents(use_openai=use_openai)
    return bizpilot_agents


# Test function for development
if __name__ == "__main__":
    # Test the agent system
    agents = BizPilotAgents(use_openai=False)  # Use Groq for testing
    
    test_queries = [
        "Help me create a business plan for a food delivery startup",
        "What's the market size for AI-powered fitness apps?",
        "I need a 6-month roadmap for launching my SaaS product",
        "How should I price my subscription service?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        
        response = agents.process_query(query)
        print(response)