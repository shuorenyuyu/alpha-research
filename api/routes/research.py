"""
Research papers API routes
Fetches data from research-tracker database
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os

router = APIRouter()

# Path to research-tracker database and articles
# Try local data directory first (for deployment), then fall back to research-tracker
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
DB_PATH_LOCAL = os.path.join(DATA_DIR, "papers.db")
DB_PATH_TRACKER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "..",
    "research-tracker",
    "data",
    "papers.db"
)
DB_PATH = DB_PATH_LOCAL if os.path.exists(DB_PATH_LOCAL) else DB_PATH_TRACKER

WECHAT_PATH_LOCAL = os.path.join(DATA_DIR, "wechat_articles")
WECHAT_PATH_TRACKER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "..",
    "research-tracker",
    "data",
    "wechat_articles"
)
# Prefer research-tracker path for auto-sync, fall back to local if not available
WECHAT_PATH = WECHAT_PATH_TRACKER if os.path.exists(WECHAT_PATH_TRACKER) else WECHAT_PATH_LOCAL

class Paper(BaseModel):
    id: int
    title: str
    authors: str
    year: Optional[int]
    venue: Optional[str]
    abstract: Optional[str]
    url: Optional[str]
    citation_count: int
    summary_zh: Optional[str]
    investment_insights: Optional[str]
    fetched_at: str
    processed: bool

@router.get("/papers", response_model=List[Paper])
async def get_papers(
    limit: int = 20,
    offset: int = 0,
    processed_only: bool = False
):
    """
    Get research papers
    
    - **limit**: Number of papers to return (default: 20)
    - **offset**: Pagination offset (default: 0)
    - **processed_only**: Only return AI-summarized papers (default: false)
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT 
                id, title, authors, year, venue, abstract, url,
                citation_count, summary_zh, investment_insights,
                fetched_at, processed
            FROM papers
        """
        
        if processed_only:
            query += " WHERE processed = 1"
        
        query += " ORDER BY fetched_at DESC LIMIT ? OFFSET ?"
        
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        conn.close()
        
        papers = [dict(row) for row in rows]
        return papers
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/papers/{paper_id}", response_model=Paper)
async def get_paper(paper_id: int):
    """Get a single paper by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, title, authors, year, venue, abstract, url,
                citation_count, summary_zh, investment_insights,
                fetched_at, processed
            FROM papers
            WHERE id = ?
        """, (paper_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        return dict(row)
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/stats")
async def get_stats():
    """Get statistics about the research database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total papers
        cursor.execute("SELECT COUNT(*) FROM papers")
        stats["total_papers"] = cursor.fetchone()[0]
        
        # Processed papers
        cursor.execute("SELECT COUNT(*) FROM papers WHERE processed = 1")
        stats["processed_papers"] = cursor.fetchone()[0]
        
        # Average citations
        cursor.execute("SELECT AVG(citation_count) FROM papers")
        stats["avg_citations"] = round(cursor.fetchone()[0] or 0, 1)
        
        # Latest paper date
        cursor.execute("SELECT MAX(fetched_at) FROM papers")
        stats["latest_fetch"] = cursor.fetchone()[0]
        
        conn.close()
        return stats
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/wechat/list")
async def list_wechat_articles():
    """List available WeChat articles"""
    try:
        if not os.path.exists(WECHAT_PATH):
            return {"articles": []}
        
        articles = [f for f in os.listdir(WECHAT_PATH) if f.endswith('.html')]
        articles.sort(reverse=True)  # Latest first
        return {"articles": articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing articles: {str(e)}")

@router.get("/wechat/{filename}", response_class=HTMLResponse)
async def get_wechat_article(filename: str):
    """Get WeChat article HTML content with dark theme"""
    try:
        # Security: only allow .html files and prevent path traversal
        if not filename.endswith('.html') or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        filepath = os.path.join(WECHAT_PATH, filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Article not found")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Inject dark theme CSS
        dark_theme_css = """
        <style>
            body {
                background: #0a0a0a !important;
                color: #e0e0e0 !important;
            }
            .container {
                background: #1a1a1a !important;
                box-shadow: 0 2px 8px rgba(0,0,0,0.5) !important;
            }
            h1 {
                color: #ffffff !important;
                border-bottom-color: #3b82f6 !important;
            }
            h2 {
                color: #f0f0f0 !important;
                border-left-color: #3b82f6 !important;
            }
            h3 {
                color: #e0e0e0 !important;
            }
            h4, h5 {
                color: #d0d0d0 !important;
            }
            p {
                color: #d0d0d0 !important;
            }
            .meta {
                background: #2a2a2a !important;
                color: #d0d0d0 !important;
            }
            .meta p {
                color: #d0d0d0 !important;
            }
            .investment-section {
                background: linear-gradient(135deg, #1e3a5f 0%, #2d1e3f 100%) !important;
            }
            .abstract {
                background: #1e2a3a !important;
                border-left-color: #3b82f6 !important;
                color: #d0d0d0 !important;
            }
            .content {
                color: #d0d0d0 !important;
            }
            .tags {
                background: #2a2a2a !important;
            }
            .tag {
                background: #3b82f6 !important;
                color: #ffffff !important;
            }
            a {
                color: #60a5fa !important;
            }
            a:hover {
                color: #93c5fd !important;
            }
            code {
                background: #2a2a2a !important;
                color: #e0e0e0 !important;
            }
            strong {
                color: #f0f0f0 !important;
            }
            li {
                color: #d0d0d0 !important;
            }
        </style>
        """
        
        # Inject the dark theme CSS before </head>
        if '</head>' in content:
            content = content.replace('</head>', f'{dark_theme_css}</head>')
        
        return HTMLResponse(content=content)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading article: {str(e)}")
