# MCP servers

Build MCP (Model Context Protocol) servers that let LLMs interact with external services through well-designed tools, in Python (FastMCP) or Node/TypeScript (MCP SDK). Quality is measured not by how comprehensively tools wrap an API, but by how well their schemas, descriptions, and outputs enable an LLM with no other context to accomplish real tasks.

## Design principles

- **API coverage vs. workflow tools**: balance comprehensive endpoint coverage against specialized workflow tools. Workflow tools are convenient for specific tasks; broad coverage lets agents compose operations. When uncertain, prioritize comprehensive API coverage.
- **Naming and discoverability**: clear, action-oriented names with consistent service prefixes (`github_create_issue`, `github_list_repos`) so agents find the right tool and avoid conflicts with other servers.
- **Context management**: return focused, relevant data. Support filtering and pagination so tool outputs do not overwhelm the agent's context.
- **Actionable errors**: error messages should guide the agent toward a fix with a specific next step (e.g. suggest a filter to reduce results).

## Workflow

1. **Research and plan**: study the MCP spec (sitemap at `https://modelcontextprotocol.io/sitemap.xml`, fetch pages with `.md` suffix), the relevant SDK README, and the target service's API (endpoints, auth, data models). List the tools to implement, starting with the most common operations.
2. **Implement**: set up project structure, build shared infrastructure (API client with auth, error handling, response formatting, pagination), then implement tools.
3. **Review and test**: check for DRY, consistent error handling, full type coverage, clear descriptions. Build and test with MCP Inspector (`npx @modelcontextprotocol/inspector`).
4. **Evaluate**: create evaluation questions (see below) to verify an LLM can use the server effectively.

**Recommended stack**: TypeScript (strong SDK, good model code-gen, static typing). Transport: streamable HTTP with stateless JSON for remote servers (simpler to scale than stateful sessions); stdio for local servers. Avoid SSE (deprecated).

## Conventions

- **Server name**: Python `{service}_mcp` (e.g. `slack_mcp`); Node `{service}-mcp-server` (e.g. `slack-mcp-server`). Descriptive, no version numbers.
- **Tool name**: snake_case with service prefix, action-oriented: `{service}_{action}_{resource}` (`slack_send_message`). Keep operations focused and atomic.
- **Response formats**: support both `json` (complete structured data, all fields, for programmatic use) and `markdown` (human-readable, default; headers/lists, human-readable timestamps, display names with IDs in parens, omit verbose metadata).
- **Pagination**: always respect `limit` (default 20-50); never load all results into memory. Return `total`, `count`, `offset`, `has_more`, `next_offset` (or cursor).

Pagination response shape:
```json
{ "total": 150, "count": 20, "offset": 0, "items": [], "has_more": true, "next_offset": 20 }
```

## Tool annotations

Hints, not security guarantees; clients must not make security-critical decisions from them.

| Annotation | Default | Meaning |
|---|---|---|
| `readOnlyHint` | false | Does not modify environment |
| `destructiveHint` | true | May perform destructive updates |
| `idempotentHint` | false | Repeated calls have no additional effect |
| `openWorldHint` | true | Interacts with external entities |

## Tool descriptions

Each tool needs a `title`, a thorough `description`, validated input schema, and annotations. The description must precisely match actual functionality and should include:

- Summary plus what the tool does NOT do (e.g. "searches existing users, does not create them").
- Each parameter with type, constraints, default, and an example.
- Full return schema for JSON output (field names, types, inline comments).
- Use-when / don't-use-when examples pointing to the correct sibling tool.
- Error-handling notes (what message appears for 429, empty results, etc.).

## Security

- **Auth**: OAuth 2.1 with token validation (accept only tokens intended for your server), or API keys from env vars (never in code), validated on startup.
- **Input validation**: schema-validate all inputs (Pydantic/Zod). Sanitize file paths (directory traversal), validate URLs/identifiers, check sizes and ranges, prevent command injection.
- **Errors**: do not expose internal details; log security-relevant errors server-side; clean up resources on failure.
- **DNS rebinding** (local HTTP servers): validate the `Origin` header, bind to `127.0.0.1` not `0.0.0.0`.
- **stdio**: never log to stdout, use stderr.

## Character limits

Define a `CHARACTER_LIMIT` (~25000). When a response exceeds it, truncate the data, set a `truncated` flag, and include a message telling the agent to use `offset` or add filters.

---

## Python (FastMCP)

FastMCP auto-generates description and inputSchema from the function signature and docstring. Use `@mcp.tool` with a Pydantic model for input.

