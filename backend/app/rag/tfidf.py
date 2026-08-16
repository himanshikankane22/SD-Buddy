"""Lightweight pure-Python TF-IDF retrieval.

No external ML dependencies (works offline, easy to explain in interviews).
In production this could be swapped for an embedding index (e.g. sentence-transformers
or a vector DB). The interface stays the same.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from functools import lru_cache

from .loader import KBSection, load_kb_sections

_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "as",
    "by", "at", "is", "are", "was", "were", "be", "been", "it", "this", "that",
    "these", "those", "from", "into", "about", "which", "what", "when", "where",
    "how", "who", "i", "we", "you", "they", "he", "she", "will", "would", "can",
    "could", "should", "do", "does", "did", "have", "has", "had", "not", "no",
    "yes", "please", "your", "my", "our", "their", "use", "used", "using", "via",
}


def tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS and len(t) > 1]


class TfidfIndex:
    """In-memory TF-IDF index over KB sections."""

    def __init__(self, sections: list[KBSection]) -> None:
        self.sections = sections
        self.doc_count = len(sections)

        self._tokenized: list[Counter] = []
        self._idf: dict[str, float] = {}

        for sec in sections:
            self._tokenized.append(Counter(tokenize(sec.full_text)))

        # document frequency
        df: Counter = Counter()
        for toks in self._tokenized:
            df.update(toks.keys())

        for term, docfreq in df.items():
            self._idf[term] = math.log((1 + self.doc_count) / (1 + docfreq)) + 1.0

    def _tfidf(self, doc_idx: int, term: str) -> float:
        tf = self._tokenized[doc_idx].get(term, 0.0)
        if tf == 0:
            return 0.0
        return tf * self._idf.get(term, 1.0)

    def query(self, text: str, top_k: int = 5) -> list[tuple[KBSection, float]]:
        query_toks = tokenize(text)
        if not query_toks:
            return []

        q_counts = Counter(query_toks)
        scored: list[tuple[int, float]] = []
        for doc_idx in range(self.doc_count):
            score = 0.0
            for term, qtf in q_counts.items():
                score += qtf * self._tfidf(doc_idx, term)
            if score > 0:
                scored.append((doc_idx, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [(self.sections[i], s) for i, s in scored[:top_k]]


@lru_cache(maxsize=1)
def build_index() -> TfidfIndex:
    return TfidfIndex(load_kb_sections())


def retrieve(query: str, top_k: int = 5, min_score: float = 0.0) -> list[tuple[KBSection, float]]:
    idx = build_index()
    results = idx.query(query, top_k=top_k)
    return [(sec, score) for sec, score in results if score >= min_score]


def format_context(query: str, top_k: int = 5) -> str:
    """Return a compact context block for the LLM from the top KB sections."""
    parts = []
    for i, (sec, _score) in enumerate(retrieve(query, top_k=top_k), start=1):
        parts.append(f"[{i}] Source: {sec.source} | {sec.title}\n{sec.text[:1400]}")
    return "\n\n---\n\n".join(parts)
