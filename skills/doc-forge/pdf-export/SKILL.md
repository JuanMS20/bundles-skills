---
name: pdf-export
description: "Convert Markdown manual to professional PDF with cover, TOC, chapters, page numbers, and clean typography. Use when user says 'exportar PDF', 'generar PDF', 'crear PDF del manual', or after manual-writer produces a book-structured Markdown manual."
---

# PDF Export

Converts a book-structured Markdown directory into a professional PDF using Python + WeasyPrint.

## When to Use

- After `manual-writer` produces Markdown chapters
- User says "PDF", "exportar", "generar documento", "imprimir"
- When updating an existing PDF after manual changes

## Prerequisites

First run installs dependencies:
```bash
uv pip install weasyprint markdown pygments
```

## Process

### FASE 1 — Locate Manual

1. Find the manual directory: `<project>/docs/manual-[mode]/`
2. If multiple modes exist, ask which one
3. Verify files exist: cover.md, toc.md, at least 1 chapter

### FASE 2 — Configure

Default config (user can override):
```yaml
font_size_body: 14pt       # Large, readable
font_size_h1: 28pt
font_size_h2: 20pt
font_size_h3: 16pt
font_family: "Segoe UI", "Helvetica Neue", Arial, sans-serif
page_size: A4
margins: 2.5cm
```

### FASE 3 — Generate PDF

Run the conversion script:
```bash
python "<skill_dir>/scripts/md-to-pdf.py" \
  --input "<project>/docs/manual-usuario/" \
  --output "<project>/docs/manual-usuario.pdf" \
  --config "<optional-config.yaml>"
```

The script:
1. Reads all .md files in order (sorted by filename)
2. Converts Markdown → HTML
3. Applies CSS template with book typography
4. Generates PDF with cover page, page numbers, headers

### FASE 4 — Verify

- [ ] PDF file exists and size > 0
- [ ] Open and spot-check: cover page renders, TOC is present, chapters are readable
- [ ] Font size is comfortable (14pt body minimum)
- [ ] Page numbers appear
- [ ] No broken images or missing content

## Custom Config

Create `docs/manual-config.yaml` to override defaults:
```yaml
title: "Mi Proyecto"
subtitle: "Manual de Usuario"
author: "Mi Empresa"
font_size_body: 16pt
accent_color: "#2563eb"
logo_path: "./assets/logo.png"
```

## Updating PDF

When manual content changes:
1. Re-run the same command
2. PDF is overwritten
3. Verify output

## Pitfalls

- **Missing weasyprint**: Install with `uv pip install weasyprint`. On Windows, may need GTK runtime. If fails, fallback: use markdown → HTML and open in browser → Print to PDF.
- **WeasyPrint Windows GTK failure**: On Windows without GTK, WeasyPrint throws `OSError: cannot load library 'libgobject-2.0-0'`. **Proven fallback**: Use `reportlab` instead (`uv pip install reportlab`). See [references/reportlab-fallback.md](references/reportlab-fallback.md) for working template with correct font sizes.
- **Code block font size TOO SMALL**: This is the #1 user complaint. PyMuPDF's `insert_htmlbox` renders code blocks at unreadable sizes. reportlab's `Preformatted` needs **fontSize=14 minimum** (16 preferred) for code/prompts. Never use fontSize < 12 for any content. Users will reject PDFs with small code blocks — they escalate frustration fast ("siguen MUY PEQUEÑOS").
- **HTML-only fallback**: If all PDF generators fail, generate standalone HTML with large CSS fonts (16px+ for code) and instruct user to Ctrl+P → Save as PDF from browser. This always works.
- **Special characters**: Ensure .md files are UTF-8 encoded. Spanish accents (á, é, ñ) must render correctly.
- **Image paths**: Use relative paths in Markdown. The script resolves them relative to the manual directory.
- **File ordering**: Files are sorted alphabetically. Use numbered prefixes (00-, 01-, 02-) to control chapter order.
