# Pipeline de Subtítulos

## Métodos de Input

### 1. SRT/VTT existente
Parsear archivo y generar array de subtítulos:
```ts
interface SubtitleCue {
  text: string;
  startFrame: number;
  endFrame: number;
  words?: WordCue[];  // para karaoke
}
```

### 2. Transcripción manual
Si no hay SRT, usar transcript con timestamps:
```
0:00-0:03 "Hola a todos"
0:03-0:06 "bienvenidos al canal"
```
Convertir a frames: `frame = seconds * fps`

### 3. Sin transcripción
Crear subtítulos key-moment (no word-by-word):
- Hook phrase completo
- Cada 5-10s una frase clave
- CTA al final

## Estilos por Plataforma

### YouTube Standard
```tsx
<span style={{
  background: "rgba(0,0,0,0.6)",
  color: "#fff",
  padding: "10px 20px",
  borderRadius: 4,
  fontSize: 36,
  fontWeight: 500,
}}>{text}</span>
```
Posición: bottom-center, 80px from bottom

### TikTok / Reels
```tsx
<span style={{
  color: "#fff",
  WebkitTextStroke: "2px #000",
  fontSize: 60,
  fontWeight: 900,
  textTransform: "uppercase",
}}>{text}</span>
```
Posición: bottom-center, 150px from bottom (espacio para UI nativa)
Animación: pop-in `spring()` o `scale(0.9→1)` + opacity

### Karaoke Word-by-Word
```tsx
// Cada palabra es un <span> con color condicional
words.map((word, i) => (
  <span key={i} style={{
    color: currentWordIndex > i ? "#ff0055" : "#fff",
    transition: "none",  // frame-driven
  }}>{word.text} </span>
))
```

## Sincronización

Usar `useCurrentFrame()` para determinar qué palabra está activa:
```tsx
const currentWordIndex = words.findIndex(
  (w) => frame >= w.startFrame && frame < w.endFrame
);
```

## Pipeline Completo

1. Obtener/transcribir audio
2. Generar/parsear SRT → array de cues
3. (Opcional) Split en palabras con timestamps estimados
4. Crear componente `<Subtitles>` con `<Sequence>` por cue
5. Aplicar estilo según plataforma
6. Overlay sobre video principal
