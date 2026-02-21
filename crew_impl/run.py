"""
CLI runner for CrewAI Web Research Agent
"""
import sys
from crew import run_research


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py '<your question>'")
        print("\nExample:")
        print("  python run.py 'What is the capital of France?'")
        print("  python run.py 'What is the best programming language?'")
        return
    
    query = " ".join(sys.argv[1:])
    print(f"🔍 Web Research Agent (CrewAI Implementation)")
    print("=" * 50)
    print(f"Query: {query}\n")
    
    result = run_research(query)
    
    print("\n" + "="*50)
    print("📊 FINAL RESULT:")
    print("="*50)
    print(result)
    print("="*50)


if __name__ == "__main__":
    main()
