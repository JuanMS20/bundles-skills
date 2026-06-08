---
name: ffmpeg-video-production
description: "Complete FFmpeg video production: multi-segment assembly, format normalization, transitions, mixed assets (photos, audio, video), vertical video treatment, photo slideshows, concat pitfalls, and timestamp repair. Use when editing, merging, or assembling video with FFmpeg — covers the full pipeline from inventory to delivery."
tags: [ffmpeg, video, editing, multimedia, production]
triggers:
  - "editar video con ffmpeg"
  - "ensamblar clips en video final"
  - "unir videos en uno solo"
  - "producción de video documental"
  - "concatenar segments de video"
  - "mezclar fotos y video con audio"
  - "vertical a horizontal video"
  - "acelerar video ffmpeg"
  - "speed up video ffmpeg"
  - "atempo setpts speed change"
  - "drawtext caracteres especiales"
---

# FFmpeg Video Production

Producción de video completo usando FFmpeg CLI. Ensamblaje de assets mixtos
(fotos, clips de video, archivos de audio) en un video final unificado.

## Flujo de Trabajo

### Fase 1: Inventario
1. Listar TODOS los archivos multimedia (video, audio, imágenes)
2. Obtener specs de cada archivo con `ffprobe`:
   - Duración, resolución, codec, fps, canales de audio
3. Clasificar por tipo: video landscape, video vertical, audio-only, imágenes
4. Mapear cada archivo al segmento del guion/script correspondiente
5. Calcular duración total estimada — reportar al usuario

### Fase 2: Normalización
- **Target universal**: 1920x1080, 30fps, H.264, AAC audio
- **Fotos**: `scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080`
- **Video landscape** (más ancho que alto): escalar para caber en 1920x1080
- **Video vertical** (más alto que ancho): ver técnica de fondo borroso abajo

### Fase 3: Procesamiento de Assets
- Crear tarjetas de título/texto con `color` + `drawtext`
- Crear dividers de sección (fondo sólido + texto con fade)
- Agregar efecto Ken Burns a fotos estáticas (zoompan)
- Procesar videos verticales con fondo borroso

### Fase 4: Ensamblaje
- Generar archivo de lista para concat demuxer
- **CRÍTICO**: TODOS los segmentos deben tener pista de audio (ver pitfall)
- Concatenar con `-c:v libx264 -c:a aac`
- Verificar output con `ffprobe`: duración, streams, resolución

## Pitfalls Críticos

### ⚠️ setpts + atempo: dirección INVERTIDA

**Problema**: `setpts=PTS/1.25` + `atempo=0.8` hace el video más LENTO, no más rápido.
Es lo contrario de lo intuitivo.

**Solución verificada**: Para acelerar 1.25x:
- Video: `setpts=0.8*PTS` (0.8 = 1/1.25)
- Audio: `atempo=1.25`

```bash
ffmpeg -i input.mp4 -filter_complex \
  "[0:v]setpts=0.8*PTS[v];[0:a]atempo=1.25[a]" \
  -map "[v]" -map "[a]" output.mp4
```

### ⚠️ setpts en filter_complex causa pantalla gris al buscar

**Problema**: Aplicar `setpts` dentro de un filter_complex con blur/overlay genera
timestamps rotos. Al adelantar/retroceder en el reproductor, la pantalla se pone gris.

**Solución**: Separar en DOS PASES:
1. Aplicar filtros visuales (blur, overlay, etc.) SIN setpts
2. Acelerar el resultado con setpts simple en un segundo ffmpeg

```bash
# Paso 1: blur a velocidad original
ffmpeg -y -i input.mp4 -filter_complex \
  "[0:v]split=2[bg][fg];[bg]scale=1920:1080:...,gblur=sigma=40[b]; \
   [fg]scale=1920:1080:...[f];[b][f]overlay=...,format=yuv420p[v]" \
  -map "[v]" -map 0:a? output_blur.mp4

# Paso 2: acelerar limpiamente
ffmpeg -y -i output_blur.mp4 \
  -vf "setpts=0.8*PTS" -af "atempo=1.25" output_fast.mp4
```

