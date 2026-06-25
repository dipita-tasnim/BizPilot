"""
BizPilot AI Agent - Main agent orchestrator for business assistance
"""
import os
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from dotenv import load_dotenv
import json

load_dotenv()

class BizPilotAgent:
    def __init__(self):
        # Web research agent for market analysis
        self.web_agent = Agent(
            name="Market Research Agent",
            model=OpenAIChat(id="gpt-4o-mini"),  # Using mini for cost efficiency
            tools=[DuckDuckGo()],
            instructions=[
                "You are a market research specialist for startups and businesses.",
                "Always provide recent, factual information with sources.",
                "Focus on market trends, competitor analysis, and industry insights.",
                "Keep responses concise but informative."
            ],
            show_tool_calls=True,
            markdown=True
        )
        
        # Finance agent for financial analysis
        self.finance_agent = Agent(
            name="Finance Agent", 
            role="Financial analysis and market data",
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
            instructions=[
                "You are a financial analyst specializing in startup and business finance.",
                "Use tables to display financial data clearly.",
                "Provide insights on market conditions, funding trends, and financial metrics.",
                "Include relevant financial context for business decisions."
            ],
            show_tool_calls=True,
            markdown=True,
        )
        
        # Business planning agent (main orchestrator)
        self.business_agent = Agent(
            name="Business Planning Agent",
            model=OpenAIChat(id="gpt-4o-mini"),
            team=[self.web_agent, self.finance_agent],
            instructions=[
                "You are BizPilot AI, an expert business consultant and startup advisor.",
                "Help users with business planning, roadmaps, market analysis, and strategic decisions.",
                "When creating roadmaps, provide detailed, actionable monthly plans.",
                "Always consider market context and financial implications.",
                "Use data from your team agents to provide comprehensive advice.",
                "Format roadmaps as structured JSON when requested.",
                "Be encouraging and practical in your advice."
            ],
            show_tool_calls=True,
            markdown=True,
        )
    
    def get_business_advice(self, query: str) -> dict:
        """Get business advice from the AI agent"""
        try:
            # Get response from the business agent
            response = self.business_agent.run(query)
            
            # Check if this is a roadmap request
            is_roadmap = any(keyword in query.lower() for keyword in 
                           ["roadmap", "plan", "timeline", "6-month", "6 month", "launch plan"])
            
            result = {
                "reply": response.content,
                "is_roadmap": is_roadmap
            }
            
            # If it's a roadmap request, try to extract structured data
            if is_roadmap:
                roadmap_data = self._extract_roadmap_structure(response.content)
                if roadmap_data:
                    result["roadmap"] = roadmap_data
            
            return result
            
        except Exception as e:
            return {
                "reply": f"I encountered an error while processing your request: {str(e)}. Please try again.",
                "is_roadmap": False,
                "error": str(e)
            }
    
    def _extract_roadmap_structure(self, content: str) -> list:
        """Extract structured roadmap data from AI response"""
        try:
            # Try to find month-by-month structure in the response
            roadmap = []
            lines = content.split('\n')
            current_month = None
            current_tasks = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Look for month indicators
                if any(month_indicator in line.lower() for month_indicator in 
                      ["month 1", "month 2", "month 3", "month 4", "month 5", "month 6",
                       "1.", "2.", "3.", "4.", "5.", "6."]):
                    
                    # Save previous month if exists
                    if current_month is not None and current_tasks:
                        roadmap.append({
                            "month": current_month,
                            "tasks": current_tasks.copy()
                        })
                    
                    # Extract month number
                    if "month" in line.lower():
                        try:
                            current_month = int(line.lower().split("month")[1].strip().split()[0])
                        except:
                            current_month = len(roadmap) + 1
                    else:
                        current_month = len(roadmap) + 1
                    
                    current_tasks = []
                    
                    # Add the title/description as first task
                    task_text = line.split(":", 1)[-1].strip() if ":" in line else line
                    if task_text and not task_text.lower().startswith("month"):
                        current_tasks.append(task_text)
                
                # Look for bullet points or task items
                elif line.startswith(('- ', '• ', '* ')) or line.startswith(tuple(f"{i}." for i in range(1, 20))):
                    task = line.lstrip('- •*0123456789. ').strip()
                    if task and current_month is not None:
                        current_tasks.append(task)
            
            # Add the last month
            if current_month is not None and current_tasks:
                roadmap.append({
                    "month": current_month,
                    "tasks": current_tasks
                })
            
            # If we couldn't extract a proper structure, create a default 6-month roadmap
            if len(roadmap) == 0:
                roadmap = [
                    {"month": 1, "tasks": ["Business idea validation", "Market research", "Legal structure setup"]},
                    {"month": 2, "tasks": ["MVP development", "Brand creation", "Initial funding"]},
                    {"month": 3, "tasks": ["Product testing", "User feedback", "Iteration"]},
                    {"month": 4, "tasks": ["Marketing launch", "Customer acquisition", "KPI tracking"]},
                    {"month": 5, "tasks": ["Scale operations", "Partnerships", "Feature expansion"]},
                    {"month": 6, "tasks": ["Full launch", "Performance analysis", "Next phase planning"]}
                ]
            
            return roadmap[:6]  # Limit to 6 months
            
        except Exception as e:
            print(f"Error extracting roadmap structure: {e}")
            return None

# Global agent instance
bizpilot_agent = BizPilotAgent()