#!/usr/bin/env python3
"""
Migra componentes React de setError/setMessage a toast notifications.

Uso: python migrate-to-toast.py <archivo.tsx>

Busca y reemplaza:
- import { useState } from 'react' → + import { useToast } from '@/context/ToastContext'
- const [error, setError] = useState<string | null>(null) → const { showToast } = useToast()
- setError(null) → (eliminado)
- setError(msg) → showToast(msg, 'error')
- {error && (<div>...</div>)} → (eliminado)
- setMessage patterns → showToast equivalente

Ejecutar desde la raíz del proyecto.
"""
import sys
import re

def migrate_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # 1. Add toast import if not present
    if 'useToast' not in content:
        content = content.replace(
            "import { useEffect, useState } from 'react'",
            "import { useEffect, useState } from 'react'\nimport { useToast } from '@/context/ToastContext'"
        )
    
    # 2. Replace error state with toast hook
    content = content.replace(
        "const [error, setError] = useState<string | null>(null)",
        "const { showToast } = useToast()"
    )
    
    # 3. Replace message state with toast hook (for Credenciales pattern)
    content = content.replace(
        "const [message, setMessage] = useState<string | null>(null)",
        "const { showToast } = useToast()"
    )
    
    # 4. Remove setError(null) calls
    content = re.sub(r'\s*setError\(null\)\n', '\n', content)
    content = re.sub(r'\s*setMessage\(null\)\n', '\n', content)
    
    # 5. Replace setError(msg) with showToast
    content = re.sub(
        r"setError\(([^)]+)\)",
        r"showToast(\1, 'error')",
        content
    )
    
    # 6. Replace setMessage for success
    content = content.replace(
        "setMessage(`Contraseña actualizada para ${resetUser.nombre}`)",
        "showToast(`Contraseña actualizada para ${resetUser.nombre}`, 'success')"
    )
    
    # 7. Replace setMessage for errors
    content = re.sub(
        r"setMessage\(([^)]+)\)",
        r"showToast(\1, 'error')",
        content
    )
    
    # 8. Remove error/message display blocks (simple patterns)
    content = re.sub(
        r'\{error && \(\s*<div[^>]*>.*?</div>\s*\)\}',
        '',
        content,
        flags=re.DOTALL
    )
    content = re.sub(
        r'\{message && \(\s*<div[^>]*>.*?</div>\s*\)\}',
        '',
        content,
        flags=re.DOTALL
    )
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Migrated: {filepath}")
    else:
        print(f"⏭️  No changes: {filepath}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python migrate-to-toast.py <archivo1.tsx> [archivo2.tsx ...]")
        sys.exit(1)
    
    for filepath in sys.argv[1:]:
        migrate_file(filepath)