### ⚠️ Keyframes inconsistentes en concat demuxer

**Problema**: Segmentos concatenados sin keyframes regulares causan pantalla gris al buscar.

**Solución**: En la concatenación final, forzar keyframes cada 2 segundos:
```bash
ffmpeg -f concat -safe 0 -i list.txt \
  -g 60 -sc_threshold 0 \
  -force_key_frames "expr:gte(t,n_forced*2)" \
  output.mp4
```

### ⚠️ drawtext con caracteres especiales falla en Windows

Tildes, dos puntos, apóstrofes en textos de drawtext causan errores silentes.
Usar texto sin acentos: "Referencias Bibliograficas" en vez de "Referencias Bibliográficas".

### ⚠️ Frame rate INCONSISTENTE causa NAL corruption (pantalla gris)

**Problema**: Segmentos con diferentes frame rates (WhatsApp=29.92fps, lavfi=25fps,
otros=29.75fps) concatenados causan "Invalid NAL unit size" y "missing picture in
access unit" — errores de corrupción a nivel de codec H.264. El video se reproduce
pero al adelantar/retroceder la pantalla se pone gris y se pega.

**Diagnóstico**:
```bash
ffprobe -v quiet -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 segmento.mp4
```
Si los segmentos tienen fps diferentes (359/12, 119/4, 25/1, etc.) → problema.

**Solución**: Forzar 30fps CFR en TODOS los segmentos Y en el concat final:
```bash
VENC="-c:v libx264 -preset fast -crf 20 -profile:v high -level 4.0 -pix_fmt yuv420p -r 30 -g 60 -sc_threshold 0 -vsync cfr"
```

Agrega `-r 30 -vsync cfr` a CADA ffmpeg que genere un segmento. Sin esto, el
concat demuxer produce archivos corruptos aunque todos los segmentos "parezcan" 30fps.

### ⚠️ filter_complex concat > concat demuxer (cuando hay problemas)

**Problema**: El concat demuxer (`-f concat -safe 0 -i list.txt`) falla silenciosamente
cuando los segmentos tienen orígenes diferentes (WhatsApp, lavfi, fotos). Produce
NAL corruption, timestamps rotos, o audio desincronizado.

**Solución**: Usar `filter_complex concat` en su lugar. Es MÁS confiable porque
procesa cada input independientemente y normaliza timestamps:

```bash
# Con N segmentos, cada uno con video+audio:
ffmpeg -y -i seg1.mp4 -i seg2.mp4 ... -i segN.mp4 \
  -filter_complex "[0:v][0:a][1:v][1:a]...[N-1:v][N-1:a]concat=n=N:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset fast -crf 20 -r 30 -vsync cfr -g 60 \
  -force_key_frames "expr:gte(t,n_forced*2)" \
  -c:a aac -ar 44100 -ac 2 -b:a 128k \
  -movflags +faststart output.mp4
```

**Cuándo usar cada uno**:
| Método | Cuándo | Velocidad |
|--------|--------|-----------|
| concat demuxer | Segmentos del mismo source/mismo fps/encoding idéntico | Rápido (stream copy) |
| filter_complex concat | Segmentos de orígenes mixtos, diferentes fps, o cuando el demuxer falla | Lento (re-encode) |

**Regla**: Si el concat demuxer produce errores NAL, pantalla gris, o audio roto →
cambiar a filter_complex concat sin dudar.

### ⚠️ -preset ultrafast produce NAL corruption en concat final

**Problema**: Usar `-preset ultrafast` en la concatenación final produce
"Invalid NAL unit size" y errores de decode. El preset ultrafast genera
un bitstream H.264 menos compliant que confunde a los decodificadores
durante seek.

**Solución**: NUNCA usar `ultrafast` para el output final. Mínimo `-preset fast`.

