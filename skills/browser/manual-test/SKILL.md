---
name: manual-test
description: >-
  Turns manual UI test steps the user provides (a checklist, bug repro steps, acceptance criteria, or a rough outline) into a complete, executable test case and runs it against a live web app using the browser_ops MCP tools, then reports pass/fail results with evidence. Use this whenever the user shares step-by-step instructions to test, verify, validate, QA, reproduce, or walk through something in a web application, even if they don't say 'manual test' explicitly. Examples: 'can you check that clicking Save actually persists the form', 'walk through this login flow and confirm it works', 'here are the repro steps for this bug, verify it's fixed', 'run through this checklist on staging', or 'elaborate these rough steps into a full test case before running it'.
compatibility: Requires the browser-ops skill.
---

# Manual Test

## Overview
People rarely hand over a fully-specified test case — they give a checklist, a bug report, or a rough description of a flow. This skill's job is to turn that into a complete, unambiguous test case, run it step by step in a real browser via the browser_ops MCP tools, and hand back a clear record of what passed, what failed, and why — so the user gets a reliable validation of the application under test, not just a best-effort click-through.

## Instructions

### 1. Capture the steps
Pull together everything the user wants tested: an explicit numbered list, a bug description, acceptance criteria, or steps mentioned earlier in the conversation. Write these out as a draft test case — a numbered list of actions and, where the user gave them, expected outcomes.

### 2. Complete the test case
A test case is only as good as its specificity — a vague step like "log in" can be executed a dozen different ways, and an automated run needs to pick one and be right about it. Handle gaps like this:
- **Fill in what's inferable.** Standard UI conventions, obvious prerequisites (e.g. "navigate to the login page" before "log in"), and expected outcomes that follow naturally from the action can be filled in without checking back.
- **Ask when it's genuinely ambiguous.** If a step depends on information only the user has — which environment or URL, which account or credentials, which record, what value belongs in a field — don't guess. Ask for the missing specifics before proceeding. Whatever explicit values the user did provide should be used exactly as given, not substituted with your own.
- **Confirm before anything destructive.** If completing the test case would mean deleting data, submitting a payment, sending a message, or another hard-to-undo action the user didn't clearly ask for, check with them before running it.

### 3. Execute against the app
Run the completed test case step by step using the browser_ops MCP tools — see the browser-ops
skill for the full tool catalog, locator model, and session-handling conventions; this section
only covers judgment calls specific to running a test case:
- When a target element's locator is unknown, take a screenshot and resolve the element visually,
  then tighten whatever locator that yields toward something stable — an id or data-testid
  attribute, for instance — rather than a long structural path, before reusing it in later steps.
  Structural locators break the next time the page layout shifts, which defeats the point of
  writing the test case once.
- Check each outcome against the expected result from the test case using the verification tools.
- If a step fails, capture what happened (screenshot, error, actual vs. expected) and use judgment
  on whether to continue: independent steps later in the case can often still be attempted, but if
  a step was a precondition for what follows (e.g. login failed), stop rather than produce a
  cascade of misleading failures.
- End the run by closing any session this run opened — including when it ends early on a
  failure — so sessions don't get left open.

### 4. Report the results
Give the user a clear record of the run, not just a verdict. For each step, show the action taken, the expected result, the actual result, and pass/fail/blocked — plus any screenshots or evidence gathered along the way. Call out clearly if the run stopped early and why.

## Important things to remember
- Use any input values the user explicitly provided exactly as given — never substitute your own data.
- If the steps are too unclear or incomplete to execute reliably, ask the user for a clearer version rather than guessing your way through, and only proceed once they're clear.
- Never use `execute_javascript` to verify page text or state — always use the dedicated `verify_*` tools (see browser-ops skill).
