#!/usr/bin/env python3
"""
md-to-pdf.py — Convert a directory of Markdown chapters into a professional PDF book.

Usage:
    python md-to-pdf.py --input ./manual-usuario/ --output ./manual.pdf
    python md-to-pdf.py --input ./manual-usuario/ --output ./manual.pdf --config ./manual-config.yaml

Requires: uv pip install weasyprint markdown pygments
"""

import argparse
import os
import sys
import re
from pathlib import Path

try:
    import markdown
    from markdown.extensions.toc import TocExtension
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
except ImportError:
    print("ERROR: 'markdown' package not found. Run: uv pip install markdown pygments")
    sys.exit(1)

try:
    from weasyprint import HTML
except ImportError:
    print("ERROR: 'weasyprint' package not found. Run: uv pip install weasyprint")
    print("NOTE: On Windows, WeasyPrint may need GTK runtime. If install fails,")
    print("      use the HTML fallback: open the .html output in browser and Print to PDF.")
    sys.exit(1)

# Optional YAML config
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


DEFAULT_CONFIG = {
    "title": "Manual",
    "subtitle": "",
    "author": "",
    "version": "",
    "font_size_body": "14pt",
    "font_size_h1": "28pt",
    "font_size_h2": "20pt",
    "font_size_h3": "16pt",
    "font_size_h4": "14pt",
    "font_family": "'Segoe UI', 'Helvetica Neue', Arial, sans-serif",
    "page_size": "A4",
    "margins": "2.5cm",
    "accent_color": "#1a1a2e",
    "link_color": "#2563eb",
    "logo_path": "",
}

CSS_TEMPLATE = """
@page {{
    size: {page_size};
    margin: {margins};

    @bottom-center {{
        content: counter(page);
        font-size: 10pt;
        color: #666;
        font-family: {font_family};
    }}

    @top-right {{
        content: "{title}";
        font-size: 9pt;
        color: #999;
        font-family: {font_family};
    }}
}}

@page :first {{
    @bottom-center {{ content: none; }}
    @top-right {{ content: none; }}
}}

body {{
    font-family: {font_family};
    font-size: {font_size_body};
    line-height: 1.7;
    color: #1a1a1a;
    max-width: 100%;
}}

/* Cover page */
.cover {{
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
    text-align: center;
}}

.cover h1 {{
    font-size: 36pt;
    color: {accent_color};
    margin-bottom: 0.3em;
    border: none;
    line-height: 1.2;
}}

.cover .subtitle {{
    font-size: 18pt;
    color: #555;
    margin-bottom: 2em;
}}

.cover .meta {{
    font-size: 12pt;
    color: #777;
    line-height: 2;
}}

/* Chapter headers */
h1 {{
    font-size: {font_size_h1};
    color: {accent_color};
    border-bottom: 3px solid {accent_color};
    padding-bottom: 0.3em;
    margin-top: 1.5em;
    page-break-before: always;
}}

h1:first-child {{
    page-break-before: avoid;
}}

h2 {{
    font-size: {font_size_h2};
    color: #2d2d2d;
    margin-top: 1.2em;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.2em;
}}

h3 {{
    font-size: {font_size_h3};
    color: #444;
    margin-top: 1em;
}}

h4 {{
    font-size: {font_size_h4};
    color: #555;
    margin-top: 0.8em;
}}

/* Paragraphs */
p {{
    margin: 0.6em 0;
    text-align: justify;
}}

/* Lists */
ul, ol {{
    margin: 0.5em 0;
    padding-left: 1.5em;
}}

li {{
    margin: 0.3em 0;
}}

/* Code blocks */
pre {{
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 1em;
    font-size: 11pt;
    line-height: 1.4;
    overflow-wrap: break-word;
    white-space: pre-wrap;
    page-break-inside: avoid;
}}

code {{
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 11pt;
}}

p code, li code {{
    background-color: #f0f0f0;
    padding: 0.1em 0.3em;
    border-radius: 3px;
    color: #c7254e;
}}

/* Tables */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 12pt;
    page-break-inside: avoid;
}}

th {{
    background-color: {accent_color};
    color: white;
    padding: 0.6em 0.8em;
    text-align: left;
    font-weight: 600;
}}

td {{
    padding: 0.5em 0.8em;
    border-bottom: 1px solid #ddd;
}}

tr:nth-child(even) td {{
    background-color: #f9f9f9;
}}

/* Blockquotes (tips, notes) */
blockquote {{
    border-left: 4px solid {accent_color};
    background-color: #f8f9fa;
    padding: 0.8em 1em;
    margin: 1em 0;
    font-style: normal;
}}

blockquote p {{
    margin: 0.3em 0;
}}

/* Links */
a {{
    color: {link_color};
    text-decoration: none;
}}

/* Images */
img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
}}

/* Horizontal rules */
hr {{
    border: none;
    border-top: 2px solid #eee;
    margin: 2em 0;
}}

/* TOC */
.toc {{
    page-break-after: always;
}}

.toc h1 {{
    page-break-before: avoid;
}}

.toc ul {{
    list-style: none;
    padding-left: 0;
}}

.toc > ul > li {{
    margin: 0.8em 0;
    font-size: 14pt;
    font-weight: 600;
}}

.toc > ul > li > ul > li {{
    margin: 0.3em 0;
    font-size: 12pt;
    font-weight: normal;
    padding-left: 1.5em;
}}

/* Strong emphasis */
strong {{
    color: #1a1a1a;
}}
"""


