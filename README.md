# 🔍 Web Research Agent - 3 Framework Comparison

A simple web research agent implemented using **OpenAI Agents SDK**, **CrewAI**, and **LangGraph**, all using **MCP (Model Context Protocol)** for Playwright browser automation.

## 🎯 Project Goal

Given a question:
1. **Search the web** using Playwright browser automation
2. **Ask clarifying questions** if the query is ambiguous
3. **Return a comprehensive answer** with sources

## 📁 Project Structure

```
web_research_agent/
├── README.md                    # This file
├── .env.example                 # Environment variables template
├── requirements.txt             # Shared dependencies
│
├── openai_impl/                 # OpenAI Agents SDK implementation
│   ├── agent.py                 # Main agent code
│   └── run.py                   # CLI runner
│
├── crew_impl/                   # CrewAI implementation
│   ├── crew.py                  # CrewAI setup
│   └── run.py                   # CLI runner
│
└── langgraph_impl/              # LangGraph implementation
    ├── graph.py                 # LangGraph state machine
    └── run.py                   # CLI runner
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd web_research_agent
pip install -r requirements.txt
playwright install chromium
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run Each Implementation

**OpenAI Agents SDK:**
```bash
python openai_impl/run.py "What is the latest version of Python?"
```

**CrewAI:**
```bash
python crew_impl/run.py "What is the latest version of Python?"
```

**LangGraph:**
```bash
python langgraph_impl/run.py "What is the latest version of Python?"
```

## 📊 Feature Comparison

| Feature | OpenAI | CrewAI | LangGraph |
|---------|--------|--------|-----------|
| **Complexity** | ⭐ Simple | ⭐⭐ Medium | ⭐⭐⭐ Advanced |
| **Setup Code** | ~50 lines | ~80 lines | ~120 lines |
| **Clarifying Questions** | ✅ Automatic | ✅ Via tasks | ✅ Via nodes |
| **Browser Automation** | ✅ MCP | ✅ MCP | ✅ MCP |
| **Trace Support** | ✅ Native | ⚠️ Custom | ✅ LangSmith |
| **State Management** | 🤖 Automatic | 🤖 Task-based | 🎛️ Explicit |
| **Best For** | Quick prototypes | Multi-agent teams | Complex workflows |

## 🎓 Learning Outcomes

### OpenAI Implementation
- Direct MCP server integration
- Automatic tool calling
- Built-in tracing

### CrewAI Implementation
- Task-based workflow
- Agent collaboration
- Memory management

### LangGraph Implementation
- State machine design
- Conditional routing
- Persistent checkpointing

## 🔧 Technical Details

### MCP Server Used
- **Playwright MCP** (`@playwright/mcp@latest`)
  - Browser automation
  - Web navigation
  - Content extraction

### Common Pattern

All three implementations follow this pattern:

```
1. Receive question
   ↓
2. Analyze if clarification needed
   ↓
3a. Yes → Ask clarifying questions → Wait for response
3b. No → Proceed to search
   ↓
4. Use Playwright to search web
   ↓
5. Extract and analyze results
   ↓
6. Format comprehensive answer
```

## 💡 Example Queries

**Simple (no clarification needed):**
- "What is the capital of France?"
- "Who won the 2023 FIFA World Cup?"

**Ambiguous (needs clarification):**
- "What's the best language?" (Programming? Spoken? For what purpose?)
- "How much does it cost?" (What product/service?)

**Research-heavy:**
- "What are the pros and cons of electric vehicles in 2025?"
- "Explain quantum computing for beginners"

## 🎯 Key Differences

### OpenAI Agents SDK
```python
# Automatic - just define agent and tools
agent = Agent(
    instructions="...",
    mcp_servers=[playwright_server]
)
result = await Runner.run(agent, query)
```

### CrewAI
```python
# Task-based - define agents and tasks
crew = Crew(
    agents=[researcher, clarifier],
    tasks=[clarification_task, research_task]
)
result = crew.kickoff(inputs={"query": query})
```

### LangGraph
```python
# State machine - explicit control flow
graph = StateGraph(State)
graph.add_node("clarify", clarify_node)
graph.add_node("research", research_node)
graph.add_conditional_edges(...)
result = await graph.ainvoke({"query": query})
```

## 🔍 When to Use Each

| Framework | Use When... |
|-----------|-------------|
| **OpenAI** | You want simple, fast implementation with great tracing |
| **CrewAI** | You need multiple specialized agents working together |
| **LangGraph** | You need fine-grained control over workflow logic |

## 📚 Further Reading

- [OpenAI Agents SDK](https://github.com/openai/openai-agents-sdk)
- [CrewAI Documentation](https://docs.crewai.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

**Ready to compare? Run all three and see which approach you prefer!** 🚀
