# browser-harness

A LangGraph agent that drives a real Chrome browser through an MCP server.

`browser-harness` connects to `browser_ops` — a FastMCP server wrapping Selenium
WebDriver — and runs a **plan → execute → verify** loop over an LLM to carry out
browser automation and manual UI test flows written in plain English.

---

## How it works

```
          ┌───────────┐
  START ─▶│ planning  │  decompose the request into atomic steps
          └─────┬─────┘
                │
                ▼
          ┌───────────┐   tool call    ┌───────┐
          │ executor  │───────────────▶│ tools │  browser_ops via MCP
          └─────┬─────┘                └───┬───┘
                │ no tool call             │
                ▼                          │
          ┌───────────┐◀──────────────────-┘
          │ verifier  │  judge the step just executed
          └─────┬─────┘
                │
      pass ─────┼───▶ executor (next step) or END (plan exhausted)
     retry ─────┼───▶ executor (same step again)
    replan ─────┴───▶ planning (re-simplify the step)
```

- **planning** breaks the user's manual steps into the simplest possible atomic
  steps. It never calls tools.
- **executor** runs *exactly one* step at a time through the `browser_ops` tools.
- **verifier** reads the tool results and returns `pass` / `retry` / `replan`.
  It never calls tools.

Retries and replans are capped in `graph/routing.py`
(`MAX_RETRIES_PER_STEP = 2`, `MAX_REPLANS = 2`) so the loop always terminates.

---

## Requirements

- Python **>= 3.13**
- [`uv`](https://docs.astral.sh/uv/) for dependency management
- Google Chrome installed, with a matching `chromedriver` available

## Setup

```bash
uv sync
cp .env.example .env      # then fill in your model + API key
```

### Configuration

The LLM is provider-agnostic — `utils/config.py`'s `get_llm()` resolves the
provider, model and API key from the environment and instantiates the model via
`init_chat_model`:

| Variable                       | Purpose                                                       |
| ------------------------------ | ------------------------------------------------------------- |
| `LLM_MODEL`                    | Model name, e.g. `gemini-2.5-flash`, `gpt-4o`, `claude-...`   |
| `LLM_PROVIDER`                 | Optional — inferred from the model name when omitted           |
| `LLM_TEMPERATURE`              | Optional sampling temperature                                  |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Provider-specific key     |
| `LLM_API_KEY`                  | Generic fallback key                                           |
| `AWS_REGION` + AWS credentials | AWS Bedrock (`bedrock_converse:<model-id>` or e.g. `us.anthropic.claude-...`) — standard AWS credential chain, no API key |

See `.env.example` for the full list.

## Usage

```bash
uv run main.py
```

`main.py` builds the graph and invokes it with a user message. Edit the message
there to give the agent a different task:

```python
from graph import build_graph

agent = await build_graph()
response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "Open example.com and verify the heading says 'Example Domain'"}]},
    # plan/execute/verify loops once per step, so the default limit of 25 is low
    config={"recursion_limit": 100},
)
```

---

## Project layout

| Path                    | What lives there                                                                 |
| ----------------------- | -------------------------------------------------------------------------------- |
| `main.py`               | Entry point: builds the graph and invokes it.                                     |
| `graph/builder.py`      | Wiring only — the `StateGraph`, its nodes and edges.                              |
| `graph/state.py`        | `GraphState` plus the `Plan` / `Verdict` structured-output schemas.               |
| `graph/nodes/`          | One module per node, each exposing a `make_*_node(llm, ...)` factory.             |
| `graph/routing.py`      | Conditional-edge logic and the retry/replan loop guards.                          |
| `graph/prompts.py`      | `load_skill()` / `system_prompt()` — composes prompts from the `SKILL.md` files.  |
| `graph/mcp_tools.py`    | `get_browser_ops_tools()` — the `MultiServerMCPClient` stdio connection.          |
| `mcp_servers/`          | The `browser_ops` MCP server: Selenium sessions, command dispatch, models.        |
| `skills/browser/`       | Markdown skill definitions consumed by the nodes at runtime.                      |
| `utils/config.py`       | `get_llm()` — provider-agnostic model resolution.                                 |
| `errors.py`             | Application-level exception hierarchy for structured command errors.              |

### Skills

Every node's system prompt is `browser-ops` **plus** its own skill:

- `browser-ops/SKILL.md` — the single source of truth for the tool surface
  (navigation, click/type, waits, verifications, session management) and the
  locator model. The other skills reference it rather than restating it.
- `planner/SKILL.md` — decomposition only.
- `manual-test/SKILL.md` — the executor's skill: run the case step by step and
  report pass/fail with evidence.
- `verifier/SKILL.md` — judge one executed step and return the verdict.

---

## Conventions

- Locators are always `{by, value}` objects, never bare CSS/XPath strings.
  Supported strategies: `css`, `xpath`, `id`, `name`, `class_name`, `tag_name`,
  `link_text`, `partial_link_text`.
- Sessions are managed implicitly by `browser_ops` (auto-created on demand).
  Only pass `session_id` explicitly when running multiple concurrent browsers.
- The `manual-test` skill avoids `execute_javascript` for verifying page text or
  state — it uses the dedicated `verify_*` tools instead.

---

## License

Licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE).

**Free for noncommercial use** — personal projects, research, experimentation,
education, non-profits, and government institutions. Commercial use requires a
separate license; open an issue or contact the maintainer to arrange one.
