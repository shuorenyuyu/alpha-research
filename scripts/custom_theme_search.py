#!/usr/bin/env python3
"""
Custom Theme Search Script
Search for research papers by custom themes/topics
"""
import sys
import os
import json
from pathlib import Path

# Add research-tracker to path
RESEARCH_TRACKER = Path.home() / "research-tracker"
if not RESEARCH_TRACKER.exists():
    # Try relative path for local development
    RESEARCH_TRACKER = Path(__file__).parent.parent.parent / "research-tracker"

sys.path.insert(0, str(RESEARCH_TRACKER / "src"))

try:
    from scrapers.arxiv_scraper import ArxivScraper
    from scrapers.semantic_scholar_scraper import SemanticScholarScraper
    from database.repository import PaperRepository
    from database.models import Paper
    # Import logger separately to avoid relative import issues
    import logging
except ImportError as e:
    print(f"Error importing modules: {e}", file=sys.stderr)
    print(f"Make sure research-tracker is set up at {RESEARCH_TRACKER}", file=sys.stderr)
    print("and venv is activated with: source ~/research-tracker/venv/bin/activate", file=sys.stderr)
    sys.exit(1)


def create_simple_logger(quiet: bool = False):
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


def search_papers_by_theme(theme: str, max_results: int = 10, source: str = "all", quiet: bool = False):
    """
    Search for papers by custom theme/topic
    
    Args:
        theme: Research theme/topic to search
        max_results: Maximum number of results to return
        source: Data source ('arxiv', 'semantic_scholar', or 'all')
        quiet: If True, suppress status messages (for JSON output)
    
    Returns:
        List of paper dictionaries
    """
    papers = []
    
    # Create a simple logger
    logger = create_simple_logger(quiet)
    
    try:
        if source in ["arxiv", "all"]:
            if not quiet:
                print(f"🔍 Searching arXiv for: {theme}", file=sys.stderr)
            arxiv_scraper = ArxivScraper(logger=logger)
            arxiv_papers = arxiv_scraper.search(theme, max_results=max_results)
            papers.extend(arxiv_papers)
            if not quiet:
                print(f"   Found {len(arxiv_papers)} papers from arXiv", file=sys.stderr)
        
        if source in ["semantic_scholar", "all"]:
            if not quiet:
                print(f"🔍 Searching Semantic Scholar for: {theme}", file=sys.stderr)
            ss_scraper = SemanticScholarScraper(logger=logger)
            ss_papers = ss_scraper.get_recent_papers([theme], max_results=max_results)
            papers.extend(ss_papers)
            if not quiet:
                print(f"   Found {len(ss_papers)} papers from Semantic Scholar", file=sys.stderr)
        
    except Exception as e:
        if not quiet:
            print(f"❌ Error searching papers: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return []
    
    # Remove duplicates by title
    seen_titles = set()
    unique_papers = []
    for paper in papers:
        title_lower = paper.get('title', '').lower()
        if title_lower and title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_papers.append(paper)
    
    # Sort by citations if available
    unique_papers.sort(
        key=lambda p: p.get('citations', 0) if p.get('citations') else 0,
        reverse=True
    )
    
    return unique_papers[:max_results]


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
