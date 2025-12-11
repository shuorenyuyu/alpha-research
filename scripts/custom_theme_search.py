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
sys.path.insert(0, str(RESEARCH_TRACKER / "src"))

from scrapers.arxiv_scraper import ArxivScraper
from scrapers.semantic_scholar_scraper import SemanticScholarScraper
from database.repository import PaperRepository
from database.models import Paper


def search_papers_by_theme(theme: str, max_results: int = 10, source: str = "all"):
    """
    Search for papers by custom theme/topic
    
    Args:
        theme: Research theme/topic to search
        max_results: Maximum number of results to return
        source: Data source ('arxiv', 'semantic_scholar', or 'all')
    
    Returns:
        List of paper dictionaries
    """
    papers = []
    
    try:
        if source in ["arxiv", "all"]:
            print(f"🔍 Searching arXiv for: {theme}")
            arxiv_scraper = ArxivScraper()
            arxiv_papers = arxiv_scraper.search(theme, max_results=max_results)
            papers.extend(arxiv_papers)
            print(f"   Found {len(arxiv_papers)} papers from arXiv")
        
        if source in ["semantic_scholar", "all"]:
            print(f"🔍 Searching Semantic Scholar for: {theme}")
            ss_scraper = SemanticScholarScraper()
            ss_papers = ss_scraper.get_recent_papers([theme], max_results=max_results)
            papers.extend(ss_papers)
            print(f"   Found {len(ss_papers)} papers from Semantic Scholar")
        
    except Exception as e:
        print(f"❌ Error searching papers: {str(e)}", file=sys.stderr)
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
    
    papers = search_papers_by_theme(args.theme, args.max_results, args.source)
    
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