| Preset | ¿Seguro para output final? |
|--------|---------------------------|
| ultrafast | NO — produce NAL corruption |
| fast | SÍ |
| medium | SÍ (más lento) |
| slow | SÍ (máxima calidad) |

### ⚠️ Concat demuxer silencia el audio (SILENT FAILURE)

**Problema**: Si ALGÚN segmento en la lista de concat no tiene pista de audio,
el concat demuxer descarta el audio de TODOS los segmentos. No produce error —
solo genera un video sin audio.

**Causa raíz**: El concat demuxer exige streams idénticos en todos los segmentos.
Si un segmento tiene 2 streams (video+audio) y otro tiene solo 1 (video),
usa el stream count del primer segmento y omite audio del resto.

**Solución**: Agregar pista de audio silencioso a todos los segmentos sin audio
( tarjetas de título, dividers, imágenes estáticas ):

```bash
ffmpeg -y -i segmento_sin_audio.mp4 \
  -f lavfi -i "anullsrc=r=44100:cl=stereo" \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 128k \
  -shortest segmento_con_audio_silencioso.mp4
```

**Detección**: Si `ffprobe` del output final muestra solo 1 stream (video),
este pitfall se activó. Re-verify después de cada concat.

**Referencia**: Ver `references/concat-audio-pitfall.md` para detalles.
**Referencia completa**: Ver `references/consistent-concat-pattern.md` para el patrón de build script con keyframes consistentes.
**Referencia**: Ver `references/frame-rate-nal-corruption.md` para diagnóstico y fix de fps inconsistente → NAL corruption.

### ⚠️ Video vertical en proyecto horizontal

**Técnica profesional — Fondo Borroso**:

```bash
ffmpeg -y -i vertical.mp4 -filter_complex \
  "[0:v]split=2[bg][fg]; \
   [bg]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,\
       gblur=sigma=40,eq=brightness=-0.1[bgblur]; \
   [fg]scale=1920:1080:force_original_aspect_ratio=decrease[fgscale]; \
   [bgblur][fgscale]overlay=(W-w)/2:(H-h)/2,format=yuv420p[out]" \
  -map "[out]" -map 0:a? -c:v libx264 -c:a aac output.mp4
```

Qué hace:
1. `split` → duplica el stream de video
2. Background: escala para llenar 1920x1080, recorta excedente, aplica blur oscuro
3. Foreground: escala para caber dentro de 1920x1080 (sin recortar)
4. Overlay: centra el foreground sobre el background borroso

**Alternativas** (menos profesionales):
- Pillarbox (barras negras): simple pero feo
- Recortar top/bottom: pierde contenido
- Stretch: distorsiona

### ⚠️ Ken Burns en fotos estáticas

```bash
ffmpeg -loop 1 -i foto.jpg -vf \
  "zoompan=z='min(zoom+0.00067,1.2)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':\
   d=150:s=1920x1080:fps=30" \
  -t 5 -c:v libx264 -pix_fmt yuv420p output.mp4
```

- `d=150` = 150 frames = 5 segundos a 30fps
- Zoom de 1.0 a 1.2 (20% de aumento total)
- El `x`/`y` mantiene el zoom centrado

### ⚠️ Speed changes (atempo + setpts) — COUNTERINTUITIVE

**Problema**: `atempo=0.8` y `setpts=PTS/1.25` hacen lo OPUESTO de lo que parece.

| Comando | Efecto real | Intuición errónea |
|---------|-------------|-------------------|
| `atempo=0.8` | **MÁS LENTO** (0.8x speed) | "0.8 = más rápido" ✗ |
| `atempo=1.25` | **MÁS RÁPIDO** (1.25x speed) | — |
| `setpts=PTS/1.25` | **MÁS LENTO** (timestamps se expanden) | "dividir = más rápido" ✗ |
| `setpts=0.8*PTS` | **MÁS RÁPIDO** (timestamps se comprimen) | — |

**Regla**: Para velocidad Nx, usar `atempo=N` y `setpts=(1/N)*PTS`.

