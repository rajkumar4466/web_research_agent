"""
Web Research Agent - LangGraph Implementation

Uses state machine with explicit clarification and research nodes.
"""
from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agents.mcp import MCPServerStdio
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Playwright MCP server parameters
PLAYWRIGHT_PARAMS = {
    "command": "npx",
    "args": ["@playwright/mcp@latest"]
}


class State(TypedDict):
    """State for the research workflow."""
    messages: Annotated[list, add_messages]
    query: str
    needs_clarification: bool
    clarification_response: str | None
    research_result: str | None


async def clarification_node(state: State) -> State:
    """
    Analyze if the query needs clarification.
    """
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    system_prompt = """You are a query analyzer. Determine if the user's question is clear or needs clarification.

Examples of CLEAR questions:
- "What is the capital of France?"
- "What's the latest version of Python?"

Examples that NEED CLARIFICATION:
- "What's the best language?" (programming? spoken? for what purpose?)
- "How much does it cost?" (what product/service?)
- "Is it good?" (what thing?)

Respond with ONLY:
- "CLEAR" if the question is unambiguous
- "CLARIFY: <specific question>" if clarification is needed"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Query: {state['query']}")
    ]
    
    response = await llm.ainvoke(messages)
    result = response.content
    
    if result.startswith("CLARIFY:"):
        # Extract clarification question
        clarification = result.replace("CLARIFY:", "").strip()
        return {
            "needs_clarification": True,
            "messages": [AIMessage(content=clarification)]
        }
    else:
        return {
            "needs_clarification": False,
            "messages": [AIMessage(content="Question is clear, proceeding with research...")]
        }


async def research_node(state: State) -> State:
    """
    Perform web research using Playwright MCP.
    """
    query = state['query']
    
    # If there was a clarification response, incorporate it
    if state.get('clarification_response'):
        query = f"{state['query']} ({state['clarification_response']})"
    
    async with MCPServerStdio(params=PLAYWRIGHT_PARAMS, client_session_timeout_seconds=120) as server:
        # Navigate to Google search
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        await server.call_tool("browser_navigate", {"url": search_url})
        
        # Get page content
        content_result = await server.call_tool("browser_content", {})
        content = content_result.content[0].text if content_result.content else "No content found"
        
        # Use LLM to synthesize answer from content
        llm = ChatOpenAI(model="gpt-4o-mini")
        
        synthesis_prompt = f"""Based on the following web search results, provide a comprehensive answer to: "{query}"

Search Results:
{content[:2000]}

Provide:
1. A clear, concise answer
2. Key facts
3. Sources/URLs if visible

Format:
**Answer:**
<your answer>

**Key Facts:**
- <fact 1>
- <fact 2>

**Sources:**
- <source if available>"""
        
        response = await llm.ainvoke([HumanMessage(content=synthesis_prompt)])
        
        return {
            "research_result": response.content,
            "messages": [AIMessage(content=response.content)]
        }


def should_clarify(state: State) -> Literal["clarify", "research"]:
    """Route to clarification or directly to research."""
    if state.get("needs_clarification"):
        return "clarify"
    return "research"


def needs_user_input(state: State) -> Literal["end", "research"]:
    """Check if we need user input or can proceed to research."""
    if state.get("needs_clarification") and not state.get("clarification_response"):
        return "end"  # Stop and wait for user input
    return "research"


def build_graph() -> StateGraph:
    """
    Build the LangGraph workflow.
    
    Workflow:
    START → clarification_node → [needs_clarification?]
                                    ↓ Yes → END (wait for user)
                                    ↓ No  → research_node → END
    """
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("clarify", clarification_node)
    workflow.add_node("research", research_node)
    
    # Add edges
    workflow.add_edge(START, "clarify")
    workflow.add_conditional_edges(
        "clarify",
        needs_user_input,
        {"end": END, "research": "research"}
    )
    workflow.add_edge("research", END)
    
    # Compile with checkpointing
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app


async def run_research(query: str) -> str:
    """
    Run the research workflow.
    
    Args:
        query: User's question
        
    Returns:
        Research result or clarification question
    """
    app = build_graph()
    
    config = {"configurable": {"thread_id": "1"}}
    
    result = await app.ainvoke(
        {"query": query, "messages": [], "needs_clarification": False},
        config=config
    )
    
    # Check if we need clarification
    if result.get("needs_clarification") and not result.get("research_result"):
        last_message = result["messages"][-1].content
        return f"🤔 Clarification needed:\n{last_message}"
    
    return result.get("research_result", "No result available")


async def run_with_clarification(query: str, clarification: str = None) -> str:
    """
    Run research with optional clarification.
    
    Args:
        query: Original question
        clarification: User's clarification response
        
    Returns:
        Research result
    """
    app = build_graph()
    config = {"configurable": {"thread_id": "1"}}
    
    initial_state = {
        "query": query,
        "messages": [],
        "needs_clarification": False,
        "clarification_response": clarification
    }
    
    result = await app.ainvoke(initial_state, config=config)
    
    return result.get("research_result", "No result available")


if __name__ == "__main__":
    # Test
    query = "What is the latest version of Python?"
    print(f"🔍 Researching: {query}\n")
    result = asyncio.run(run_research(query))
    print(f"\n📊 Result:\n{result}")
