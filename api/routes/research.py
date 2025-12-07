"""
Research papers API routes
Fetches data from research-tracker database
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import os

router = APIRouter()

# Path to research-tracker database
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "..",
    "research-tracker",
    "data",
    "papers.db"
)

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
    processed_only: bool = True
):
    """
    Get research papers
    
    - **limit**: Number of papers to return (default: 20)
    - **offset**: Pagination offset (default: 0)
    - **processed_only**: Only return AI-summarized papers (default: true)
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