**Ejemplo correcto para 1.25x speed** (video + audio):
```bash
ffmpeg -y -i input.mp4 -filter_complex \
  "[0:v]scale=1920:1080:...,setpts=0.8*PTS,fade=...,format=yuv420p[v]; \
   [0:a]atempo=1.25[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -c:a aac output.mp4
```

**Pitfall adicional**: Usar `-vf` + `-af` separados para speed changes es menos fiable que `-filter_complex` con streams nombrados. Cuando combines speed con otros filtros (scale, pad, blur, fade), SIEMPRE usar `-filter_complex`.

**Posición de setpts en la cadena**: En filter_complex con overlay (video vertical con fondo borroso), poner `setpts` DESPUÉS del overlay pero ANTES del fade:
```
[bgblur][fgscale]overlay=...,setpts=0.8*PTS,fade=...,format=yuv420p[out]
```

### ⚠️ drawtext con caracteres especiales en Windows

**Problema**: Caracteres acentuados (é, á, ú, ñ) y dos puntos (:) en texto de drawtext causan fallos silenciosos o errores de parsing en FFmpeg en Windows.

**Solución**: Eliminar acentos y evitar dos puntos en el texto visible. Para bibliografías APA, reestructurar:
```
# MALO: "Alvarado Arias, M. (2007). José Martí y Paulo Freire:"
# BIENO: "Alvarado Arias, M. (2007). Jose Marti y Paulo Freire"
```

Si se necesitan acentos, usar un archivo de texto externo con `textfile=` en vez de `text=` inline.

## Templates de Comandos

### Verificar archivo multimedia
```bash
ffprobe -v quiet -print_format json -show_format -show_streams "archivo.mp4"
```

### Normalizar video landscape a 1920x1080
```bash
ffmpeg -y -i input.mp4 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,\
       pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
  -c:v libx264 -crf 20 -r 30 -c:a aac -b:a 128k output.mp4
```

### Concat demuxer (con todos los segments con audio)
```bash
# Archivo concat_list.txt:
# file 'segment1.mp4'
# file 'segment2.mp4'
# ...

ffmpeg -y -f concat -safe 0 -i concat_list.txt \
  -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 128k output.mp4
```

### Tarjeta de título con fade
```bash
ffmpeg -y -f lavfi -i "color=c=0x1a1a2e:s=1920x1080:d=5:r=30" \
  -vf "drawtext=text='TITULO':fontsize=64:fontcolor=white:\
       x=(w-text_w)/2:y=(h-text_h)/2:\
       alpha='if(lt(t,1),t,if(gt(t,4),5-t,1))'" \
  -c:v libx264 -pix_fmt yuv420p output.mp4
```

### Speed change 1.25x (video + audio)
```bash
ffmpeg -y -i input.mp4 -filter_complex \
  "[0:v]setpts=0.8*PTS[v];[0:a]atempo=1.25[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  -c:a aac -ar 44100 -ac 2 -b:a 128k output.mp4
```

### Speed change + normalization (landscape video at 1.25x)
```bash
ffmpeg -y -i input.mp4 -filter_complex \
  "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,\
   pad=1920:1080:(ow-iw)/2:(oh-ih)/2,\
   setpts=0.8*PTS,fade=t=in:st=0:d=0.5,fade=t=out:st=23:d=0.5,\
   format=yuv420p[v];\
   [0:a]atempo=1.25[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  -c:a aac -ar 44100 -ac 2 -b:a 128k output.mp4
```

## Repairing Corrupt Timestamps

If Windows gives error `0x80070323` when opening the MP4, timestamps are corrupt from the concat. Re-encode from individual sources (not from the corrupt file).

