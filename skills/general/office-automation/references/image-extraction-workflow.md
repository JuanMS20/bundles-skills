# Image Extraction from Word Documents

## Complete Workflow

### Step 1: Extract all images
```python
from docx import Document
from docx.oxml.ns import qn
import os

doc = Document('paper.docx')
out_dir = 'images'
os.makedirs(out_dir, exist_ok=True)

# via relationships (gets all embedded images)
count = 0
for rel in doc.part.rels.values():
    if 'image' in rel.reltype:
        img_data = rel.target_part.blob
        ext = rel.target_part.content_type.split('/')[-1]
        if ext == 'jpeg': ext = 'jpg'
        fname = f'imagen_{count:02d}.{ext}'
        with open(os.path.join(out_dir, fname), 'wb') as f:
            f.write(img_data)
        print(f'{fname} -> {len(img_data)} bytes')
        count += 1
```

### Step 2: Map images to context
Find what each image represents by checking surrounding paragraphs:

```python
for i, para in enumerate(doc.paragraphs):
    for run in para.runs:
        if run._element.findall(qn('w:drawing')):
            prev = doc.paragraphs[i-1].text.strip() if i > 0 else ''
            nxt = doc.paragraphs[i+1].text.strip() if i < len(doc.paragraphs)-1 else ''
            print(f'Image at para {i}: before={prev[:80]}, after={nxt[:80]}')
```

### Step 3: Visually identify each image
Use `vision_analyze` to confirm what each image shows (screenshot, diagram, etc.)

### Step 4: Insert into PPTX
```python
slide.shapes.add_picture('images/img.jpg', Inches(0.8), Inches(1.7), height=Inches(2.3))
```

## Common Image Types in Academic Papers

| Type | Typical Size | Best Slide |
|---|---|---|
| Use case diagram | Medium PNG | Methodology |
| Architecture diagram | Medium PNG | Methodology |
| App screenshots | Multiple JPGs | Results/Application |
| Charts/graphs | PNG | Results |
| Formulas | Small PNG | Methodology |

## Tips
- Very small files (<5KB) are likely icons/logos, not content figures
- Duplicate images at same paragraph = same figure (multiple crops)
- Group app screenshots in grid layout on one slide
