"""
CLI runner for LangGraph Web Research Agent
"""
import asyncio
import sys
from graph import run_research, run_with_clarification


async def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py '<your question>'")
        print("\nExample:")
        print("  python run.py 'What is the capital of France?'")
        print("  python run.py 'What is the best programming language?'")
        return
    
    query = " ".join(sys.argv[1:])
    print(f"🔍 Web Research Agent (LangGraph Implementation)")
    print("=" * 50)
    print(f"Query: {query}\n")
    
    # First attempt
    result = await run_research(query)
    
    # Check if clarification is needed
    if result.startswith("🤔 Clarification needed:"):
        print(result)
        print("\n" + "-" * 50)
        
        # In CLI mode, we'll just show the clarification request
        # In interactive mode, you could prompt for input here
        clarification = input("\n📝 Your clarification: ").strip()
        
        if clarification:
            print("\n🔄 Re-running with clarification...\n")
            result = await run_with_clarification(query, clarification)
    
    print("\n" + "="*50)
    print("📊 FINAL RESULT:")
    print("="*50)
    print(result)
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