```python
from enum import Enum
from typing import Optional
import httpx
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("example_mcp")
API_BASE_URL = "https://api.example.com/v1"

class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

class UserSearchInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True, extra="forbid")
    query: str = Field(..., description="Search string", min_length=2, max_length=200)
    limit: Optional[int] = Field(default=20, ge=1, le=100, description="Max results")
    offset: Optional[int] = Field(default=0, ge=0, description="Results to skip")
    response_format: ResponseFormat = Field(default=ResponseFormat.MARKDOWN, description="Output format")

    @field_validator("query")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

async def _make_api_request(endpoint: str, method: str = "GET", **kwargs) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.request(method, f"{API_BASE_URL}/{endpoint}", timeout=30.0, **kwargs)
        resp.raise_for_status()
        return resp.json()

def _handle_api_error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        code = e.response.status_code
        return {404: "Error: Resource not found. Check the ID.",
                403: "Error: Permission denied.",
                429: "Error: Rate limit exceeded. Wait before retrying."}.get(
                code, f"Error: API request failed with status {code}")
    if isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. Please try again."
    return f"Error: Unexpected error: {type(e).__name__}"

@mcp.tool(name="example_search_users", annotations={
    "title": "Search Example Users",
    "readOnlyHint": True, "destructiveHint": False,
    "idempotentHint": True, "openWorldHint": True,
})
async def example_search_users(params: UserSearchInput) -> str:
    '''Comprehensive docstring with Args, Returns schema, Examples, Error Handling.'''
    try:
        data = await _make_api_request("users/search", params={
            "q": params.query, "limit": params.limit, "offset": params.offset})
        users, total = data.get("users", []), data.get("total", 0)
        if not users:
            return f"No users found matching '{params.query}'"
        # format per params.response_format (markdown vs json)
        ...
    except Exception as e:
        return _handle_api_error(e)

if __name__ == "__main__":
    mcp.run()  # or mcp.run(transport="streamable_http", port=8000)
```

**Pydantic v2**: use `model_config` (not nested `Config`), `field_validator` (not `validator`), `model_dump()` (not `dict()`); validators need `@classmethod`. Use `extra="forbid"` to reject unknown fields. Let Pydantic do validation, no manual checks.

**Advanced FastMCP**:
- **Context injection**: add `ctx: Context` param for `ctx.report_progress()`, `ctx.log_info/error()`, `ctx.elicit()` (request input from user), `ctx.read_resource()`, `ctx.fastmcp.name`.
- **Resources**: `@mcp.resource("file://documents/{name}")` for URI-template data access. Use resources for simple, template-based reads; tools for operations with validation/side effects.
- **Structured returns**: return TypedDict or Pydantic models directly; FastMCP serializes and generates the schema.
- **Lifespan**: `FastMCP(..., lifespan=...)` with an `@asynccontextmanager` to init/clean up persistent connections, accessed via `ctx.request_context.lifespan_state`.

**Checklist**: async/await for all I/O; specific exception types; module-level UPPER_CASE constants; grouped imports; shared helpers (no copy-paste between tools); `python your_server.py --help` runs.

---

## Node / TypeScript (MCP SDK)

Use modern APIs only: `server.registerTool()`, `registerResource()`, `registerPrompt()`. Do NOT use deprecated `server.tool()` or manual `setRequestHandler`. Validate input with Zod (`.strict()` to forbid extra fields). The `description` must be explicit (JSDoc is not extracted).

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";
import { z } from "zod";
import axios, { AxiosError } from "axios";

const API_BASE_URL = "https://api.example.com/v1";
const CHARACTER_LIMIT = 25000;
enum ResponseFormat { MARKDOWN = "markdown", JSON = "json" }

const UserSearchInputSchema = z.object({
  query: z.string().min(2).max(200).describe("Search string"),
  limit: z.number().int().min(1).max(100).default(20).describe("Max results"),
  offset: z.number().int().min(0).default(0).describe("Results to skip"),
  response_format: z.nativeEnum(ResponseFormat).default(ResponseFormat.MARKDOWN),
}).strict();
type UserSearchInput = z.infer<typeof UserSearchInputSchema>;

const server = new McpServer({ name: "example-mcp-server", version: "1.0.0" });