## Comprehensive Pitfalls Table

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Concat demuxer without `duration` | Segment plays ~75% longer than expected (duplicates last file) | Don't use `duration` directives; let the demuxer read real duration |
| `-c copy` with mixed H.264 | Corrupt NAL units, error 0x80070323 | Re-encode with `-preset fast` (never ultrafast for final) |
| Segments without audio | Audio disappears in ALL segments | Add `anullsrc` to silent segments |
| `zoompan` on photos | Grey/black frames | Use `loop + scale + crop` static |
| `fade st` with expressions | `Unable to parse option value` | Pre-calculate duration, pass literal |
| `atempo=0.8` for speed-up | Audio plays SLOWER | Use `atempo=1.25` for 1.25x speed |
| `setpts=PTS/1.25` for speed-up | Video plays SLOWER | Use `setpts=0.8*PTS` for 1.25x speed |
| `-vf` + `-af` with speed filters | Inconsistent timing, one stream not sped up | Use `-filter_complex` with named streams |
| drawtext accented chars on Windows | Silent failure or parse error | Strip accents, avoid colons |
| MSYS paths in Python `open()` | `FileNotFoundError` | Use `C:\Users\...` for Python, `/c/Users/...` for FFmpeg/shell |
| `execute_code` without ffmpeg in PATH | `exit_code 127` | Use `terminal()` directly for FFmpeg |
| Inconsistent fps across segments | NAL corruption, gray screen on seek | Force `-r 30 -vsync cfr` on ALL segments + final concat |
| concat demuxer with mixed-origin segments | NAL errors, timestamp corruption | Switch to `filter_complex concat` |
| `-preset ultrafast` on final output | Invalid NAL units, decode errors | Use minimum `-preset fast` for final concat |
| No seek test in verification | Undetected gray-screen-on-seek bug | Run `ffmpeg -v error -ss N -i out.mp4 -t 3 -f null -` at 3+ points |

## Recommended Workflow

1. **Inventory**: List all sources with `ffprobe` (duration, resolution, codec, **fps**)
2. **Mapping**: Confirm with user which file → which segment
3. **Pre-process**: Normalize ALL segments to uniform format (**force `-r 30 -vsync cfr`**)
4. **Verify**: Confirm V+A in each individual segment + correct fps
5. **Concatenate**: Prefer `filter_complex concat` for mixed-origin segments
6. **Validate**: `ffprobe` + `ffmpeg -v error` + **seek test at 3+ points**
7. **Deliver**: Verify it opens in Windows and seeking works without gray screen

### ⚠️ Pantalla gris al adelantar (keyframes inconsistentes)

**Problema**: Al concatenar segmentos con encoding diferente, el reproductor no puede
buscar (seek) correctamente → pantalla gris al adelantar o retroceder.

**Causa raíz**: Cada segmento tiene keyframes en posiciones diferentes. El reproductor
necesita un keyframe para iniciar decodificación en cualquier punto. Sin keyframes
regulares, seek = pantalla gris.

**Causa secundaria**: Usar `-c:v copy` en algunos segmentos preserva el patrón de
keyframes del archivo fuente, que difiere entre segmentos.

**Solución triple**:

1. **Encoding consistente en TODOS los segmentos** (sin `-c:v copy`):
```bash
VENC="-c:v libx264 -preset fast -crf 20 -profile:v high -level 4.0 -pix_fmt yuv420p -g 60 -sc_threshold 0"
```

2. **Re-encode en la concatenación final** con keyframes forzados:
```bash
ffmpeg -y -f concat -safe 0 -i list.txt \
  -c:v libx264 -preset fast -crf 20 -profile:v high -level 4.0 \
  -pix_fmt yuv420p -g 60 -sc_threshold 0 \
  -force_key_frames "expr:gte(t,n_forced*2)" \
  -c:a aac -ar 44100 -ac 2 -b:a 128k \
  -movflags +faststart output.mp4
```

3. **Verificar keyframes** en el output:
```bash
ffprobe -v quiet -select_streams v:0 -show_entries frame=pts_time,pict_type -of csv=p=0 output.mp4 | grep ",I" | head -20
```
Gap promedio debe ser ~2s. Si >4s, hay problema de seek.

