"""Load and chunk the Markdown knowledge base."""
from __future__ import annotations

import re
from pathlib import Path

from ..config import get_settings


class KBSection:
    """A chunk of the KB: source file, section title, and body text."""

    def __init__(self, source: str, title: str, text: str) -> None:
        self.source = source
        self.title = title
        self.text = text

    @property
    def full_text(self) -> str:
        return f"{self.title}\n{self.text}"


def _heading_level(line: str) -> int | None:
    m = re.match(r"^(#{1,6})\s+(.*)$", line.strip())
    if m:
        return len(m.group(1))
    return None


def _kb_dir(kb_dir: str | None = None) -> Path:
    if kb_dir:
        p = Path(kb_dir)
        if p.exists():
            return p
    candidates = [
        Path(get_settings().kb_dir),
        Path(get_settings().kb_dir).resolve(),
        Path(__file__).resolve().parent.parent.parent.parent / "kb",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


def load_kb_sections(kb_dir: str | None = None) -> list[KBSection]:
    """Load every .md file under kb/ and split it into heading-based sections."""
    base = _kb_dir(kb_dir)
    if not base.exists():
        raise FileNotFoundError(f"KB directory not found: {base}")

    sections: list[KBSection] = []
    for md in sorted(base.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        lines = text.splitlines()
        source = md.name

        current_title = md.name
        current_body: list[str] = []

        def flush(body: list[str], title: str, _source: str = source) -> None:
            joined = "\n".join(body).strip()
            if joined:
                sections.append(KBSection(_source, title, joined))

        for line in lines:
            lvl = _heading_level(line)
            if lvl is not None and lvl <= 3:
                flush(current_body, current_title)
                current_title = re.sub(r"^#+\s*", "", line.strip())
                current_body = []
            else:
                current_body.append(line)
        flush(current_body, current_title)
    return sections


def load_kb_text(kb_dir: str | None = None) -> str:
    """Full KB as plain text (used for quick keyword checks)."""
    base = _kb_dir(kb_dir)
    return "\n\n".join(s.full_text for s in load_kb_sections(str(base)))
