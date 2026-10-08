# Arquitectura AWS — Proceso de datos ITT (para futuras implementaciones)

Este documento consolida la **arquitectura objetivo** del flujo de datos del ITT en AWS:
el pipeline medallón (Bronze/Silver/Gold), la capa API como fuente única de verdad, el
análisis de viabilidad y las decisiones pragmáticas para la escala real del proyecto.

> **Estado: propuesta de diseño, NO implementada.** Sirve de guía para cuando se decida
> construir el pipeline. Toda ejecución en AWS requiere **autorización explícita del
> usuario** (ver `docs/07_conexion_aws_calitrack.md`). Documentos relacionados:
> - `docs/07_conexion_aws_calitrack.md` — conexión, perfiles, nomenclatura de recursos.
> - `docs/08_estructura_aws_proceso_data_itt.md` — hoja de ruta medallón (versión pública en docs).

---

## 1. Diagrama de arquitectura (objetivo)

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1 · FUENTES: Seguridad(DATIC) · Movilidad(SIMUR) · Economía(CámaraCo) │
│    · Educación(SIMAT) · Ambiental(NDVI Sentinel-2 / censo arbóreo)    │
└───────────────────────────────┬──────────────────────────────────────┘
                 ingesta con fecha de corte + linaje
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 2 · BRONZE / RAW   (s3 raw/)   crudo, inmutable, no se modifica        │
└───────────────────────────────┬──────────────────────────────────────┘
         Compuerta de calidad (CRS, fechas, geometrías, nulos)
              ├── NO pasa → cuarentena (raw/_rejected/)
              └── sí pasa ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 3 · SILVER GLOBAL  (s3 curated/)  limpio, tipado, EPSG:4326, GeoParquet│
└───────────────────────────────┬──────────────────────────────────────┘
                 Filtro espacial por polígono (geopandas sjoin)
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 4 · SILVER POR ZONA   Intervención (Cdd Paraíso·Roosevelt·Obrero·AvCali)│
│                       + Espejo/control (sin obra)                      │
└───────────────────────────────┬──────────────────────────────────────┘
                 Scores por dimensión + ITT ponderado
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 5 · GOLD / DATA MARTS  (s3 analytics/)                                 │
│     ├── AGREGADOS publicables                                          │
│     └── DETALLE reservado (PII)                                        │
└───────────────────────────────┬──────────────────────────────────────┘
                       FUENTE ÚNICA DE VERDAD
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 6 · API ITT   (API Gateway + Lambda · token/API key · control acceso) │
└───────────────────────────────┬──────────────────────────────────────┘
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│ 7 · CONSUMIDORES (intercambiables):                                    │
│     Dashboards BI · Mapas/GIS · Sitio web/App · Terceros · ML          │
│     (los agregados → cualquiera; el detalle PII → endpoint restringido)│
└──────────────────────────────────────────────────────────────────────┘

TRANSVERSALES:
  · Catálogo de datos (esquema + linaje) gobierna Silver y Gold.
  · Orquestación (evento S3 / cron / manual) dispara cada etapa.
  · Resiliencia: si NO se publican dashboards/mapas, la API sigue sirviendo el dato.
