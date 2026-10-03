Use the `Data AI Systems` bundle.

Default flow:
- `bs-ai-build` for prompts, MCP servers, RAG and agent orchestration
- `bs-ai-harden` before shipping anything that builds prompts, exposes tools to a model or retrieves untrusted content

Pull evals, retrieval tuning or context optimization only when the task needs them.
