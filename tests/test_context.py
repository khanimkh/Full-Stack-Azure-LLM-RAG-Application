import sys
from pathlib import Path


BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from app.services.rag_chat import RagChatService  # noqa: E402


def test_context_builder_contains_source_and_title() -> None:
    docs = [{"title": "Doc A", "source": "a.md", "content": "Hello"}]
    result = RagChatService._build_context(docs)
    assert "Doc A" in result
    assert "a.md" in result
