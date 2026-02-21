"""
Web Research Agent - OpenAI Agents SDK Implementation

Uses Playwright MCP server for web browsing and automatically handles clarifications.
"""
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Playwright MCP server parameters
PLAYWRIGHT_PARAMS = {
    "command": "npx",
    "args": ["@playwright/mcp@latest"]
}

AGENT_INSTRUCTIONS = """You are a helpful web research assistant.

Your goal: Answer the user's question by searching the web using your browser tools.

IMPORTANT RULES:
1. If the question is unclear or ambiguous, ASK clarifying questions before searching
2. Use the browser tools to navigate and search for information
3. Provide comprehensive answers with sources
4. Be concise but thorough

Examples of when to ask for clarification:
- "What's the best language?" → Ask: "Do you mean programming language, spoken language, or something else?"
- "How much does it cost?" → Ask: "What product or service are you asking about?"
- "Is it good?" → Ask: "What specifically are you asking about?"

Examples of clear questions (proceed directly):
- "What is the capital of France?"
- "What's the latest version of Python?"
"""


async def run_web_research_agent(query: str, max_turns: int = 25) -> str:
    """
    Run the web research agent with the given query.
    
    Args:
        query: User's question
        max_turns: Maximum number of turns for the agent
        
    Returns:
        Agent's response
    """
    async with MCPServerStdio(params=PLAYWRIGHT_PARAMS, client_session_timeout_seconds=120) as server:
        agent = Agent(
            name="WebResearcher",
            instructions=AGENT_INSTRUCTIONS,
            model="gpt-4o-mini",
            mcp_servers=[server]
        )
        
        with trace("web-research"):
            result = await Runner.run(agent, query, max_turns=max_turns)
            
        return result.final_output


async def interactive_mode():
    """Run in interactive mode for back-and-forth clarifications."""
    print("🔍 Web Research Agent (OpenAI Implementation)")
    print("=" * 50)
    print("Ask me anything! I'll search the web for answers.")
    print("Type 'quit' to exit.\n")
    
    async with MCPServerStdio(params=PLAYWRIGHT_PARAMS, client_session_timeout_seconds=120) as server:
        agent = Agent(
            name="WebResearcher",
            instructions=AGENT_INSTRUCTIONS,
            model="gpt-4o-mini",
            mcp_servers=[server]
        )
        
        conversation = []
        
        while True:
            user_input = input("\n📝 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
            
            conversation.append({"role": "user", "content": user_input})
            
            print("\n🤖 Agent: Thinking...\n")
            
            with trace("web-research"):
                result = await Runner.run(
                    agent, 
                    user_input, 
                    context=conversation,
                    max_turns=25
                )
            
            print(f"🤖 Agent: {result.final_output}\n")
            conversation.append({"role": "assistant", "content": result.final_output})


if __name__ == "__main__":
    # Run in interactive mode
    asyncio.run(interactive_mode())
