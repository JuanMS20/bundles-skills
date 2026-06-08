# ReportLab PDF Fallback (Windows sin GTK)

Cuando WeasyPrint falla por falta de GTK en Windows, usar reportlab directamente.

## Instalación

```bash
uv pip install reportlab
```

## Template funcional

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from pathlib import Path

doc = SimpleDocTemplate("output.pdf", pagesize=A4,
                       leftMargin=2*cm, rightMargin=2*cm,
                       topMargin=2*cm, bottomMargin=2*cm)

styles = getSampleStyleSheet()

# CRITICAL: fontSize >= 14 para código, 16+ preferido
code_style = ParagraphStyle('Code', parent=styles['Code'],
                           fontSize=14, fontName='Courier',
                           backColor=colors.HexColor('#f5f5f5'),
                           borderColor=colors.HexColor('#999999'),
                           borderWidth=2, borderPadding=15,
                           leading=18, leftIndent=10, rightIndent=10)

normal_style = ParagraphStyle('Normal', parent=styles['Normal'],
                             fontSize=14, spaceAfter=8, leading=20)

content = []
# Para cada línea del markdown:
# - Headings (# ## ###) → Paragraph con estilo apropiado
# - Bloques de código (```) → Preformatted con code_style
# - Listas (- *) → Paragraph con bullet
# - Texto normal → Paragraph con normal_style

doc.build(content)
```

## Reglas de tamaño de fuente

| Elemento | Mínimo | Preferido |
|----------|--------|-----------|
| Título (H1) | 24px | 28px |
| Subtítulo (H2) | 18px | 20px |
| H3 | 14px | 16px |
| Párrafo | 12px | 14px |
| Código/Prompts | 14px | 16px |
| Tablas | 12px | 14px |

**NUNCA** usar fontSize < 12 para ningún contenido. Los usuarios rechazan PDFs con código pequeño inmediatamente.
