# Agent & Tool Creation Notes: CrewAI vs OpenAI Agents SDK

Quick reference for creating **agents** and **tools** in both frameworks, based on this project’s patterns.

---

## 1. OpenAI Agents SDK

### Agent creation

- **Package:** `openai-agents` (provides the `agents` module).
- **Imports:** `from agents import Agent, Runner, trace` and `from agents.mcp import MCPServerStdio`.

**Defining an agent:**

```python
from agents import Agent

agent = Agent(
    name="WebResearcher",           # Identifier for the agent
    instructions="""...""",         # System prompt: role, rules, examples
    model="gpt-4o-mini",            # OpenAI model (e.g. gpt-4o, gpt-4o-mini)
    mcp_servers=[server]             # List of MCP servers (tools come from here)
)
```

**Important fields:**

| Field           | Purpose |
|----------------|--------|
| `name`         | Unique name for the agent. |
| `instructions` | Full system prompt: behavior, when to clarify, when to use tools, output format. |
| `model`        | Model ID string. |
| `mcp_servers`  | MCP server instances (stdio, HTTP, etc.). Tools are **discovered from these**, not defined in code. |

- You do **not** define tools manually; the SDK gets tool list and schemas from each MCP server.
- Optional: `mcp_config` for schema conversion, error handling, etc.

### Tools (via MCP)

- Tools are **not** created in Python for the OpenAI SDK in this setup; they come from **MCP servers**.
- You only **connect** a server; the model sees whatever tools that server exposes.

**Connecting an MCP server (e.g. Playwright):**

```python
from agents.mcp import MCPServerStdio

PLAYWRIGHT_PARAMS = {
    "command": "npx",
    "args": ["@playwright/mcp@latest"]
}

async with MCPServerStdio(
    params=PLAYWRIGHT_PARAMS,
    client_session_timeout_seconds=120
) as server:
    agent = Agent(
        name="WebResearcher",
        instructions=AGENT_INSTRUCTIONS,
        model="gpt-4o-mini",
        mcp_servers=[server]
    )
    # Agent now has all tools from Playwright MCP (e.g. browser_navigate, browser_content)
```

- The agent uses the server’s tools by name (e.g. `browser_navigate`, `browser_content`); you don’t register them yourself.

### Running the agent

```python
from agents import Runner, trace

# One-off run
with trace("web-research"):
    result = await Runner.run(agent, query, max_turns=25)
answer = result.final_output

# With conversation history (e.g. interactive)
result = await Runner.run(agent, user_input, context=conversation, max_turns=25)
```

- **Async:** Use `await Runner.run(...)`.
- **Tracing:** Wrap in `with trace("workflow-name"):` for the OpenAI traces dashboard.

### Summary (OpenAI)

- **Agent:** `Agent(name=..., instructions=..., model=..., mcp_servers=[...])`.
- **Tools:** Supplied by MCP servers; no custom tool class in Python.
- **Execution:** `Runner.run(agent, input, max_turns=..., context=...)` → `result.final_output`.

---

## 2. CrewAI

### Agent creation

- **Imports:** `from crewai import Agent, Task, Crew, Process`.
- Agents have **role**, **goal**, **backstory**, and optional **tools**.

**Defining an agent:**

```python
from crewai import Agent

# Agent without tools (e.g. clarifier)
clarifier = Agent(
    role="Query Clarifier",
    goal="Analyze user questions and ask clarifying questions if needed",
    backstory="""You are an expert at understanding user intent...""",
    verbose=True,
    allow_delegation=False
)

# Agent with tools
researcher = Agent(
    role="Web Researcher",
    goal="Search the web and provide comprehensive answers with sources",
    backstory="""You are a skilled web researcher...""",
    verbose=True,
    tools=[browser_tool],      # List of BaseTool instances
    allow_delegation=False
)
```

**Important fields:**

| Field              | Purpose |
|--------------------|--------|
| `role`             | Job title / role name (e.g. “Web Researcher”). |
| `goal`             | What the agent is trying to achieve. |
| `backstory`        | Context/persona; helps the LLM behave consistently. |
| `tools`            | List of CrewAI tools (subclasses of `BaseTool`). |
| `verbose`          | Whether to log step-by-step. |
| `allow_delegation` | Whether this agent can delegate to other agents. |

