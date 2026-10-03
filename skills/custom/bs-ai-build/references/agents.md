# Agents & orchestration (langgraph)

Build stateful, multi-actor agents as explicit graphs. Make flow visible and debuggable: design state carefully, use reducers for accumulation, add persistence for production, and always guard cycles against infinite loops.

## State graphs

A `StateGraph` is nodes (functions) plus edges (control flow) over a typed state. Nodes receive the full state and return partial updates; reducers decide how updates merge.

Basic ReAct-style agent with tools:

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # reducer appends, not overwrites

@tool
def search(query: str) -> str:
    """Search the web."""
    return f"Results for: {query}"

tools = [search]
llm = ChatOpenAI(model="gpt-4o").bind_tools(tools)

def agent(state: AgentState) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}

def should_continue(state: AgentState) -> str:
    return "tools" if state["messages"][-1].tool_calls else END

graph = StateGraph(AgentState)
graph.add_node("agent", agent)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, ["tools", END])
graph.add_edge("tools", "agent")  # loop back
app = graph.compile()

app.invoke({"messages": [("user", "What is 25 * 4?")]})
```

## Reducers

Annotate each state field with a reducer to control merge behavior. No reducer means overwrite.

```python
from operator import add

def merge_dicts(left: dict, right: dict) -> dict:
    return {**left, **right}

class ResearchState(TypedDict):
    messages: Annotated[list, add_messages]      # append
    findings: Annotated[dict, merge_dicts]       # merge
    sources: Annotated[list[str], add]           # accumulate
    current_step: str                            # overwrite
    errors: Annotated[int, lambda a, b: a + b]   # sum
```

Nodes return only the fields they update; LangGraph applies the reducers.

## Routing

Use `add_conditional_edges` with a router function that reads state and returns the next node name. Map return values to nodes explicitly.

```python
def route_query(state: RouterState) -> str:
    return state["query_type"]  # "coding" | "search" | "chat"

graph.add_edge(START, "classifier")
graph.add_conditional_edges(
    "classifier",
    route_query,
    {"coding": "coding", "search": "search", "chat": "chat"},
)
graph.add_edge("coding", END)
graph.add_edge("search", END)
graph.add_edge("chat", END)
```

## Checkpointers & persistence

Compile with a checkpointer so state persists across turns and runs resume. Pass a `thread_id` to scope a conversation.

```python
from langgraph.checkpoint.memory import MemorySaver

app = graph.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "user-123"}}
app.invoke({"messages": [("user", "Hi")]}, config)
```

Persistence enables human-in-the-loop: interrupt before a node, inspect or edit state, then resume.

## Anti-patterns

**Infinite loop without exit.** Agent loops forever, burning tokens. Always add exit conditions: a max-iterations counter in state, explicit `END` in routing, and an application-level timeout.

```python
def should_continue(state):
    if state["iterations"] > 10 or state["task_complete"]:
        return END
    return "agent"
```

**Stateless nodes.** Bypassing state loses persistence and resumability. Route all data through state updates; use reducers for accumulation; let LangGraph own the state.

**Giant monolithic state.** Hard to reason about, bloats context, slows serialization. Use input/output schemas for clean interfaces, keep internal data in private state, and separate concerns.

## Limitations

Python-first (TypeScript lags). Graph concepts have a learning curve, state management adds complexity, and debugging cyclic flows can be hard.