```

---

## 2. Capas medallón y su correspondencia con el datalake real

| Capa | Rol | Zona S3 actual | Formato propuesto |
|---|---|---|---|
| Bronze / Raw | Crudo, inmutable, con linaje | `raw/` (protegida) | original (geojson/xlsx/tif) |
| Silver Global | Limpio, tipado, CRS único | `curated/` | GeoParquet |
| Silver por Zona | Geo-fencing por polígono | `curated/<zona>/` | GeoParquet |
| Gold / Data Marts | Scores + ITT, listo para consumo | `analytics/` | Parquet / JSON |
| API | Capa de servicio sobre Gold | API Gateway + Lambda | JSON / GeoJSON |
| Sandbox | Pruebas | `pruebas/` | — |

Hoy los datos de Ciudad Paraíso viven en `pruebas/itt_Ciudad_Paraiso/` (dimensiones 1-6
+ Infraestructura). La hoja de ruta plantea promoverlos raw → curated → analytics.

---

## 3. Capa API — fuente única de verdad

**Motivación (requisito del usuario):** las zonas y sus dashboards/mapas deben poder
publicarse vía API, o sintetizarse en una API, **por si no se pueden publicar los
dashboards y mapas** (restricción institucional, caída de hosting, cambio de BI). La API
desacopla el dato de la presentación: cualquier consumidor es intercambiable y ninguno es
imprescindible.

**Patrón recomendado (para la escala del proyecto):** API Gateway + Lambda que lee los
archivos Gold de `analytics/` en S3 y los devuelve como JSON/GeoJSON. Sin base de datos.
Barato, simple, idempotente. (Patrón alternativo si crece: Athena/DynamoDB detrás.)

**Diseño de endpoints (borrador):**

```
GET /itt/zonas                      -> lista de zonas + último ITT
GET /itt/{zona}                     -> ITT + scores por dimensión (serie 2023-2026)
GET /itt/{zona}/dimensiones/{dim}   -> detalle de una dimensión (indicadores)
GET /itt/{zona}/mapa                -> GeoJSON SEGURO (ubicación + tipo, sin PII)
GET /itt/{zona}/trimestral          -> serie trimestral
GET /itt/comparativo                -> ITT de todas las zonas para comparar
```

**Privacidad en la API (misma regla del sitio público):**
- Los endpoints públicos sirven solo agregados / ubicación+tipo (sin dirección, fecha,
  sexo, edad, placas, etc.).
- El detalle con PII, si se expone, va en un **endpoint restringido** (token con más
  privilegios) o no se expone.

**Nombre sugerido del recurso:** `aca-prod-calitrack-itt-api` (patrón de nomenclatura del
protocolo), tag `Proyecto=CaliTrack`, región `us-east-1`, perfil `calitrack-aca`.

**Pendiente técnico cuando se construya:** CORS (permitir el dominio de GitHub Pages) y
manejo del token desde un sitio estático sin exponerlo.

---

## 4. Análisis de viabilidad (resumen)

**Veredicto:** la arquitectura medallón + API es correcta y viable. Riesgo principal:
**sobredimensionamiento** para la escala real del proyecto.

**Contexto de escala real:**
- Volumen pequeño: el datalake de Ciudad Paraíso pesa ~11 MB (MB, no TB).
- Baja frecuencia: datos trimestrales/anuales, no streaming.
- Equipo pequeño.

**Fortalezas del diseño:**
- Separación de capas correcta (trazabilidad, no recalcular todo).
- Partir por zona en Silver es acertado: cada zona tiene umbrales `ref_min/ref_max`,
  polígono y dimensiones distintas (p.ej. Ciudad Paraíso tiene Educación, Roosevelt no).
- Geo-fencing en Silver = el mismo `sjoin` que ya hacen los notebooks (continuidad).
- API desacopla dato de presentación (resiliencia de publicación).

**Debilidades a cubrir (no estaban en el diagrama original):**
- Orquestación (qué dispara cada etapa).
- Catálogo de datos / esquema (geometrías consistentes entre capas).
- Compuerta de validación de calidad entre Bronze y Silver.
- Gobernanza/privacidad: Gold debe separar publicable vs. reservado (PII).
- Zonas espejo/control para evaluación de impacto (no solo zonas de intervención).

---

## 5. Decisiones pragmáticas recomendadas (para esta escala)

NO implementar la versión "enterprise" (Glue + Step Functions pesados). Para MB de datos
trimestrales:

| Pieza | Recomendación pragmática |
|---|---|
| Orquestación | Lambda por etapa, disparada por evento S3 (subir a `raw/` dispara Silver) |
| Formato Silver/Gold | GeoParquet (comprime, lo lee geopandas y Athena) |
| Compuerta de calidad | Lambda de validación (reutiliza lógica de los notebooks: sjoin, parseo de fechas, CRS) |
| Consulta analítica | Athena sobre `analytics/` (sin montar bases de datos) |
| API | API Gateway + Lambda leyendo `analytics/` |

Esto cumple el espíritu medallón con la huella operativa de un equipo pequeño.

---

## 6. Checklist de implementación (cuando se autorice)

Antes de crear cualquier recurso (ver protocolo `docs/07`):
1. Autorización explícita del usuario para la creación concreta.
2. Perfil `calitrack-aca`, región `us-east-1`, sesión SSO activa.
3. Nombre `aca-prod-calitrack-...`, tag `Proyecto=CaliTrack`.
4. No tocar `raw/` ni zonas protegidas (`raw/blend_instantdb/`, `externo/`).
5. No crear/editar roles IAM; usar los existentes.
6. Salidas idempotentes por fecha: `curated/<fuente>/<YYYY-MM-DD>/`.
7. Verificar tras crear (`get`/`list` + tag).

Orden sugerido de construcción:
1. Promover datos actuales de `pruebas/` a `raw/` (con linaje).
2. Lambda de calidad Bronze→Silver (validación + GeoParquet + CRS único).
3. Lambda de geo-fencing Silver→Silver por zona.
4. Lambda de scores Silver→Gold (reusa la lógica del notebook 08).
5. API Gateway + Lambda sobre Gold (endpoints de la sección 3).
6. Conectar consumidores (el sitio Pages consume la API; BI/GIS/ML según necesidad).

---

## 7. Puntos abiertos / decisiones pendientes

- Orquestador definitivo (Lambda simple vs. Step Functions si crece).
- Formato final (GeoParquet confirmado como preferido).
- Estrategia de partición: Silver→zona→Gold (recomendada) vs. Gold consolidado→partir.
- Definir y cargar zonas espejo por cada zona de intervención.
- Modelo de autenticación de la API (API key vs. Cognito) y CORS para el sitio estático.
