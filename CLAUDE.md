# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

`browser-harness` is a LangGraph agent that drives a browser via an MCP (Model Context Protocol) server. It connects to the `browser_ops` MCP server, which wraps Selenium WebDriver (Chrome) behind FastMCP tools, and runs a plan → execute → verify loop over an LLM to carry out browser automation and manual UI test flows.

The loop: a **planning** node breaks the user's manual steps into atomic steps, an **executor** node runs exactly one step at a time through the `browser_ops` tools, and a **verifier** node judges each executed step and routes back — `pass` advances to the next step, `retry` re-attempts the same step, `replan` sends it back to the planner for re-simplification. Retry/replan counts are capped in `graph/routing.py` so the loop always terminates.

The LLM is provider-agnostic: `utils/config.py`'s `get_llm()` resolves provider/model/API key from `LLM_MODEL`, `LLM_PROVIDER`, `LLM_TEMPERATURE` and provider-specific key env vars (see `.env.example`), then instantiates via `init_chat_model`.

## Commands

This project uses `uv` for dependency management (Python >= 3.13).

- Install dependencies: `uv sync`
- Run the agent entry point: `uv run main.py`
- Add a dependency: `uv add <package>`

There is no configured lint/test/build tooling in `pyproject.toml` yet — check with the user before assuming a specific test runner.

## Architecture

- `main.py` — entry point. Builds the graph via `graph.build_graph()` and invokes it with a user message.
- `graph/` — the LangGraph plan → execute → verify loop:
  - `__init__.py` — public surface: re-exports `build_graph`, so callers use `from graph import build_graph`.
  - `builder.py` — wiring only: builds the `StateGraph`, adds nodes/edges, compiles.
  - `state.py` — `GraphState` plus the `Plan`/`Verdict` structured-output schemas.
  - `nodes/` — one module per node (`planner.py`, `executor.py`, `verifier.py`), each exposing a `make_*_node(llm, ...)` factory that returns the async node function.
  - `routing.py` — conditional-edge logic and the retry/replan loop guards.
  - `prompts.py` — `load_skill()` / `system_prompt()`, which compose each node's system prompt from `skills/browser/*/SKILL.md`.
  - `mcp_tools.py` — `get_browser_ops_tools()`, the `MultiServerMCPClient` connection to `mcp_servers/server.py`.
- `mcp_servers/` — the `browser_ops` MCP server implementation (Selenium session management, command dispatch, models). Treat this as an existing, self-contained subsystem — do not modify it.
- `skills/browser/` — skill definitions consumed by agents at runtime, not Python code. One skill per node, plus the shared tool surface; every node's prompt is `browser-ops` + its own skill:
  - `browser-ops/SKILL.md` — the single source of truth for the `browser_ops` MCP tool surface (navigation, click/type, waits, verifications, session management) and locator model (`{by, value}` with strategies `css`, `xpath`, `id`, `name`, `class_name`, `tag_name`, `link_text`, `partial_link_text`). The other skills reference it rather than restating tool names.
  - `planner/SKILL.md` — decomposition only: turns the user's manual steps into the simplest possible atomic steps. Never executes tools.
  - `manual-test/SKILL.md` — the executor's skill: runs the test case step by step and reports pass/fail with evidence.
  - `verifier/SKILL.md` — judges one executed step from its tool results and returns `pass` / `retry` / `replan`. Never executes tools.
- `errors.py` — application-level exception hierarchy (`AppError` and subclasses like `MissingLocatorError`, `ElementNotFoundError`, `CommandExecutionError`) used for structured error messages from browser commands.
- `utils/config.py` — `get_llm()`, the provider-agnostic model resolution described above.

## Key conventions

- Locators throughout the tool surface are always `{by, value}` objects, not bare CSS/XPath strings.
- Sessions are managed implicitly by `browser_ops` (auto-created on demand); only manage `session_id` explicitly when running multiple concurrent browsers.
- The `manual-test` skill explicitly avoids `execute_javascript` for verifying page text/state — it uses the dedicated `verify_*` tools instead.
