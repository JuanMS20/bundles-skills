---
name: office-automation
description: >
  Read, extract, and manipulate Office documents (Word, Excel, PowerPoint, PDF) programmatically with Python.
  Fills PowerPoint templates from research content, extracts structured data from .docx/.pdf/.xlsm,
  and generates presentation-ready files. Use when user asks to fill slides, extract content from
  academic papers, merge data from multiple document formats, or automate Office document workflows.
  Covers python-docx, openpyxl, pymupdf/PyPDF2, python-pptx on Windows.
tags: [office, pptx, docx, xlsx, pdf, python, automation, presentation, academic]
---

# Office Document Automation

Read, extract, and manipulate Office/PDF documents programmatically. Common use case:
fill a PowerPoint template from a research paper (Word) + evaluation data (PDF/Excel).

## When to Use

- User asks to fill PowerPoint slides from a Word document
- Extract content from .docx/.pdf/.xlsm for reuse
- Automate Office document workflows (merge, transform, populate)
- Academic presentations: thesis defense, research summaries

## Required Libraries

Install before any Office work:

```bash
uv pip install python-docx openpyxl pymupdf python-pptx PyPDF2
```

On Windows with `uv`, this is the reliable install method. `pip` may fail with
"SRE module mismatch" if the system Python has conflicting `re` module versions.

## Core Techniques

### Reading Word (.docx)

```python
from docx import Document
doc = Document('file.docx')

# Paragraphs with style info
for p in doc.paragraphs:
    if p.text.strip():
        print(f'[{p.style.name}] {p.text[:200]}')

# Tables
for table in doc.tables:
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        print(cells)
```

Key: `p.style.name` tells you if it's a heading, body text, list, etc. Use this
to identify sections (Heading 1 = major sections, List Paragraph = bullets).

### Reading PDF

```python
import fitz  # pymupdf
doc = fitz.open('file.pdf')
for page in doc:
    print(page.get_text())
```

pymupdf is faster and more reliable than PyPDF2 for text extraction.

### Reading Excel (.xlsm with macros)

```python
import openpyxl
wb = openpyxl.load_workbook('file.xlsm', keep_vba=True)
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    for row in ws.iter_rows(values_only=False):
        vals = [(c.value, c.coordinate) for c in row if c.value is not None]
        if vals:
            print(vals)
```

Use `keep_vba=True` for .xlsm files to avoid errors.

### Filling PowerPoint Templates

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

prs = Presentation('template.pptx')

# Navigate existing shapes
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                # Match and replace placeholder text
                if 'Placeholder' in para.text:
                    for run in para.runs:
                        run.text = ''
                    if para.runs:
                        para.runs[0].text = 'New content'
                        para.runs[0].font.size = Pt(14)
                        para.runs[0].font.bold = True

# Add new text boxes
txBox = slide.shapes.add_textbox(
    Inches(0.8), Inches(1.8), Inches(8.2), Inches(3.5)
)
tf = txBox.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
run = p.add_run()
run.text = 'Content here'
run.font.size = Pt(12)

prs.save('output.pptx')
```

### Slide Structure Detection

Inspect template before filling:

```python
prs = Presentation('template.pptx')
for i, slide in enumerate(prs.slides):
    print(f'Slide {i+1} (layout: {slide.slide_layout.name})')
    for shape in slide.shapes:
        print(f'  {shape.name}: text={shape.has_text_frame}, table={shape.has_table}')
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                if para.text.strip():
                    print(f'    "{para.text[:100]}"')
```

This reveals which shapes are placeholders and what text they contain.

### Extracting Images from Word

Word docs often contain figures (app screenshots, diagrams, charts) that must
go into the presentation. Extract them via relationship inspection:

```python
from docx.opc.constants import RELATIONSHIP_TYPE as RT
import os

doc = Document('paper.docx')
os.makedirs('images', exist_ok=True)

count = 0
for rel in doc.part.rels.values():
    if 'image' in rel.reltype:
        img_data = rel.target_part.blob
        ext = rel.target_part.content_type.split('/')[-1]
        if ext == 'jpeg': ext = 'jpg'
        fname = f'image_{count:02d}.{ext}'
        with open(f'images/{fname}', 'wb') as f:
            f.write(img_data)
        count += 1
```

**Identify images**: Use `vision_analyze` on each extracted image to understand
what it shows (screenshot, diagram, formula, table). Then map images to their
figure captions in the Word doc by checking paragraphs near each image:

```python
from docx.oxml.ns import qn
for i, para in enumerate(doc.paragraphs):
    for run in para.runs:
        if run._element.findall(qn('w:drawing')):
            prev = doc.paragraphs[i-1].text.strip() if i > 0 else ''
            print(f'Image at para {i}: context = {prev[:100]}')
