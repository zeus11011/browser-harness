# brag plan — browser-harness

**What:** A LangGraph agent that takes a manual UI test written in plain English and runs it in real Chrome, through the `browser_ops` MCP server (Selenium).
**For:** QA folks and devs with a pile of "click here, then check that" checklists.
**Sets it apart:** It doesn't trust itself. planning → executor → verifier: every single step gets a verdict — `pass`, `retry` or `replan` — and the loop is capped so it always terminates.
**Best claim:** "runs *exactly one* step at a time" + "the executor's own account of what happened is not evidence" (verifier skill).
**Visual hook:** one messy human sentence shattering into numbered atomic steps.
**Real material shown:** the node names, the real tool names (`navigate`, `type_text`, `click`, `wait`, `verify_text`), the `{by, value}` locator model, the three verdicts, the README's loop diagram, `uv run main.py`, the repo URL.
**No UI of its own** (CLI agent), so the "product in use" is staged: a fictional demo shop (`shop.example`) being driven. No real users/credentials — the username is a placeholder `qa-bot`.
**Tone:** default — punchy, clean, dark terminal + one acid-green accent (pass), amber (retry), violet (replan).
**Type:** Space Grotesk (display) + JetBrains Mono (code).
**Share caption:** Write the test like a human. browser-harness plans it, clicks it, and refuses to believe itself until the tool results agree.

## Music
120 BPM, 4/4, A minor, beat = 0.5s, bar = 2s. Synth: kick on beats, clap on 2/4, offbeat hats, sub bass on A–F–C–G per bar, soft pluck arp. SFX (ticks, blips, a low "thud" on the fail, rising sweep into the logo) are tuned to the key and land on the 8th-note grid. All cuts on beats.

## Storyboard (20.0s)
| # | t | Scene | On screen |
|---|---|---|---|
| 1 | 0.0–3.0 | **Hook** | "Write the test like a human." slams in; under it, a sentence types itself: *log in, search "headphones", add the first one to cart, check the cart* |
| 2 | 3.0–6.0 | **Plan** | The sentence shatters into 8 numbered atomic steps (staggered on 8ths). Label: `planning` → "one action per step." |
| 3 | 6.0–10.0 | **Execute** | Left: steps, current one lit. Right: a mini Chrome window driving shop.example (cursor clicks, typing). Bottom: the tool call ticker — `navigate(...)`, `type_text({by:"id", value:"user"}, "qa-bot")`, `click(...)`. Label `executor` — "exactly one step at a time." |
| 4 | 10.0–14.0 | **Verify** | `click({by:"css", value:".add-to-cart"})` → `ElementNotFound`. Verifier stamp **RETRY**. Re-run with `wait(...)` → **PASS**. Chips: pass · retry · replan. Line: "Every step gets judged. Nothing gets trusted." |
| 5 | 14.0–17.0 | **Loop** | The README's loop diagram drawn live: planning → executor → tools → verifier, arrows back. Caption "Capped retries. It always terminates." |
| 6 | 17.0–20.0 | **Outro** | `browser-harness` wordmark, "Plain-English UI tests, run in real Chrome.", `uv run main.py`, github.com/zeus11011/browser-harness |
