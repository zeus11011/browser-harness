"""Loading of the SKILL.md files that make up each node's system prompt."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills" / "browser"


def load_skill(name: str) -> str:
    return (SKILLS_DIR / name / "SKILL.md").read_text(encoding="utf-8")


def system_prompt(*skills: str) -> str:
    """Compose a node's system prompt: the browser-ops tool surface plus its own skill."""
    return "\n\n".join(load_skill(name) for name in ("browser-ops", *skills))
