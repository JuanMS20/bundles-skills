# OWASP Top 10 — Referencia 2025

Fuente: https://owasp.org/Top10/2025/ (verificado 2026-06-06)

## Lista 2025 (vigente)

| # | Categoría | Cambio desde 2021 |
|---|-----------|-------------------|
| A01 | Broken Access Control | Sin cambio (#1 en ambas) |
| A02 | Security Misconfiguration | Sin cambio |
| A03 | Software Supply Chain Failures | Renombrado (era "Vulnerable and Outdated Components"). Ahora incluye CI/CD, typosquatting, supply chain attacks |
| A04 | Cryptographic Failures | Sin cambio |
| A05 | Injection | Subió de #3 (2021) |
| A06 | Insecure Design | Bajó de #4 (2021) |
| A07 | Authentication Failures | Renombrado (era "Identification and Authentication Failures") |
| A08 | Software or Data Integrity Failures | Renombrado (era "...and Data..." → "...or Data...") |
| A09 | Security Logging and Alerting Failures | Renombrado (era "...Monitoring...") |
| A10 | Mishandling of Exceptional Conditions | NUEVO — reemplazó SSRF |

## SSRF en 2025
SSRF ya no es categoría propia. Se verifica bajo A01 (Broken Access Control) 
o A05 (Injection) según el vector. Seguir probando SSRF si la app hace 
server-side requests con input del usuario.

## A10 — Qué verificar (nueva categoría)
Mishandling of Exceptional Conditions cubre:
- Servicios externos que caen (timeout, connection refused)
- Out-of-memory, disk full
- Excepciones no capturadas que revelan stack traces
- Errores de DB que dejan transacciones inconsistentes
- Inputs inválidos que causan crashes no recuperables
- Timeouts del lado servidor no configurados

## Lección de verificación
En una sesión anterior, el agente encontró "OWASP Top 10 2025" en el archivo 
y lo "corrigió" a 2021 basándose en knowledge cutoff. Error: 2025 ES la versión 
correcta. El knowledge cutoff del modelo puede estar desactualizado respecto a 
estándares publicados después del entrenamiento.

REGLA: Si ves una referencia de versión/año que crees incorrecta → verificar en 
owasp.org ANTES de tocar. No "corregir" basándose en intuición del training data.
