# Templates por Plataforma

## 1. YouTube Intro (5-10s)

Estructura:
```
0-1s   → Hook visual rápido (clip más intenso)
1-3s   → Logo/título animado con tagline
3-5s   → Transición a contenido
5-10s  → [Opcional] B-roll de setup/contexto
```

Spec técnico:
- 1920x1080, 30fps
- Música: 0.15-0.2 volumen
- Logo centrado o esquina

## 2. TikTok / Reel Hook (0-3s)

Estructura:
```
0-0.5s → Impact frame (texto grande + color)
0.5-3s → Hook verbal + visual sync
```

Spec técnico:
- 1080x1920, 30fps
- Texto mínimo 72px (legible en mobile)
- Colores saturados, alto contraste
- Subtítulos grandes con animación pop-in

## 3. Podcast Visualizer (ongoing)

Estructura:
```
Background: imagen/video estático
Overlay: waveform o bars animadas con audio
Lower third: episodio + invitado + topic
```

Spec técnico:
- 1920x1080 o 1:1 para clips
- Waveform sync con `<Audio>` volume analysis
- Lower third entra a los 3s, sale al final

## 4. Tutorial Screen Recording

Estructura:
```
0-3s   → Título del tutorial
3-5s   → ¿Qué vamos a lograr? (resultado final)
5-30s  → Paso 1 con callout
30-60s → Paso 2 con callout
...    → Steps con zoom y highlights
Final  → Outro + CTA (suscribir, comentar)
```

Spec técnico:
- 1920x1080, 30fps
- Cursor highlight (círculo amarillo)
- Click ripple animation
- Text callouts sync con cursor

## 5. Interview / Talking Head

Estructura:
```
0-2s   → Fade in desde negro
2-5s   → Lower third (nombre + rol)
5-...  → Entrevista con cortes tipo L/Jump
Final  → Fade out + info card
```

Spec técnico:
- 1920x1080, 30fps
- B-roll overlay para cubrir jump cuts
- Lower third gradient o barra limpia
- Color grading consistente entre takes

## Design Tokens Universales

| Elemento | Spec |
|---|---|
| Fuente | Sans-serif bold (Inter, Roboto, system-ui) |
| Títulos | 60-96px (vertical), 48-72px (horizontal) |
| Body / captions | 32-48px |
| Padding seguro | 60px de bordes (vertical: 120px bottom para captions) |
| Contraste | WCAG AA mínimo (4.5:1) |
