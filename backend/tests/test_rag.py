"""Tests for the RAG pipeline."""
from app.rag.loader import load_kb_sections
from app.rag.tfidf import build_index, retrieve


def test_kb_loaded():
    sections = load_kb_sections()
    # 12 articles expected
    assert len(sections) >= 12


def test_sections_have_content():
    sections = load_kb_sections()
    for sec in sections:
        assert sec.text.strip(), f"empty section: {sec.source} -> {sec.title}"


def test_retrieval_relevant():
    results = retrieve("how to reset a forgotten active directory password", top_k=5)
    assert results
    top_source = results[0][0].source
    assert "password" in top_source


def test_retrieval_bitlocker():
    results = retrieve("bitlocker recovery key intune entraid", top_k=3)
    assert results
    assert any("bitlocker" in sec.source for sec, _ in results)


def test_index_buildable():
    idx = build_index()
    assert idx.doc_count == len(load_kb_sections())


def test_retrieval_empty_query():
    assert retrieve("") == []
