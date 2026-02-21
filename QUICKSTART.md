# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## Step 1: Setup Environment

```bash
cd web_research_agent

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-...
```

## Step 2: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Step 3: Test Each Implementation

### 🔵 OpenAI Agents SDK (Simplest)

**Single query:**
```bash
python openai_impl/run.py "What is the capital of France?"
```

**Interactive mode:**
```bash
python openai_impl/run.py
# Then type your questions interactively
```

### 🟢 CrewAI (Task-based)

```bash
python crew_impl/run.py "What is the latest Python version?"
```

### 🟣 LangGraph (Most Control)

```bash
python langgraph_impl/run.py "What is quantum computing?"
```

## Example Queries to Try

### Clear Questions (Direct answers)
```bash
python openai_impl/run.py "What is the capital of Japan?"
python openai_impl/run.py "Who is the CEO of Tesla?"
python openai_impl/run.py "What year did World War 2 end?"
```

### Ambiguous Questions (Should trigger clarification)
```bash
python openai_impl/run.py "What's the best language?"
# Expected: "Do you mean programming language, spoken language, or something else?"

python openai_impl/run.py "How much does it cost?"
# Expected: "What product or service are you asking about?"

python openai_impl/run.py "Is it worth it?"
# Expected: "What are you referring to?"
```

## Troubleshooting

### Issue: `npx` not found

**Solution:** Add Node.js to your PATH

```python
import os
node_bin = "/path/to/node/bin"  # Update this path
os.environ["PATH"] = f"{node_bin}:{os.environ['PATH']}"
```

Or install Node.js from https://nodejs.org

### Issue: Playwright errors

**Solution:** Install browsers
```bash
playwright install chromium
playwright install-deps  # On Linux
```

### Issue: Import errors

**Solution:** Install missing packages
```bash
pip install -r requirements.txt
```

## Next Steps

1. **Compare Results**: Run the same query on all 3 implementations
2. **Modify Instructions**: Edit the agent instructions to customize behavior
3. **Add More Tools**: Integrate additional MCP servers
4. **Deploy**: Package your favorite implementation as an API

## Performance Comparison

Run this test:

```bash
# OpenAI (fastest setup, automatic tracing)
time python openai_impl/run.py "What is AI?"

# CrewAI (more verbose, task-based)
time crew_impl/run.py "What is AI?"

# LangGraph (most control, explicit state)
time langgraph_impl/run.py "What is AI?"
```

## Which to Use?

| Choose | If You Want... |
|--------|---------------|
| **OpenAI** | Quick prototypes, minimal code, built-in tracing |
| **CrewAI** | Multiple agents collaborating, task-based workflows |
| **LangGraph** | Fine-grained control, complex state machines, custom routing |

## Support

- OpenAI SDK: https://platform.openai.com/docs
- CrewAI: https://docs.crewai.com
- LangGraph: https://langchain-ai.github.io/langgraph/

---

**Happy researching! 🔍**
