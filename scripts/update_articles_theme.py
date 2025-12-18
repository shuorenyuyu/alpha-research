#!/usr/bin/env python3
"""
Update all existing WeChat articles to use dark theme
"""
import os
import re
from pathlib import Path

# Dark theme CSS
DARK_THEME_CSS = """    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.8;
            color: #e5e7eb;
            max-width: 720px;
            margin: 0 auto;
            padding: 20px;
            background: #000000;
        }
        .article {
            background: linear-gradient(to bottom, #111827, #1f2937);
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            border: 1px solid #374151;
        }
        h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        h2 {
            color: #e5e7eb;
            font-size: 22px;
            margin-top: 25px;
            margin-bottom: 15px;
        }
        .date {
            color: #9ca3af;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .highlight {
            background: linear-gradient(120deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #667eea;
        }
        .insight {
            background: rgba(31, 41, 55, 0.5);
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border: 1px solid #374151;
        }
        .insight h3 {
            color: #d1d5db;
            margin-top: 0;
        }
        p {
            color: #d1d5db;
            margin: 12px 0;
        }
        ul {
            color: #d1d5db;
        }
        li {
            margin: 8px 0;
        }
        strong {
            color: #e5e7eb;
        }
        .tag {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            margin: 5px 5px 5px 0;
        }
    </style>"""

def update_article_theme(filepath):
    """Update a single article to use dark theme"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the style block
        style_pattern = r'<style>.*?</style>'
        
        if re.search(style_pattern, content, re.DOTALL):
            # Replace old style with dark theme
            updated_content = re.sub(style_pattern, DARK_THEME_CSS, content, flags=re.DOTALL)
            
            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            return True
        else:
            print(f"⚠️  No style block found in {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {filepath}: {e}")
        return False

def main():
    # Get data directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    wechat_dir = project_dir / "data" / "wechat_articles"
    
    if not wechat_dir.exists():
        print(f"❌ Directory not found: {wechat_dir}")
        return
    
    # Find all HTML files
    html_files = list(wechat_dir.glob("wechat_*.html"))
    
    if not html_files:
        print("No HTML files found")
        return
    
    print(f"Found {len(html_files)} articles to update")
    
    updated = 0
    for filepath in html_files:
        if update_article_theme(filepath):
            updated += 1
            print(f"✓ Updated: {filepath.name}")
    
    print(f"\n✅ Updated {updated}/{len(html_files)} articles to dark theme")

if __name__ == "__main__":
    main()
