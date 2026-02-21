"""
Web Research Agent - CrewAI Implementation

Uses Playwright tools via CrewAI and task-based clarification workflow.
"""
from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv
import asyncio
from typing import Type

load_dotenv()

# Playwright MCP server parameters
PLAYWRIGHT_PARAMS = {
    "command": "npx",
    "args": ["@playwright/mcp@latest"]
}


class BrowserSearchInput(BaseModel):
    """Input for browser search tool."""
    query: str = Field(description="The search query or URL to navigate to")


class BrowserSearchTool(BaseTool):
    """Tool that uses Playwright MCP server for web browsing."""
    name: str = "browser_search"
    description: str = "Search the web and extract information using a browser. Provide a search query or URL."
    args_schema: Type[BaseModel] = BrowserSearchInput
    
    def _run(self, query: str) -> str:
        """Run browser search synchronously."""
        return asyncio.run(self._arun(query))
    
    async def _arun(self, query: str) -> str:
        """Run browser search using Playwright MCP."""
        async with MCPServerStdio(params=PLAYWRIGHT_PARAMS, client_session_timeout_seconds=120) as server:
            # Navigate to Google and search
            await server.call_tool("browser_navigate", {"url": f"https://www.google.com/search?q={query}"})
            
            # Get page content
            result = await server.call_tool("browser_content", {})
            
            # Extract text content
            content = result.content[0].text if result.content else "No content found"
            
            # Limit content length
            return content[:2000]  # Return first 2000 chars


def create_research_crew(query: str) -> Crew:
    """
    Create a CrewAI crew for web research with clarification.
    
    Args:
        query: User's question
        
    Returns:
        Configured Crew instance
    """
    # Create browser tool
    browser_tool = BrowserSearchTool()
    
    # Clarification Agent
    clarifier = Agent(
        role="Query Clarifier",
        goal="Analyze user questions and ask clarifying questions if needed",
        backstory="""You are an expert at understanding user intent. 
        When a question is ambiguous or lacks context, you ask specific clarifying questions.
        When a question is clear, you approve it for research.""",
        verbose=True,
        allow_delegation=False
    )
    
    # Research Agent
    researcher = Agent(
        role="Web Researcher",
        goal="Search the web and provide comprehensive answers with sources",
        backstory="""You are a skilled web researcher who uses browser tools to find accurate information.
        You always cite your sources and provide well-structured answers.""",
        verbose=True,
        tools=[browser_tool],
        allow_delegation=False
    )
    
    # Clarification Task
    clarification_task = Task(
        description=f"""Analyze this question: "{query}"
        
        Determine if the question is clear or needs clarification.
        
        If CLEAR (like "What is the capital of France?"):
        - Output: "CLEAR: <question>"
        
        If AMBIGUOUS (like "What's the best language?"):
        - Output: "CLARIFY: <specific clarifying questions>"
        
        Be strict - only mark as CLEAR if the question is unambiguous.""",
        agent=clarifier,
        expected_output="Either 'CLEAR: <question>' or 'CLARIFY: <questions>'"
    )
    
    # Research Task
    research_task = Task(
        description=f"""Research and answer this question: "{query}"
        
        Steps:
        1. Use the browser_search tool to find information
        2. Analyze the results
        3. Provide a comprehensive answer with sources
        
        Format your answer as:
        **Answer:**
        <your answer>
        
        **Sources:**
        - <source 1>
        - <source 2>""",
        agent=researcher,
        expected_output="Comprehensive answer with sources",
        context=[clarification_task]  # Depends on clarification
    )
    
    # Create crew
    crew = Crew(
        agents=[clarifier, researcher],
        tasks=[clarification_task, research_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew


def run_research(query: str) -> str:
    """
    Run the research crew with the given query.
    
    Args:
        query: User's question
        
    Returns:
        Research result
    """
    crew = create_research_crew(query)
    result = crew.kickoff()
    return str(result)


if __name__ == "__main__":
    # Test
    test_query = "What is the latest version of Python?"
    print(f"🔍 Researching: {test_query}\n")
    result = run_research(test_query)
    print(f"\n📊 Result:\n{result}")
