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
    """List available WeChat articles with titles"""
    try:
        if not os.path.exists(WECHAT_PATH):
            return {"articles": []}
        
        import re
        
        article_list = []
        files = [f for f in os.listdir(WECHAT_PATH) if f.endswith('.html')]
        files.sort(reverse=True)  # Latest first
        
        for filename in files:
            # Extract date
            date_match = re.search(r'wechat_(\d{8})\.html', filename)
            date = date_match.group(1) if date_match else 'unknown'
            
            # Try to get title from markdown
            md_filename = filename.replace('.html', '.md')
            md_filepath = os.path.join(WECHAT_PATH, md_filename)
            title = f"AI Research - {date[:4]}-{date[4:6]}-{date[6:8]}"
            
            if os.path.exists(md_filepath):
                try:
                    with open(md_filepath, 'r', encoding='utf-8') as f:
                        content = f.read(500)  # Read first 500 chars
                        title_match = re.search(r'# 🔬 (.+)', content)
                        if title_match:
                            title = title_match.group(1).strip()
                except:
                    pass
            
            article_list.append({
                "filename": filename,
                "date": date,
                "title": title
            })
        
        return {"articles": article_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing articles: {str(e)}")

class NewPaper(BaseModel):
    title: str
    content: str
    url: Optional[str] = None

@router.post("/wechat/create")
async def create_wechat_article(paper: NewPaper):
    """Create a new WeChat research article"""
    try:
        # Ensure directory exists
        os.makedirs(WECHAT_PATH, exist_ok=True)
        
        # Generate filename with today's date
        from datetime import datetime
        today = datetime.now().strftime("%Y%m%d")
        
        # Check if file already exists for today
        base_filename = f"wechat_{today}"
        counter = 1
        filename = base_filename
        while os.path.exists(os.path.join(WECHAT_PATH, f"{filename}.md")):
            filename = f"{base_filename}_{counter}"
            counter += 1
        
        md_filename = f"{filename}.md"
        md_filepath = os.path.join(WECHAT_PATH, md_filename)
        
        # Create markdown content
        md_content = f"""# 🔬 {paper.title}

> **发布日期**: {datetime.now().strftime("%Y-%m-%d")}  
> **来源**: 手动添加
"""
        
        if paper.url:
            md_content += f"> **论文链接**: [{paper.url}]({paper.url})\n"
        
        md_content += f"""

---

## 📄 研究内容

{paper.content}

---

## 📊 总结

手动添加的研究论文分析。
"""
        
        # Write markdown file
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return {
            "success": True,
            "filename": f"{filename}.html",
            "message": f"Article created: {md_filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating article: {str(e)}")

@router.delete("/wechat/{filename}")
async def delete_wechat_article(filename: str):
    """Delete a WeChat article (both .html and .md files)"""
    try:
        # Security: only allow .html files and prevent path traversal
        if not filename.endswith('.html') or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        deleted_files = []
        
        # Delete HTML file
        html_filepath = os.path.join(WECHAT_PATH, filename)
        if os.path.exists(html_filepath):
            os.remove(html_filepath)
            deleted_files.append(filename)
        
        # Delete corresponding markdown file
        md_filename = filename.replace('.html', '.md')
        md_filepath = os.path.join(WECHAT_PATH, md_filename)
        if os.path.exists(md_filepath):
            os.remove(md_filepath)
            deleted_files.append(md_filename)
        
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
        
        if os.path.exists(md_filepath):
            # Read markdown
            with open(md_filepath, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Extract title for HTML
            import re
            title_match = re.search(r'# 🔬 (.+)', md_content)
            title = title_match.group(1) if title_match else 'AI Research'
            
            # Preserve markdown formatting but make it HTML-safe and styled
            # Convert to HTML while keeping it readable
            html_content = md_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # Convert markdown syntax to HTML for display
            html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
            html_content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html_content, flags=re.MULTILINE)
            
            # Bold text
            html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
            
            # Blockquotes
            html_content = re.sub(r'^&gt; (.+)$', r'<div class="meta-line">\1</div>', html_content, flags=re.MULTILINE)
            
            # Links
            html_content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2" target="_blank">\1</a>', html_content)
            
            # Horizontal rules
            html_content = re.sub(r'^---$', r'<hr/>', html_content, flags=re.MULTILINE)
            
            # Lists
            html_content = re.sub(r'^- (.+)$', r'<div class="list-item">• \1</div>', html_content, flags=re.MULTILINE)
            
            # Paragraphs - wrap non-tagged lines
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
            
            # Create clean HTML with dark theme
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
        else:
            # Fallback to HTML file if markdown doesn't exist
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
