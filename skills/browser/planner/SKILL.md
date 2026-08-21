---
name: planner
description: >-
  Breaks down manual UI steps the user provides — a checklist, a rough outline, a single vague
  step, acceptance criteria, or bug repro steps — into the simplest possible sequence of atomic
  actions, so they can be executed one at a time against the browser_ops MCP tools. Use this
  whenever the user hands over manual/step-based instructions for browser automation and nothing
  has executed them yet. Examples: 'here are the steps to test checkout, break them down', 'plan
  out how to automate this login flow', 'log in and update the profile picture — plan the steps',
  or a single compound step like 'search for a product and add it to cart'.
compatibility: Requires the browser-ops skill for the tool catalog used to judge atomicity.
---

# Planner

## Overview
Manual steps handed to an agent are almost never already atomic — one line might bundle
navigation, a form fill, and a submit; another might be too vague to map to a single tool call.
This skill's only job is decomposition: turn whatever steps the user gives (one step or many)
into an ordered list of the simplest possible actions, each one small enough to correspond to a
single browser_ops tool call. It does not execute anything and does not validate outcomes — that
is the execution/manual-test skill's job.

## Instructions

### 1. Capture the input
Take the steps exactly as given — a numbered list, a paragraph, a single sentence, or steps
mentioned earlier in the conversation. Don't discard detail; every concrete value the user gave
(a URL, field value, label, credential) must survive into the broken-down plan unchanged.

### 2. Break each step into atomic actions
For each input step, split it until every resulting item maps to one browser_ops action — see the
browser-ops skill for the full tool catalog (navigation, click/type/select, wait, verify, etc.).
Rules of thumb:
- A step with "and" joining two actions ("log in and go to settings") becomes two or more steps.
- A step naming an implicit prerequisite (e.g. "submit the form" without ever navigating there)
  gets that prerequisite added as its own earlier step, only when it's genuinely implied by
  context — don't invent steps the user's flow doesn't need.
- A step that's already atomic ("click the Save button") is kept as-is, not split further.
- A vague step ("log in") is expanded into its obvious constituent actions (navigate to login
  page, enter username, enter password, click login) using standard UI conventions — without
  inventing values the user didn't provide.
- Keep verification separate from action: "verify the item appears in the cart" is its own step,
  not folded into the click that triggered it.

### 3. Handle ambiguity
If a step can't be broken down without information only the user has — which field, which value,
which page, which of several matching elements — don't guess. Ask before finalizing that part of
the plan. Use any values the user did give exactly as provided.

### 4. Output the plan
Return a single ordered, numbered list of atomic steps. Each item should be a short, literal
instruction (one action, one target, one value if applicable) — ready to be handed to an
execution step without further interpretation. Do not add pass/fail criteria, tool names, or
locators; this skill only decomposes, it doesn't resolve elements or execute.

## Important things to remember
- Never execute browser_ops tools from this skill — planning only.
- Never substitute your own data for values the user provided.
- If the input is already a list of atomic steps, say so and return it unchanged rather than
  padding it with redundant splits.
