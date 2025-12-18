#!/usr/bin/env python3
"""
Custom Theme Search Script
Search for research papers by custom themes/topics
"""
import json
import logging
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List

import httpx

# Add research-tracker to path
RESEARCH_TRACKER = Path.home() / "research-tracker"
if not RESEARCH_TRACKER.exists():
    # Try relative path for local development
    RESEARCH_TRACKER = Path(__file__).parent.parent.parent / "research-tracker"

sys.path.insert(0, str(RESEARCH_TRACKER / "src"))

try:
    from scrapers.arxiv_scraper import ArxivScraper
    from scrapers.semantic_scholar_scraper import SemanticScholarScraper
    from database.repository import PaperRepository  # noqa: F401  # kept for backward compatibility
    from database.models import Paper  # noqa: F401  # kept for backward compatibility

    HAS_RESEARCH_TRACKER = True
    IMPORT_ERROR: Exception | None = None
except ImportError as e:  # pragma: no cover - exercised through fallback tests
    HAS_RESEARCH_TRACKER = False
    IMPORT_ERROR = e


def create_simple_logger(quiet: bool = False) -> logging.Logger:
    """Create a simple logger for the scrapers"""
    logger = logging.getLogger('custom_search')
    logger.setLevel(logging.DEBUG if not quiet else logging.ERROR)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(logging.DEBUG if not quiet else logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def _normalize_paper(title: str, authors: List[str], published_date: str | None,
                     citations: int | None, url: str | None) -> Dict[str, Any]:
    """Normalize paper dictionary to a consistent schema"""
    return {
        "title": title or "Untitled",
        "authors": authors or [],
        "published_date": published_date,
        "citations": citations if citations is not None else 0,
        "url": url,
    }


def _fallback_arxiv_search(theme: str, max_results: int, logger: logging.Logger,
                           quiet: bool = False) -> List[Dict[str, Any]]:
    """Lightweight arXiv search used when research-tracker is unavailable"""
    params = {
        "search_query": f"all:{theme}",
        "start": 0,
        "max_results": max_results,
    }

    try:
        response = httpx.get(
            "http://export.arxiv.org/api/query",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
    except Exception as exc:  # pragma: no cover - defensive network guard
        logger.error("arXiv fallback failed: %s", exc)
        return []

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as exc:  # pragma: no cover - defensive parsing guard
        logger.error("arXiv response parse error: %s", exc)
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    papers: List[Dict[str, Any]] = []

    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", default="", namespaces=ns).strip()
        published_raw = entry.findtext("atom:published", default="", namespaces=ns)
        published_date = published_raw[:10] if published_raw else None
        authors = [
            author.findtext("atom:name", default="", namespaces=ns).strip()
            for author in entry.findall("atom:author", ns)
            if author.findtext("atom:name", default="", namespaces=ns).strip()
        ]
        url = entry.findtext("atom:id", default="", namespaces=ns)
        papers.append(_normalize_paper(title, authors, published_date, None, url))

    if not quiet:
        print(f"   Fallback arXiv returned {len(papers)} papers", file=sys.stderr)

    return papers


def _fallback_semantic_scholar_search(theme: str, max_results: int, logger: logging.Logger,
                                      quiet: bool = False) -> List[Dict[str, Any]]:
    """Semantic Scholar search used when research-tracker is unavailable"""
    params = {
        "query": theme,
        "limit": max_results,
        "fields": "title,authors,citationCount,year,url",
    }

    try:
        response = httpx.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # pragma: no cover - defensive network guard
        logger.error("Semantic Scholar fallback failed: %s", exc)
        return []

    papers: List[Dict[str, Any]] = []
    for paper in payload.get("data", []):
        authors = [a.get("name") for a in paper.get("authors", []) if a.get("name")]
        papers.append(
            _normalize_paper(
                paper.get("title", "Untitled"),
                authors,
                str(paper.get("year")) if paper.get("year") else None,
                paper.get("citationCount"),
                paper.get("url"),
            )
        )

    if not quiet:
        print(f"   Fallback Semantic Scholar returned {len(papers)} papers", file=sys.stderr)

    return papers


def _deduplicate_and_sort(papers: List[Dict[str, Any]], max_results: int) -> List[Dict[str, Any]]:
    """Deduplicate by title (case-insensitive) and sort by citations, keeping the highest-cited duplicate."""
    deduped: Dict[str, Dict[str, Any]] = {}

    for paper in papers:
        title_lower = paper.get('title', '').lower()
        if not title_lower:
            continue

        current = deduped.get(title_lower)
        if current is None or (paper.get('citations') or 0) > (current.get('citations') or 0):
            deduped[title_lower] = paper

    unique_papers = list(deduped.values())
    unique_papers.sort(
        key=lambda p: p.get('citations', 0) if p.get('citations') else 0,
        reverse=True
    )

    return unique_papers[:max_results]


def search_papers_by_theme(theme: str, max_results: int = 10, source: str = "all",
                           quiet: bool = False) -> List[Dict[str, Any]]:
    """Search for papers by custom theme/topic.

    Args:
        theme: Research theme/topic to search for.
        max_results: Maximum number of papers to return (per endpoint upper bound is enforced upstream).
        source: Data source selector ("arxiv", "semantic_scholar", or "all").
        quiet: Suppress console output when True (used for JSON mode).

    Returns:
        List of paper dictionaries sorted by citation count and deduplicated by title.
    """
    papers: List[Dict[str, Any]] = []
    errors: List[str] = []

    logger = create_simple_logger(quiet)

    if HAS_RESEARCH_TRACKER:
        if source in ["arxiv", "all"]:
            try:
                if not quiet:
                    print(f"🔍 Searching arXiv for: {theme}", file=sys.stderr)
                arxiv_scraper = ArxivScraper(logger=logger)
                arxiv_papers = arxiv_scraper.search(theme, max_results=max_results)
                papers.extend(arxiv_papers)
                if not quiet:
                    print(f"   Found {len(arxiv_papers)} papers from arXiv", file=sys.stderr)
            except Exception as exc:  # pragma: no cover - exercised through fallback
                errors.append(f"arXiv search failed: {exc}")
                if not quiet:
                    print(f"⚠️ arXiv search fallback: {exc}", file=sys.stderr)

        if source in ["semantic_scholar", "all"]:
            try:
                if not quiet:
                    print(f"🔍 Searching Semantic Scholar for: {theme}", file=sys.stderr)
                ss_scraper = SemanticScholarScraper(logger=logger)
                ss_papers = ss_scraper.get_recent_papers([theme], max_results=max_results)
                papers.extend(ss_papers)
                if not quiet:
                    print(f"   Found {len(ss_papers)} papers from Semantic Scholar", file=sys.stderr)
            except Exception as exc:  # pragma: no cover - exercised through fallback
                errors.append(f"Semantic Scholar search failed: {exc}")
                if not quiet:
                    print(f"⚠️ Semantic Scholar search fallback: {exc}", file=sys.stderr)
    else:
        msg = f"research-tracker unavailable: {IMPORT_ERROR}" if IMPORT_ERROR else "research-tracker unavailable"
        errors.append(msg)
        if not quiet:
            print(f"⚠️ {msg}. Using built-in fallback search.", file=sys.stderr)

    if not papers:
        if source in ["arxiv", "all"]:
            papers.extend(_fallback_arxiv_search(theme, max_results, logger, quiet))

        if source in ["semantic_scholar", "all"]:
            papers.extend(_fallback_semantic_scholar_search(theme, max_results, logger, quiet))

    deduped = _deduplicate_and_sort(papers, max_results)

    if not deduped and not quiet:
        print(f"❌ No papers found for \"{theme}\". Try a different theme or source.", file=sys.stderr)
        if errors:
            print(f"   Context: {'; '.join(errors)}", file=sys.stderr)

    return deduped


def main():
    """Main entry point for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Search research papers by custom theme')
    parser.add_argument('theme', help='Research theme/topic to search')
    parser.add_argument('--max-results', type=int, default=10, help='Maximum results (default: 10)')
    parser.add_argument('--source', choices=['arxiv', 'semantic_scholar', 'all'], 
                       default='all', help='Data source (default: all)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # When outputting JSON, suppress status messages
    papers = search_papers_by_theme(args.theme, args.max_results, args.source, quiet=args.json)
    
    # Convert datetime objects to strings for JSON serialization
    if args.json:
        for paper in papers:
            for key, value in paper.items():
                if hasattr(value, 'isoformat'):  # datetime object
                    paper[key] = value.isoformat()
                elif hasattr(value, 'strftime'):  # date object
                    paper[key] = value.strftime('%Y-%m-%d')
    
    if args.json:
        print(json.dumps(papers, indent=2, ensure_ascii=False))
    else:
        print(f"\n📚 Found {len(papers)} papers for '{args.theme}':\n")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.get('title', 'N/A')}")
            print(f"   Authors: {', '.join(paper.get('authors', []))[:80]}")
            print(f"   Published: {paper.get('published_date', 'N/A')}")
            if paper.get('citations'):
                print(f"   Citations: {paper['citations']}")
            if paper.get('url'):
                print(f"   URL: {paper['url']}")
            print()


if __name__ == "__main__":
    main()
