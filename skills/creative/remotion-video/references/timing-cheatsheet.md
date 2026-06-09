# Timing Cheatsheet — Edición Profesional

## Curvas Bézier (copy-paste)

| Nombre | Curva | Uso |
|---|---|---|
| Crisp ease-out | `bezier(0.16, 1, 0.3, 1)` | Entradas de texto, logos, lower thirds |
| Smooth ease-in-out | `bezier(0.65, 0, 0.35, 1)` | Transiciones generales, crossfades |
| Snappy overshoot | `bezier(0.34, 1.56, 0.64, 1)` | Pop-ins TikTok/Reels, badges |
| Gentle ease-out | `bezier(0.25, 1, 0.5, 1)` | Fades de fondo, overlays sutiles |
| Power slide | `bezier(0.7, 0, 0.3, 1)` | Slides de escenas completas |
| Hard cut prep | Sin easing (linear) | Preparar frame exacto antes de corte seco |

## Configs Spring

| Tipo | Config | Uso |
|---|---|---|
| Bounce ligero | `{damping: 10, stiffness: 100}` | Pop-ins, notificaciones |
| Settle suave | `{damping: 20, stiffness: 80}` | Paneles, overlays |
| Pesado dramático | `{damping: 25, stiffness: 40}` | Títulos, reveals |
| Rápido tight | `{damping: 15, stiffness: 120}` | Stomps, impacts |

## Duraciones por Contexto (30fps)

| Elemento | Frames | Segundos |
|---|---|---|
| Logo reveal | 30-45 | 1.0-1.5s |
| Texto entrada | 20-30 | 0.7-1.0s |
| Texto salida | 15-20 | 0.5-0.7s |
| Transición fade | 12-20 | 0.4-0.7s |
| Transición slide/wipe | 15-25 | 0.5-0.8s |
| Lower third in | 20-30 | 0.7-1.0s |
| Lower third hold | 60-180+ | 2-6s+ |
| Lower third out | 15-20 | 0.5-0.7s |
| Hook/TikTok cut | 3-5 | 0.1-0.2s |
| Beat sync marker | 2-3 | ~0.08s |

## Ritmo de Edición por Plataforma

| Plataforma | Ritmo | Cortes por minuto | Notas |
|---|---|---|---|
| YouTube (tutorial) | Medio | 15-25 | Tiempo de respirar |
| YouTube Shorts | Rápido | 40-60 | 1-2s por clip |
| TikTok | Muy rápido | 60-100 | Sync con beat |
| Instagram Reels | Rápido | 50-70 | Visual first |
| Podcast/entrevista | Lento | 5-15 | Lissage natural |