- In CrewAI, **each agent that should use tools must be given a `tools` list**; tools are not auto-discovered from MCP in the same way as in the OpenAI SDK.

### Tool creation (CrewAI)

- Tools are **explicit**: you define a class that extends `BaseTool` and an **input schema** with Pydantic.

**1. Define input schema (Pydantic):**

```python
from pydantic import BaseModel, Field

class BrowserSearchInput(BaseModel):
    """Input for browser search tool."""
    query: str = Field(description="The search query or URL to navigate to")
```

**2. Subclass `BaseTool` and implement `_run` and/or `_arun`:**

```python
from crewai.tools import BaseTool
from typing import Type

class BrowserSearchTool(BaseTool):
    name: str = "browser_search"
    description: str = "Search the web and extract information using a browser. Provide a search query or URL."
    args_schema: Type[BaseModel] = BrowserSearchInput

    def _run(self, query: str) -> str:
        """Synchronous entrypoint; can call async."""
        return asyncio.run(self._arun(query))

    async def _arun(self, query: str) -> str:
        """Actual implementation (e.g. call MCP, API, etc.)."""
        # Your logic here
        return result
```

**Important:**

- `name`: Tool name the agent will see.
- `description`: Tells the LLM when and how to use the tool.
- `args_schema`: Pydantic model; defines and describes the tool’s arguments.
- Implement `_run` for sync and/or `_arun` for async; CrewAI will call the appropriate one.

**Using MCP inside a CrewAI tool:**

- You can start an MCP server inside `_arun`, call `server.call_tool("tool_name", {...})`, and return the result as a string so the agent gets the output.

### Tasks and crew

- **Task:** One unit of work for one agent, with description and optional dependency on other tasks.

```python
from crewai import Task

clarification_task = Task(
    description=f"""Analyze this question: "{query}" ...""",
    agent=clarifier,
    expected_output="Either 'CLEAR: <question>' or 'CLARIFY: <questions>'"
)

research_task = Task(
    description=f"""Research and answer: "{query}" ...""",
    agent=researcher,
    expected_output="Comprehensive answer with sources",
    context=[clarification_task]   # Run after clarification
)
```

- **Crew:** Connects agents and tasks and runs them (e.g. sequentially).

```python
from crewai import Crew, Process

crew = Crew(
    agents=[clarifier, researcher],
    tasks=[clarification_task, research_task],
    process=Process.sequential,
    verbose=True
)
result = crew.kickoff()   # Sync
```

### Summary (CrewAI)

- **Agent:** `Agent(role=..., goal=..., backstory=..., tools=[...], verbose=..., allow_delegation=...)`.
- **Tool:** Pydantic `args_schema` + `BaseTool` subclass with `name`, `description`, `_run`/`_arun`.
- **Execution:** Define `Task`s per agent, add to a `Crew`, then `crew.kickoff()`.

---

## 3. Side-by-side comparison

| Aspect            | OpenAI Agents SDK                    | CrewAI                                  |
|------------------|--------------------------------------|-----------------------------------------|
| **Agent config** | `name`, `instructions`, `model`, `mcp_servers` | `role`, `goal`, `backstory`, `tools`     |
| **Tools**        | From MCP servers (no Python tool class) | Explicit `BaseTool` + Pydantic schema   |
| **Tool args**    | Defined by MCP server                | You define via `args_schema`            |
| **Execution**    | `Runner.run(agent, input)` (async)    | `Crew(agents, tasks).kickoff()` (sync)   |
| **Workflow**     | Single agent, multi-turn             | Multi-agent, task graph (e.g. sequential)|
| **MCP**          | Native: pass server into agent       | Use MCP inside a custom tool’s `_arun`  |

---

## 4. When to use which

- **OpenAI Agents SDK:** One agent, tools from MCP, minimal code, built-in tracing. Good for straightforward “one agent + tools” apps.
- **CrewAI:** Multiple specialized agents, explicit tools and schemas, task-based pipelines (clarifier → researcher). Good when you want clear roles and a defined task flow.

Both can use the same MCP server (e.g. Playwright): OpenAI uses it directly; CrewAI wraps it in a `BaseTool` and calls `call_tool` inside `_arun`.
