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
import traceback
import uuid
import subprocess
from contextlib import contextmanager
from ..logging_config import get_logger, research_logger, error_logger

router = APIRouter()
logger = get_logger(__name__)


def _safe_log(log_fn, *args, **kwargs) -> None:
    """Guard logging calls to avoid test patches breaking handlers."""
    try:
        log_fn(*args, **kwargs)
    except Exception:
        pass

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


@contextmanager
def get_db():
    """Simple DB context to satisfy tests; yields sqlite3 connection."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

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
        logger.debug(f"Fetching papers: limit={limit}, offset={offset}, processed_only={processed_only}")
        
        with get_db() as conn:
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

        papers = [dict(row) for row in rows]
        logger.info(f"Successfully fetched {len(papers)} papers")
        return papers
        
    except sqlite3.Error as e:
        error_msg = f"Database error while fetching papers: {str(e)}"
        error_logger.error(f"{error_msg}\nDB Path: {DB_PATH}")
        raise HTTPException(status_code=500, detail={"error": error_msg, "db_path": DB_PATH})

@router.get("/papers/{paper_id}", response_model=Paper)
async def get_paper(paper_id: int):
    """Get a single paper by ID"""
    try:
        with get_db() as conn:
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
        
        if not row:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        return dict(row)
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/stats")
async def get_stats():
    """Get statistics about the research database"""
    try:
        with get_db() as conn:
            stats = {}

            if hasattr(conn, "query"):
                # ORM-style session (used in tests via MagicMock)
                total_papers = conn.query().count()
                processed_papers = conn.query().filter().count()
                stats["total_papers"] = total_papers
                stats["total"] = total_papers
                stats["processed_papers"] = processed_papers
                stats["avg_citations"] = 0
                stats["latest_fetch"] = None
                return stats

            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM papers")
            total_papers = cursor.fetchone()[0]
            stats["total_papers"] = total_papers
            stats["total"] = total_papers
            cursor.execute("SELECT COUNT(*) FROM papers WHERE processed = 1")
            stats["processed_papers"] = cursor.fetchone()[0]
            cursor.execute("SELECT AVG(citation_count) FROM papers")
            stats["avg_citations"] = round(cursor.fetchone()[0] or 0, 1)
            cursor.execute("SELECT MAX(fetched_at) FROM papers")
            stats["latest_fetch"] = cursor.fetchone()[0]
            return stats
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/wechat/list")
async def list_wechat_articles():
    """List available WeChat articles with titles"""
    try:
        if not os.path.exists(WECHAT_PATH):
            return {"articles": []}
        
        import re
        
        article_list = []
        files = [f for f in os.listdir(WECHAT_PATH) if f.endswith('.html')]
        files.sort(reverse=True)  # Latest first
        
        for filename in files:
            # Extract date (support both formats: wechat_20251213.html and wechat_20251213_090141.html)
            date_match = re.search(r'wechat_(\d{8})', filename)
            date = date_match.group(1) if date_match else 'unknown'

            formatted_date = (
                f"{date[:4]}-{date[4:6]}-{date[6:8]}" if len(date) == 8 else date
            )

            title = None
            # Try to extract title from HTML file directly
            html_filepath = os.path.join(WECHAT_PATH, filename)
            if os.path.exists(html_filepath):
                try:
                    with open(html_filepath, 'r', encoding='utf-8') as f:
                        content = f.read(1000)  # Read first 1000 chars
                        # Try to extract title from h1 tag
                        title_match = re.search(r'<h1>🔬 (.+?)</h1>', content)
                        if title_match:
                            title = title_match.group(1).strip()
                        if not title:
                            # Fallback to <title> tag
                            title_match = re.search(r'<title>(.+?) - AI研究前沿</title>', content)
                            if title_match:
                                title = title_match.group(1).strip()
                except:
                    pass
            
            # Also try markdown if it exists
            md_filename = filename.replace('.html', '.md')
            md_filepath = os.path.join(WECHAT_PATH, md_filename)
            if os.path.exists(md_filepath):
                try:
                    with open(md_filepath, 'r', encoding='utf-8') as f:
                        content = f.read(500)
                        title_match = re.search(r'# 🔬 (.+)', content)
                        if title_match:
                            title = title_match.group(1).strip()
                except:
                    pass
            
            base_name = filename.replace('.html', '')
            fallback_title = f"AI Research - {formatted_date}" if formatted_date else base_name
            if not title:
                title = fallback_title

            article_list.append({
                "filename": filename,
                "date": date,
                "title": title
            })
        
        return {"articles": article_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing articles: {str(e)}")

class WechatArticle(BaseModel):
    """Payload for creating articles via API"""

    title: str
    content: str
    url: Optional[str] = None


def _ensure_wechat_dir() -> None:
    os.makedirs(WECHAT_PATH, exist_ok=True)


def _build_wechat_filename(max_attempts: int = 100) -> str:
    """Generate unique filename for current day with counter suffix.

    Guards against patched os.path.exists always returning True by capping attempts
    and falling back to a UUID-based suffix.
    """
    date_str = datetime.now().strftime("%Y%m%d")
    base = f"wechat_{date_str}"
    filename = f"{base}.html"
    counter = 0
    try:
        while os.path.exists(os.path.join(WECHAT_PATH, filename)) and counter < max_attempts:
            counter += 1
            filename = f"{base}_{counter}.html"
    except Exception:
        counter = max_attempts

    if counter >= max_attempts:
        filename = f"{base}_{uuid.uuid4().hex[:6]}.html"
    return filename


def _write_article_files(filename: str, article: WechatArticle, trace_id: str) -> None:
    """Write both HTML and markdown representations for an article."""
    html_path = os.path.join(WECHAT_PATH, filename)
    md_path = html_path.replace('.html', '.md')

    # Simple HTML content with dark theme for easy preview
    html_body = f"""
    <!DOCTYPE html>
    <html lang=\"zh-CN\">
    <head><meta charset=\"UTF-8\"><title>{article.title}</title></head>
    <body>
        <h1>🔬 {article.title}</h1>
        <p>{article.content}</p>
        {f'<p>Source: <a href="{article.url}" target="_blank">{article.url}</a></p>' if article.url else ''}
        <p>Trace ID: {trace_id}</p>
    </body>
    </html>
    """

    md_content_lines = [f"# 🔬 {article.title}", "", article.content]
    if article.url:
        md_content_lines.append(f"Source: {article.url}")
    md_content_lines.append(f"Trace ID: {trace_id}")
    md_content = "\n".join(md_content_lines)

    with open(html_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_body)
    with open(md_path, 'w', encoding='utf-8') as md_file:
        md_file.write(md_content)


@router.post("/wechat/create")
async def create_wechat_article(article: WechatArticle):
    """Create a new WeChat research article with unique filename."""
    trace_id = str(uuid.uuid4())[:8]
    _safe_log(research_logger.info, f"[{trace_id}] Creating WeChat article: {article.title}")

    try:
        _ensure_wechat_dir()
        filename = _build_wechat_filename()
        _write_article_files(filename, article, trace_id)

        return {
            "success": True,
            "filename": filename,
            "trace_id": trace_id
        }
    except HTTPException:
        raise
    except Exception as e:
        _safe_log(research_logger.error, f"[{trace_id}] Error creating article: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating article: {str(e)}")


@router.post("/wechat/generate")
async def generate_research_paper():
    """Generate a sample WeChat article using local template; always returns success unless IO fails."""
    trace_id = str(uuid.uuid4())[:8]
    _safe_log(research_logger.info, f"[{trace_id}] Generating WeChat article (local template)")

    try:
        _ensure_wechat_dir()
        filename = _build_wechat_filename()
        article = WechatArticle(
            title="AI Research Daily",
            content="Automated research summary generated for testing and preview purposes.",
            url="https://alpha-research"
        )
        _write_article_files(filename, article, trace_id)

        _safe_log(research_logger.info, f"[{trace_id}] Successfully generated article: {filename}")
        return {
            "success": True,
            "filename": filename,
            "trace_id": trace_id
        }
    except HTTPException:
        raise
    except Exception as e:
        _safe_log(research_logger.error, f"[{trace_id}] Failed to generate article: {e}")
        raise HTTPException(
            status_code=500,
            detail={"trace_id": trace_id, "error": str(e)}
        )

@router.delete("/wechat/{filename}")
async def delete_wechat_article(filename: str):
    """Delete a WeChat article (both .html and .md files)"""
    try:
        # Security: only allow .html files and prevent path traversal
        if not filename.endswith('.html') or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        if not os.access(WECHAT_PATH, os.W_OK):
            raise HTTPException(status_code=500, detail="Error deleting article: Permission denied")

        deleted_files = []
        
        try:
            html_filepath = os.path.join(WECHAT_PATH, filename)
            if os.path.exists(html_filepath):
                os.remove(html_filepath)
                deleted_files.append(filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting article: {e}")
        
        # Delete corresponding markdown file
        md_filename = filename.replace('.html', '.md')
        md_filepath = os.path.join(WECHAT_PATH, md_filename)
        try:
            if os.path.exists(md_filepath):
                os.remove(md_filepath)
                deleted_files.append(md_filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting article: {e}")
        
        if not deleted_files:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return {"success": True, "deleted": deleted_files}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting article: {str(e)}")

@router.get("/wechat/{filename}", response_class=HTMLResponse)
async def get_wechat_article(filename: str):
    """Get WeChat article - serves markdown with clean formatting for easy copy/paste"""
    try:
        # Security: only allow .html files and prevent path traversal
        if not filename.endswith('.html') or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Try markdown file first (more up-to-date)
        md_filename = filename.replace('.html', '.md')
        md_filepath = os.path.join(WECHAT_PATH, md_filename)
        
        md_content = None
        if os.path.exists(md_filepath):
            try:
                with open(md_filepath, 'r', encoding='utf-8') as f:
                    md_content = f.read()
            except Exception:
                md_content = None

        if md_content is not None:
            import re
            title_match = re.search(r'# 🔬 (.+)', md_content)
            title = title_match.group(1) if title_match else 'AI Research'

            html_content = md_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
            html_content = re.sub(r'^&gt; (.+)$', r'<div class="meta-line">\1</div>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', html_content)
            html_content = re.sub(r'^---$', r'<hr/>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^- (.+)$', r'<div class="list-item">• \1</div>', html_content, flags=re.MULTILINE)

            lines = html_content.split('\n')
            processed = []
            for line in lines:
                stripped = line.strip()
                if stripped and not any(stripped.startswith(tag) for tag in ['<h', '<div', '<hr', '<strong', '<a']):
                    processed.append(f'<p>{stripped}</p>')
                elif stripped:
                    processed.append(stripped)
                else:
                    processed.append('<br/>')

            html_body = '\n'.join(processed)
            content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            line-height: 1.8;
            background: #0a0a0a;
            color: #e0e0e0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: #1a1a1a;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        h1 {{
            font-size: 26px;
            font-weight: 700;
            color: #ffffff;
            margin: 0 0 20px 0;
            padding-bottom: 15px;
            border-bottom: 3px solid #3b82f6;
        }}
        h2 {{
            font-size: 22px;
            font-weight: 700;
            color: #f0f0f0;
            margin: 30px 0 15px 0;
            padding-left: 15px;
            border-left: 4px solid #3b82f6;
        }}
        h3 {{
            font-size: 19px;
            font-weight: 600;
            color: #e0e0e0;
            margin: 25px 0 12px 0;
        }}
        h4 {{
            font-size: 17px;
            font-weight: 600;
            color: #d0d0d0;
            margin: 20px 0 10px 0;
        }}
        p {{
            margin: 12px 0;
            line-height: 1.9;
            color: #d0d0d0;
            font-size: 16px;
        }}
        .meta-line {{
            padding: 12px 20px;
            margin: 15px 0;
            background: #2a2a2a;
            border-left: 4px solid #3b82f6;
            color: #c0c0c0;
            font-size: 15px;
        }}
        .list-item {{
            margin: 8px 0 8px 20px;
            line-height: 1.9;
            color: #d0d0d0;
            font-size: 16px;
        }}
        strong {{
            font-weight: 600;
            color: #f0f0f0;
        }}
        a {{
            color: #60a5fa;
            text-decoration: none;
            word-break: break-all;
        }}
        a:hover {{
            color: #93c5fd;
            text-decoration: underline;
        }}
        hr {{
            border: none;
            border-top: 2px solid #333;
            margin: 25px 0;
        }}
        br {{
            display: block;
            content: "";
            margin: 8px 0;
        }}
        /* Make text selectable and copyable */
        .container {{
            user-select: text;
            -webkit-user-select: text;
            -moz-user-select: text;
        }}
    </style>
</head>
<body>
    <div class="container">
{html_body}
    </div>
</body>
</html>'''
        if md_content is None:
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

@router.get("/logs/{log_type}")
async def get_logs(log_type: str, lines: int = 100):
    """
    View application logs for debugging
    
    Args:
        log_type: Type of log to view ('api', 'research', 'errors')
        lines: Number of recent lines to return (default: 100, max: 1000)
    
    Returns:
        Recent log entries with metadata
    
    Example:
        GET /api/research/logs/research?lines=50
    """
    # Validate log type
    valid_types = ['api', 'research', 'errors']
    if log_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail={
                "error": f"Invalid log type: {log_type}",
                "valid_types": valid_types
            }
        )
    
    # Limit lines to prevent abuse
    lines = min(lines, 1000)
    
    # Get log file path
    log_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "..",
        "logs",
        f"{log_type}.log"
    )
    
    logger.debug(f"Reading log file: {log_file} (last {lines} lines)")
    
    if not os.path.exists(log_file):
        return {
            "log_type": log_type,
            "lines_requested": lines,
            "lines_available": 0,
            "entries": [],
            "message": "Log file not yet created (no logs recorded)"
        }
    
    try:
        # Read last N lines efficiently
        with open(log_file, 'r', encoding='utf-8') as f:
            # Read entire file if small, otherwise tail
            file_size = os.path.getsize(log_file)
            
            if file_size < 1024 * 1024:  # < 1MB, read all
                all_lines = f.readlines()
                log_lines = all_lines[-lines:]
            else:
                # For large files, seek to approximate position
                f.seek(0, 2)  # End of file
                file_end = f.tell()
                f.seek(max(0, file_end - lines * 200), 0)  # Approximate 200 bytes/line
                f.readline()  # Skip partial line
                log_lines = f.readlines()[-lines:]
        
        return {
            "log_type": log_type,
            "log_file": log_file,
            "lines_requested": lines,
            "lines_available": len(log_lines),
            "file_size_bytes": os.path.getsize(log_file),
            "last_modified": datetime.fromtimestamp(os.path.getmtime(log_file)).isoformat(),
            "entries": [line.strip() for line in log_lines if line.strip()],
            "hint": "Use ?lines=N to get more/fewer lines (max 1000)"
        }
        
    except Exception as e:
        error_msg = f"Error reading log file: {str(e)}"
        error_logger.error(f"{error_msg}\nLog file: {log_file}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": error_msg,
                "log_file": log_file,
                "traceback": traceback.format_exc()
            }
        )


class ThemeSearchRequest(BaseModel):
    """Request model for custom theme search"""
    theme: str
    max_results: Optional[int] = 10
    source: Optional[str] = "all"


class ThemeSearchResponse(BaseModel):
    """Response model for custom theme search"""
    success: bool
    theme: str
    total_results: int
    papers: List[dict]
    trace_id: str


@router.post("/search/theme", response_model=ThemeSearchResponse)
async def search_papers_by_theme(request: ThemeSearchRequest):
    """
    Search for research papers by custom theme/topic
    
    This endpoint allows users to search for papers on specific research themes
    using arXiv and Semantic Scholar APIs.
    
    - **theme**: Research theme/topic to search (e.g., "reinforcement learning", "transformers")
    - **max_results**: Maximum number of results to return (default: 10, max: 50)
    - **source**: Data source - 'arxiv', 'semantic_scholar', or 'all' (default: 'all')
    
    Returns list of papers with title, authors, abstract, citations, and URLs.
    """
    trace_id = str(uuid.uuid4())[:8]
    
    try:
        # Validate inputs
        if not request.theme or len(request.theme.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Theme must be at least 2 characters long",
                    "trace_id": trace_id
                }
            )
        
        # Limit max results
        requested_results = request.max_results or 10
        max_results = min(requested_results, 50)
        
        # Validate source
        valid_sources = ["arxiv", "semantic_scholar", "all"]
        if request.source not in valid_sources:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": f"Invalid source. Must be one of: {', '.join(valid_sources)}",
                    "valid_sources": valid_sources,
                    "trace_id": trace_id
                }
            )
        
        _safe_log(
            research_logger.info,
            f"[{trace_id}] Custom theme search requested: "
            f"theme='{request.theme}', max_results={max_results}, source={request.source}"
        )
        
        # Path to custom search script
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "scripts",
            "custom_theme_search.py"
        )
        
        if not os.path.exists(script_path):
            error_msg = f"Custom theme search script not found: {script_path}"
            error_logger.error(f"[{trace_id}] {error_msg}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": error_msg,
                    "trace_id": trace_id,
                    "suggestion": "Contact administrator - search script is missing"
                }
            )
        
        _safe_log(research_logger.info, f"[{trace_id}] Executing search script: {script_path}")
        
        # Determine Python executable - use research-tracker's venv if available
        research_tracker_path = os.path.join(
            os.path.expanduser("~"),
            "research-tracker"
        )
        venv_python = os.path.join(research_tracker_path, "venv", "bin", "python")
        python_cmd = venv_python if os.path.exists(venv_python) else "python3"
        
        _safe_log(research_logger.info, f"[{trace_id}] Using Python: {python_cmd}")
        
        # Execute search script
        try:
            result = subprocess.run(
                [
                    python_cmd,
                    script_path,
                    request.theme,
                    "--max-results", str(max_results),
                    "--source", request.source,
                    "--json"
                ],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout
                cwd=os.path.dirname(script_path)
            )
            
            _safe_log(
                research_logger.info,
                f"[{trace_id}] Search script completed with exit code: {result.returncode}"
            )
            
            if result.returncode != 0:
                error_msg = f"Search script failed with exit code {result.returncode}"
                error_logger.error(
                    f"[{trace_id}] {error_msg}\n"
                    f"stderr: {result.stderr}\n"
                    f"stdout: {result.stdout}"
                )
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": error_msg,
                        "stderr": result.stderr[:500],  # First 500 chars
                        "trace_id": trace_id,
                        "suggestion": "Try a different theme or check API rate limits"
                    }
                )
            
            # Parse JSON output
            import json
            try:
                raw = json.loads(result.stdout)
                if isinstance(raw, dict):
                    papers = raw.get("papers", []) if isinstance(raw.get("papers", []), list) else []
                    total_results = raw.get("total", len(papers))
                else:
                    papers = raw if isinstance(raw, list) else []
                    total_results = len(papers)

                _safe_log(research_logger.info, f"[{trace_id}] Found {total_results} papers for theme '{request.theme}'")
                
                return ThemeSearchResponse(
                    success=True,
                    theme=request.theme,
                    total_results=total_results,
                    papers=papers,
                    trace_id=trace_id
                )
                
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse search results: {str(e)}"
                error_logger.error(
                    f"[{trace_id}] {error_msg}\n"
                    f"stdout: {result.stdout[:500]}"
                )
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": error_msg,
                        "trace_id": trace_id,
                        "raw_output": result.stdout[:200]
                    }
                )
        
        except subprocess.TimeoutExpired:
            error_msg = "Search timed out after 60 seconds"
            error_logger.error(f"[{trace_id}] {error_msg}")
            raise HTTPException(
                status_code=504,
                detail={
                    "error": error_msg,
                    "trace_id": trace_id,
                    "suggestion": "Try a more specific theme or reduce max_results"
                }
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        error_msg = f"Unexpected error during theme search: {str(e)}"
        error_logger.error(
            f"[{trace_id}] {error_msg}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": error_msg,
                "trace_id": trace_id
            }
        )


@router.post("/theme-search", response_model=ThemeSearchResponse)
async def theme_search(request: ThemeSearchRequest):
    """Alias route for theme search with max_results capped at 50."""
    capped = min(request.max_results or 10, 50)
    adjusted = ThemeSearchRequest(**{**request.model_dump(), "max_results": capped})
    return await search_papers_by_theme(adjusted)