function handleApiError(error: unknown): string {
  if (error instanceof AxiosError && error.response) {
    const map: Record<number, string> = {
      404: "Error: Resource not found. Check the ID.",
      403: "Error: Permission denied.",
      429: "Error: Rate limit exceeded. Wait before retrying.",
    };
    return map[error.response.status] ?? `Error: API failed with ${error.response.status}`;
  }
  return `Error: ${error instanceof Error ? error.message : String(error)}`;
}

server.registerTool("example_search_users", {
  title: "Search Example Users",
  description: `Full description with Args, Returns schema, Examples, Error Handling.`,
  inputSchema: UserSearchInputSchema,
  annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: true },
}, async (params: UserSearchInput) => {
  try {
    const data = await makeApiRequest<any>("users/search", "GET", undefined, {
      q: params.query, limit: params.limit, offset: params.offset });
    const users = data.users ?? [];
    if (!users.length)
      return { content: [{ type: "text", text: `No users found matching '${params.query}'` }] };
    const output = { total: data.total, count: users.length, offset: params.offset, users,
      has_more: data.total > params.offset + users.length };
    const text = params.response_format === ResponseFormat.MARKDOWN
      ? formatMarkdown(output) : JSON.stringify(output, null, 2);
    return { content: [{ type: "text", text }], structuredContent: output };
  } catch (error) {
    return { content: [{ type: "text", text: handleApiError(error) }] };
  }
});
```

Return both `content` text and `structuredContent` (modern SDK pattern) so clients can process outputs. Define `outputSchema` where possible.

**Transports**:
```typescript
// stdio (local)
await server.connect(new StdioServerTransport());

// streamable HTTP (remote): new stateless transport per request
app.post("/mcp", async (req, res) => {
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
  res.on("close", () => transport.close());
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});
```

**Project layout**: `src/index.ts` (entry), `tools/` (one file per domain), `services/` (API clients), `schemas/` (Zod), `constants.ts`, build to `dist/index.js`. tsconfig with `strict: true`, `module/moduleResolution: Node16`, `target: ES2022`. Deps: `@modelcontextprotocol/sdk`, `axios`, `zod`.

**Resources**: `server.registerResource()` with a URI template for static/template-based data; tools for operations with validation or side effects. Use notifications (`notifications/tools/list_changed`) sparingly, only on genuine capability changes.

**Checklist**: strict mode, no `any` (use `unknown`), explicit `Promise<T>` return types, type guards for errors; shared helpers (no copy-paste); `npm run build` succeeds and `node dist/index.js` runs.

---

## Evaluations

Create 10 questions that test whether an LLM, with access ONLY to your server's tools, can answer realistic and difficult questions. The eval measures the tools' schemas/descriptions/outputs, not the implementation.

**Process**: inspect API docs and tool schemas (without reading the server's source); then explore content with READ-ONLY, small, paginated tool calls (`limit < 10`) to find real data; then generate the questions and solve each yourself to verify the answer.

**Each question must be**:
- Independent (no dependency on another question's result or prior writes).
- Read-only, non-destructive, idempotent.
- Complex: requires multiple (potentially dozens of) tool calls, multi-hop reasoning, paging.
- Not solvable by a single keyword search: avoid target keywords, use synonyms/paraphrases so the LLM must search, analyze, and derive.
- Stable: based on closed/historical data; never on dynamic counts (reactions, replies, members "currently").
- Verifiable by direct string comparison: a single value (ID, name, datetime, number, boolean, URL). Specify the output format in the question ("Use YYYY/MM/DD.", "Answer True or False.", "Answer A, B, C, or D."). Prefer human-readable answers. Never a list, complex object, or natural-language text.

Include some deliberately ambiguous questions that still resolve to a single answer, and questions that stress large tool outputs across data modalities (IDs, names, timestamps, file types, URLs).

**Output format** (XML):
```xml
<evaluation>
  <qa_pair>
    <question>Find the repository archived in Q3 2023 that had previously been the most forked project in the org. What was its primary language?</question>
    <answer>Python</answer>
  </qa_pair>
</evaluation>
```

**Good** questions need filtering + aggregation + synthesis over historical data with a single stable answer. **Poor** questions rely on current state (changes over time), are solvable by exact-title keyword search, or have list/ambiguous-format answers.

**Run** with the harness (`scripts/evaluation.py`): `-t stdio` auto-launches the server (`-c python -a server.py [-e KEY=val]`); `-t sse`/`-t http` require the server already running (`-u URL -H "Authorization: Bearer ..."`). Output: accuracy, avg duration, tool-call counts, per-task pass/fail with the agent's feedback. If accuracy is low, refine tool descriptions, parameter docs, and the amount of data returned.
