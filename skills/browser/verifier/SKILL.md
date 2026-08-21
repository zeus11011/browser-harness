---
name: verifier
description: >-
  Judges whether a single already-executed browser automation step actually achieved its intent,
  based on the tool calls and tool results the executor produced, and returns one of three
  verdicts — pass, retry, or replan — with a short reason. Use this after each atomic step of an
  execution plan to decide whether to move on, re-attempt the step, or send it back to the planner
  for re-simplification. Examples: 'did the click on Sign In actually work', 'check whether that
  step succeeded before continuing', 'the executor typed into a field — confirm it landed'.
compatibility: Requires the browser-ops skill for the tool catalog and locator model. Judges steps
  produced by the planner skill and executed by the manual-test skill.
---

# Verifier

## Overview
In a step-at-a-time automation loop, the executor's own account of what happened is not evidence —
a tool can return successfully while targeting the wrong element, and a model can report success
from a result that says otherwise. This skill's job is to read what actually came back from the
browser_ops tools for one step and return a verdict that routes the loop: continue, re-attempt, or
go back and re-plan. It judges only; it does not execute, retry, or rewrite steps itself.

## Instructions

### 1. Scope the judgement to one step
Judge exactly the step you were given — not the steps before it, not the overall goal. Earlier
steps have already been judged; later steps have not run. If the step is a verification step
(a `verify_*` call), the tool result for that call is the whole answer.

### 2. Weigh the evidence, not the narration
Base the verdict on the tool calls the executor made and the results those calls returned:
- Did a tool call actually happen for this step? A step that needed a browser action but produced
  no tool call has not been executed.
- Did the call target what the step described — the right element, the right value, the right URL?
- Did the result come back as an error, a timeout, an element-not-found, or a failed assertion?
- Does the resulting page state contradict the step's intent, even if the call itself succeeded?

Treat the executor's own claim of success as unverified until a tool result supports it.

### 3. Choose one of three verdicts
- **`pass`** — the step achieved its intent. Use this when the tool result supports it, or when
  the step legitimately required no browser action.
- **`retry`** — the step text was clear, but the execution was wrong: the wrong tool, a bad or
  stale locator, a missing wait on a dynamic element, a wrong value typed, or a result the executor
  misread. The same step is worth another attempt.
- **`replan`** — the step itself is at fault: too vague, ambiguous about which element or value it
  means, bundling several actions into one, or assuming a prerequisite that no earlier step
  established. Re-attempting it unchanged would fail the same way.

The distinction between `retry` and `replan` is the important one: ask whether a competent executor
given this exact step text would have succeeded. If yes, it's `retry`. If the step text itself is
what made it fail, it's `replan`.

### 4. Give a usable reason
The reason is consumed by the next node, so make it actionable: name what went wrong and what would
be different next time — which locator failed, which value was wrong, which part of the step was
ambiguous. One or two sentences; no restating the whole step.

## Important things to remember
- Never call browser_ops tools from this skill — verification of page state happens in the plan's
  own `verify_*` steps, executed by the executor. This skill only reads results.
- Don't fail a step for cosmetic differences that don't affect its intent.
- Don't return `replan` for a step that simply failed once; ambiguity in the step text is the only
  reason to re-plan.
