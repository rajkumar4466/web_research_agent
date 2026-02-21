"""
CLI runner for OpenAI Web Research Agent
"""
import asyncio
import sys
from agent import run_web_research_agent, interactive_mode


async def main():
    if len(sys.argv) > 1:
        # Single query mode
        query = " ".join(sys.argv[1:])
        print(f"🔍 Researching: {query}\n")
        
        result = await run_web_research_agent(query)
        
        print("\n" + "="*50)
        print("📊 RESULT:")
        print("="*50)
        print(result)
        print("="*50)
    else:
        # Interactive mode
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
