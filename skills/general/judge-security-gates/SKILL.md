---
name: judge-security-gates
description: "Pentest multi-plataforma. Web: XSS, SQLi, CSRF, CSP. Móvil: APK tampering, insecure storage. Juegos: economy manipulation, client trust. CLI: injection, path traversal. Deps vulnerables. La IA genera código vulnerable por defecto. Use when: security check, 'es seguro?', antes de exponer app, juzgar seguridad."
---

# JUDGE SECURITY GATES — La app es un colador?

## Principio: La IA no sabe de seguridad. Punto.

La IA genera código que "funciona". No código que "resiste ataques".
Tu trabajo es pensar como atacante y encontrar los agujeros
antes de que lo haga alguien malintencionado.

## FASE 0 — Detectar plataforma

- **Web**: HTML/JS frontend, servidor HTTP, browser-accessible
- **Móvil**: APK/IPA, React Native, Flutter, native SDK
- **Juego**: game client + servidor (multiplayer), o single-player
- **CLI**: tool de terminal, input de args/stdin
- **Desktop**: Electron, Tauri, native app con acceso a OS
- **Backend/API**: servidor HTTP, microservicio, Edge Function

## Checklist Universal (TODAS las plataformas)

### 1. Input Validation
- [ ] TODOS los inputs de usuario están validados?
- [ ] Hay sanitización antes de guardar en DB/procesar?
- [ ] Hay rate limiting en endpoints/funciones que reciben input?
- [ ] Los file uploads validan tipo Y tamaño?

### 2. Authentication & Authorization
- [ ] Las passwords están hasheadas (bcrypt/argon2)?
- [ ] Hay expiración de tokens/sesiones?
- [ ] Los endpoints/funciones protegidos verifican auth?
- [ ] Hay verificación de ownership? (no puedo ver datos de otro user)
- [ ] Hay brute force protection?

### 3. Data Exposure
- [ ] No hay PII en logs?
- [ ] No hay API keys/secretos en código cliente?
- [ ] No hay `.env` en el repo público?
- [ ] Los errores no exponen stack traces en producción?
- [ ] Hay HTTPS/TLS forzado en comunicaciones de red?

### 4. Dependencies
- [ ] `npm audit` / `pip-audit` / `cargo audit` ejecutado?
- [ ] Hay vulnerabilidades CRÍTICAS en dependencias?
- [ ] Las dependencias están actualizadas?

## Checklist Web

- [ ] Hay sanitización antes de renderizar HTML? (XSS)
- [ ] No hay `innerHTML` con input de usuario?
- [ ] No hay concatenación de strings en SQL queries? (SQLi)
- [ ] No hay `eval()` con input de usuario?
- [ ] Hay Content Security Policy (CSP)?
- [ ] Hay CSRF tokens en formularios?
- [ ] CORS no es `*` en producción?
- [ ] Hay X-Frame-Options / clickjacking protection?
- [ ] Los file uploads no ejecutan el archivo subido?

## Checklist Móvil

- [ ] Storage no guarda tokens/passwords en texto plano? (Keychain/Keystore)
- [ ] Certificate pinning en comunicación con backend?
- [ ] APK/IPA tiene ofuscación? (ProGuard/R8)
- [ ] Biometrics usa crypto-backed auth, no boolean flag?
- [ ] Deep links / intents no permiten bypass de auth?
- [ ] No hay API keys hardcodeadas en el binario?

## Checklist Juegos

- [ ] El servidor valida TODAS las transacciones de economía?
- [ ] Saves no son editables trivialmente? (checksum, server-side, encrypted)
- [ ] No hay lógica crítica de gameplay solo en el cliente?
- [ ] Anti-cheat básico si es multiplayer?
- [ ] No hay items/datos duplicables (duping)?

## Checklist CLI

- [ ] No hay command injection? (`exec`/`spawn` con input sin sanitizar)
- [ ] Path traversal prevenido? (no concatenar paths de usuario)
- [ ] Variables de entorno no se loggean?
- [ ] Permisos de archivos son restrictivos? (no 777)

## Checklist Desktop

- [ ] IPC no permite ejecución arbitraria de código?
- [ ] No carga DLLs/librerías de directorios sin permisos?
- [ ] Protocol handlers (URL schemes) sanitizados?
- [ ] Auto-updater verifica firma del paquete?

## Análisis de Código (patrones VULNERABLES por plataforma)

### Web
```javascript
// ❌ SQL Injection
const query = `SELECT * FROM users WHERE id = ${userId}`;
// ✅
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);

// ❌ XSS
element.innerHTML = userInput;
// ✅
element.textContent = userInput;

// ❌ Credenciales hardcodeadas
const API_KEY = 'sk-liv...cdef';
// ✅
const API_KEY = process.env.API_KEY;
```

### Móvil
```javascript
// ❌ Token en AsyncStorage/plain SharedPreferences
await AsyncStorage.setItem('token', jwtToken);
// ✅ Token en Secure Storage
import * as SecureStore from 'expo-secure-store';
await SecureStore.setItemAsync('token', jwtToken);
```

### Juegos
```javascript
// ❌ Cliente decide cuánto oro ganó
player.gold += earnedAmount; // enviado al servidor tal cual
// ✅ Servidor valida y calcula
const reward = server.calculateReward(questId, playerId);
```

### CLI
```javascript
// ❌ Command injection
exec(`cat ${userInput}`);
// ✅ Sanitizado o sin shell
execFile('cat', [sanitizedFile]);
```

## Formato de Veredicto

```
## VEREDICTO JUDGE SECURITY GATES

### Plataforma: [Web / Móvil / Juego / CLI / Desktop]

### Estado: [SEGURO / VULNERABLE / PELIGROSO]

### Severidad:
| Tipo | Cantidad | Severidad |
|------|----------|-----------|
| Crítica (RCE, SQLi, Auth bypass, Economy duping) | X | CRÍTICA |
| Alta (XSS, IDOR, CSRF, Insecure storage) | X | ALTA |
| Media (Info disclosure, Missing headers) | X | MEDIA |
| Baja (Best practices) | X | BAJA |

### Vulnerabilidades Encontradas:
1. [archivo:linea] — [tipo] — [explotación] — severidad

### Dependencias Vulnerables:
| Paquete | Versión | CVE | Severidad |

### Recomendaciones:
1. [acción concreta con prioridad]

### Score de Seguridad: [0-100]/100
```

## Reglas de Oro
- **NUNCA** apruebes si hay SQL Injection o command injection
- **NUNCA** apruebes si hay XSS reflejado o stored (web)
- **NUNCA** apruebes si hay credenciales hardcodeadas
- **NUNCA** apruebes si hay vulnerabilities CRÍTICAS en dependencias
- **NUNCA** apruebes si hay duping/economy exploit sin validación server-side (juegos)
- **NUNCA** apruebes si hay token storage en texto plano (móvil)
- Si hay >0 CRÍTICAS -> PELIGROSO. Fix inmediato.