def load_config(config_path: str | None) -> dict:
    """Load config from YAML file, merged with defaults."""
    config = dict(DEFAULT_CONFIG)
    if config_path and Path(config_path).exists():
        if not HAS_YAML:
            print("WARNING: PyYAML not installed. Using default config. Run: uv pip install pyyaml")
        else:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
                config.update(user_config)
    return config


def read_chapters(input_dir: Path) -> list[tuple[str, str]]:
    """Read all .md files in order. Returns list of (filename, content)."""
    md_files = sorted(input_dir.glob("*.md"))
    if not md_files:
        print(f"ERROR: No .md files found in {input_dir}")
        sys.exit(1)

    chapters = []
    for f in md_files:
        content = f.read_text(encoding="utf-8")
        chapters.append((f.name, content))
    return chapters


def md_to_html(md_text: str) -> str:
    """Convert Markdown to HTML with extensions."""
    md = markdown.Markdown(
        extensions=[
            TocExtension(permalink=False, toc_depth="1-3"),
            TableExtension(),
            FencedCodeExtension(),
            "meta",
        ]
    )
    html = md.convert(md_text)
    return html


def build_cover_html(config: dict) -> str:
    """Build HTML for the cover page."""
    parts = ['<div class="cover">']
    parts.append(f'<h1>{config["title"]}</h1>')
    if config.get("subtitle"):
        parts.append(f'<div class="subtitle">{config["subtitle"]}</div>')
    parts.append('<div class="meta">')
    if config.get("author"):
        parts.append(f'<div>{config["author"]}</div>')
    if config.get("version"):
        parts.append(f'<div>Versión {config["version"]}</div>')
    import datetime
    parts.append(f'<div>{datetime.date.today().strftime("%B %d, %Y")}</div>')
    parts.append("</div></div>")
    return "\n".join(parts)


def build_full_html(chapters: list[tuple[str, str]], config: dict) -> str:
    """Assemble full HTML document from chapters."""
    css = CSS_TEMPLATE.format(**config)

    body_parts = []

    # Cover page
    body_parts.append(build_cover_html(config))

    for filename, content in chapters:
        html_content = md_to_html(content)

        # Special handling for cover.md — replace the auto-generated cover
        if filename == "cover.md":
            # Use the cover.md content as the cover instead
            body_parts[-1] = f'<div class="cover">{html_content}</div>'
            continue

        # Add TOC class if it's the toc file
        if "toc" in filename.lower():
            body_parts.append(f'<div class="toc">{html_content}</div>')
        else:
            body_parts.append(html_content)

    body = "\n<hr>\n".join(body_parts)

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{config["title"]}</title>
    <style>{css}</style>
</head>
<body>
{body}
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown manual to PDF")
    parser.add_argument("--input", "-i", required=True, help="Directory containing .md chapter files")
    parser.add_argument("--output", "-o", required=True, help="Output PDF path")
    parser.add_argument("--config", "-c", default=None, help="Optional YAML config file")
    parser.add_argument("--html-only", action="store_true", help="Generate HTML only (fallback if WeasyPrint fails)")
    args = parser.parse_args()

    input_dir = Path(args.input)
    if not input_dir.is_dir():
        print(f"ERROR: {input_dir} is not a directory")
        sys.exit(1)

    config = load_config(args.config)

    # Auto-detect title from cover.md if not in config
    cover_path = input_dir / "cover.md"
    if cover_path.exists() and config["title"] == "Manual":
        cover_content = cover_path.read_text(encoding="utf-8")
        # Extract first H1
        match = re.search(r"^#\s+(.+)$", cover_content, re.MULTILINE)
        if match:
            config["title"] = match.group(1).strip()
        # Extract subtitle from first H2
        match = re.search(r"^##\s+(.+)$", cover_content, re.MULTILINE)
        if match:
            config["subtitle"] = match.group(1).strip()

    print(f"Reading chapters from: {input_dir}")
    chapters = read_chapters(input_dir)
    print(f"Found {len(chapters)} chapters")

    full_html = build_full_html(chapters, config)

    # Always save HTML (useful as fallback)
    output_path = Path(args.output)
    html_path = output_path.with_suffix(".html")
    html_path.write_text(full_html, encoding="utf-8")
    print(f"HTML saved: {html_path}")

    if args.html_only:
        print("HTML-only mode. Open the .html file in a browser and Print to PDF.")
        return

    # Generate PDF
    print(f"Generating PDF: {output_path}")
    try:
        HTML(string=full_html, base_url=str(input_dir.resolve())).write_pdf(str(output_path))
        size_kb = output_path.stat().st_size / 1024
        print(f"PDF generated: {output_path} ({size_kb:.0f} KB)")
    except Exception as e:
        print(f"PDF generation failed: {e}")
        print(f"HTML fallback available at: {html_path}")
        print("Open the HTML in a browser and use Print → Save as PDF")
        sys.exit(1)


if __name__ == "__main__":
    main()