**Parámetros clave**:
- `-g 60`: keyframe cada 60 frames (2s a 30fps)
- `-sc_threshold 0`: desactiva detección de escenas (que inserta keyframes extra)
- `-force_key_frames "expr:gte(t,n_forced*2)"`: fuerza keyframe cada 2s exactos
- `-profile:v high -level 4.0`: asegura compatibilidad con reproductores

### ⚠️ Single-pass vs two-pass encoding

**Anti-patrón**: Hacer `-c:v copy` para video + luego re-encode "para consistencia".
Es el doble de lento y no aporta calidad.

**Correcto**: Usar `filter_complex` para procesar video + audio en una sola pasada:
```bash
ffmpeg -y -i slideshow.mp4 -i audio.mp3 \
  -filter_complex "[1:a]atempo=1.25,afade=...[a]" \
  -map 0:v -map "[a]" \
  -c:v libx264 -preset fast -crf 20 ... \
  -c:a aac ... output.mp4
```

Para fotos como slideshow con audio narrado, usar inputs múltiples + concat en filter:
```bash
ffmpeg -y -loop 1 -t 6.3 -i photo1.png \
       -loop 1 -t 6.3 -i photo2.png \
       -i narration.mp3 \
  -filter_complex \
    "[0:v]scale=1920:1080:...:crop=...[v0]; \
     [1:v]scale=1920:1080:...:crop=...[v1]; \
     [v0][v1]concat=n=2:v=1:a=0[vcat]; \
     [2:a]atempo=1.25,afade=...[a]; \
     [vcat]format=yuv420p[vout]" \
  -map "[vout]" -map "[a]" -shortest \
  -c:v libx264 -preset fast ... output.mp4
```

### ⚠️ Preset speed tradeoff

| Preset | Velocidad | Calidad (CRF 20) | Uso recomendado |
|--------|-----------|-------------------|-----------------|
| ultrafast | 5-10x realtime | Baja | Debug/testing |
| fast | 2-4x realtime | Buena | Producción general |
| medium | 1-2x realtime | Muy buena | Solo si el tiempo no importa |
| slow | 0.3-0.5x realtime | Excelente | Entrega final premium |

**Regla**: Para workflows iterativos (build → verify → fix), usar `fast`. Solo usar
`medium` o `slow` en la entrega final si el cliente pide máxima calidad.

### ⚠️ Unicode filenames en Windows + Python

**Problema**: Archivos con acentos (Andrés, educación) causan `FileNotFoundError`
cuando se escriben como ASCII en Python.

**Solución**: Usar escape Unicode en strings Python:
```python
# MALO: "Video 1 Andrés_.mp4"
# BIENO: "Video 1 Andr\u00e9s_.mp4"
```

O usar raw strings con el nombre exacto del filesystem. Verificar con `ls` antes de construir.

## Checklist de Verificación Final

- [ ] `ffprobe` muestra 2 streams (video + audio)
- [ ] Resolución: 1920x1080
- [ ] FPS: 30/1 (verificar con `r_frame_rate`)
- [ ] Duración total coincide con la suma de segmentos
- [ ] Audio presente y sincronizado (diff < 0.5s)
- [ ] Sin frames corruptos al inicio/fin
- [ ] `ffmpeg -v error -i output.mp4 -f null -` = 0 errores
- [ ] Keyframes cada ~2s (verificar con ffprobe)
- [ ] `-movflags +faststart` para streaming/web
- [ ] **SEEK TEST**: `ffmpeg -v error -ss 30 -i output.mp4 -t 3 -f null -` = 0 errores
  (repetir en 3+ puntos: inicio, medio, final). Si falla → NAL corruption.

```bash
# Seek test automatizado (probar en múltiples puntos)
for t in 30 120 240 360; do
  ffmpeg -v error -ss $t -i output.mp4 -t 3 -f null - 2>&1 && echo "OK $t" || echo "FAIL $t"
done
```

## Orden de Concatenación Típico (Documental)

1. Tarjeta de título
2. Prólogos de audio (sobre fotos/B-roll)
3. Dividers de sección
4. Clips de video por segmento narrativo
5. Cierre (imagen + texto final)