```

### Creating From Scratch vs Filling Template

**When to fill template**: Template has simple placeholders, design is basic,
python-pptx can match the layout.

**When to create from scratch**: Template has complex design (custom shapes,
backgrounds, grouped elements, Google Slides import). python-pptx will produce
ugly results trying to edit these. Better to:
1. Create a standalone well-designed PPTX from scratch
2. User copies content into the template manually

This is the **copy-paste pattern** — valid and often preferred by users.

**Signs template filling will fail**:
- Template has grouped shapes (GROUP type) that can't be easily edited
- Backgrounds are images, not solid fills
- Text is inside auto-shapes with complex formatting
- User says output "looks horrible"

## Pitfalls

### Windows File Locking (CRITICAL)

**Problem**: If the target .pptx is open in PowerPoint, `shutil.copy2()` or
`open()` will fail with `PermissionError` or `[Errno 13]`.

**Symptom**: Script appears to hang or user sees "BLOCKED" — but the user
isn't blocking anything. The file is locked by another process.

**Fix**: ALWAYS write to a NEW file in a DIFFERENT location. Never overwrite
the source file in-place.

```python
import shutil
src = r'C:\path\to\template.pptx'
dst = r'C:\path\to\output\filled.pptx'  # Different directory!
shutil.copy2(src, dst)
prs = Presentation(dst)
# ... modify ...
prs.save(dst)
```

### Accented Filenames on Windows/MSYS

**Problem**: Python scripts via `terminal()` run in bash (MSYS). Files with
accented characters (é, ñ, á) in paths may fail with `FileNotFoundError`.

**Fix**: Use raw strings with escaped backslashes, or verify the exact
filename with `ls` first:

```python
src = r'C:\Users\...\Plantilla_Presentación_USC.pptx'  # Accented!
```

### Placeholder Text Matching

**Problem**: Template placeholders may span multiple runs. For example,
"Titulo trabajo" might be one run or split across two.

**Fix**: Match on `para.text.strip()` (the full paragraph text), not on
individual runs. Then clear all runs and set the first one:

```python
for para in shape.text_frame.paragraphs:
    if 'Placeholder' in para.text:  # Match paragraph text
        for run in para.runs:
            run.text = ''  # Clear all runs
        if para.runs:
            para.runs[0].text = 'New text'  # Set first run
```

### Text Overflow on Slides

**Problem**: Adding too much text to a slide makes it unreadable during
presentation.

**Rule**: Max ~6 bullet points per slide, ~12 words per bullet. If the source
content is longer, summarize — don't dump.

### Visual Quality Rejection (CRITICAL)

**Problem**: python-pptx generates functionally correct but visually ugly
presentations. Users will reject them ("esta horrible").

**Root cause**: python-pptx can't render complex template designs — custom
backgrounds, grouped shapes, gradient fills, imported Google Slides elements.

**Fix**: When the output must look professional:
1. Create from scratch with explicit color scheme, proper spacing, shapes
2. Use `MSO_SHAPE` for backgrounds, cards, accent elements
3. Add proper visual hierarchy: headers, body, accent colors
4. Include images at proper sizes with captions
5. Consider the copy-paste pattern (standalone → template)

**Design recipe for academic presentations**:
- Dark header bar (institutional color) + gold accent line
- Content area with bullet points or cards
- Images with captions below
- Slide numbers
- Clean closing slide

### Installing Packages on Windows with uv

`pip install` may fail with "SRE module mismatch" on Windows if system Python
has conflicting modules. Always use `uv pip install` instead:

```bash
uv pip install python-docx openpyxl pymupdf python-pptx PyPDF2
```

## Workflow for Academic Presentations

1. **Read all source files** (Word for content, PDF for grades/feedback, Excel for data)
2. **Inspect the PPTX template** — identify every placeholder shape and its text
3. **Map content to slides** — each Word section maps to a slide
4. **Fill the template** — modify shapes, add textboxes where needed
5. **Save to NEW location** — never overwrite the original template
6. **Verify** — re-read the output file and confirm all slides have content
7. **Summarize for user** — list what went where + any feedback from evaluations

## References

- python-docx: https://python-docx.readthedocs.io/
- python-pptx: https://python-pptx.readthedocs.io/
- pymupdf: https://pymupdf.readthedocs.io/
- openpyxl: https://openpyxl.readthedocs.io/
