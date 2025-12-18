import sys
from pathlib import Path
from typing import Any, Dict

import pytest

# Make scripts importable
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import custom_theme_search as cts  # noqa: E402


class _DummyResponse:
    def __init__(self, payload: Dict[str, Any] | None = None, text: str = ""):
        self._payload = payload or {}
        self.text = text

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Dict[str, Any]:
        return self._payload


def test_semantic_scholar_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure fallback returns parsed Semantic Scholar results when tracker is unavailable."""
    cts.HAS_RESEARCH_TRACKER = False

    def fake_get(url: str, params: Dict[str, Any] | None = None, timeout: int | None = None):
        assert "semanticscholar" in url
        assert params["query"] == "robot"
        payload = {
            "data": [
                {
                    "title": "Robot Learning",
                    "authors": [{"name": "Ada"}],
                    "citationCount": 42,
                    "year": 2023,
                    "url": "https://example.com/robot",
                }
            ]
        }
        return _DummyResponse(payload=payload)

    monkeypatch.setattr(cts.httpx, "get", fake_get)

    results = cts.search_papers_by_theme("robot", max_results=5, source="semantic_scholar", quiet=True)

    assert len(results) == 1
    assert results[0]["title"] == "Robot Learning"
    assert results[0]["citations"] == 42
    assert results[0]["authors"] == ["Ada"]
    assert results[0]["published_date"] == "2023"


def test_arxiv_and_semantic_combined_dedup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fallback combines both sources, deduplicates by title, and respects max_results."""
    cts.HAS_RESEARCH_TRACKER = False

    arxiv_feed = """
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <title>Cooperative Robots</title>
        <id>https://arxiv.org/abs/1234.5678</id>
        <published>2021-01-02T00:00:00Z</published>
        <author><name>Grace</name></author>
      </entry>
      <entry>
        <title>Robot Learning</title>
        <id>https://arxiv.org/abs/2345.6789</id>
        <published>2020-05-06T00:00:00Z</published>
        <author><name>Alan</name></author>
      </entry>
    </feed>
    """

    def fake_get(url: str, params: Dict[str, Any] | None = None, timeout: int | None = None):
        if "arxiv" in url:
            return _DummyResponse(text=arxiv_feed)

        payload = {
            "data": [
                {
                    "title": "Robot Learning",  # Duplicate title should be deduped
                    "authors": [{"name": "Ada"}],
                    "citationCount": 100,
                    "year": 2022,
                    "url": "https://example.com/semantic-robot",
                },
                {
                    "title": "Distributed Robotics",
                    "authors": [{"name": "Lin"}],
                    "citationCount": 50,
                    "year": 2024,
                    "url": "https://example.com/distributed",
                },
            ]
        }
        return _DummyResponse(payload=payload)

    monkeypatch.setattr(cts.httpx, "get", fake_get)

    results = cts.search_papers_by_theme("robotics", max_results=2, source="all", quiet=True)

    assert len(results) == 2
    assert results[0]["title"] == "Robot Learning"  # Highest citations first
    assert results[0]["citations"] == 100
    assert results[1]["title"] in {"Distributed Robotics", "Cooperative Robots"}
    assert results[1]["citations"] in {0, 50}