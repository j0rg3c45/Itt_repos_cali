# Estructura AWS — Proceso de la Data ITT

Hoja de ruta (propuesta, en definición) para el flujo de datos del Índice de
Transformación Territorial (ITT) sobre AWS, siguiendo una **arquitectura medallón**
(Bronze → Silver → Gold).

> Estado: **propuesta de arquitectura**, por ahora para contexto y discusión. No
> implementada aún. Toda ejecución en AWS requiere autorización explícita del usuario
> (ver `docs/07_conexion_aws_calitrack.md`).

## 1. Diagrama de flujo

```
            [ Fuentes / APIs / Archivos ITT ]
                          │
                          ▼
        ┌─────────────────────────────────┐
        │     BRONZE / RAW (Data Lake)    │  Datos crudos, sin transformar,
        └────────────────┬────────────────┘  con linaje y metadatos
                         │ Limpieza, tipado, estandarización de
                         │ coordenadas/geometrías
                         ▼
        ┌─────────────────────────────────┐
        │         SILVER GLOBAL           │  Datos limpios, enriquecidos
        └──────────────┬──────────────────┘  y estandarizados
                       │
          ┌────────────┴─────────────────────────────┐
          ▼ (Estrategia recomendada:                  ▼ (Alternativa:
             partición / filtro por zona)                gold consolidado antes de partir)
   ┌──────────────────────────────────────────────┐
   │          SILVER PARTICIONADO POR ZONA        │
   │   (Zona A / Zona B / Zona C / ...)           │
   │   - Filtrado espacial / geo-fencing          │
   │   - Atributos específicos por zona           │
   └──────────────────────┬───────────────────────┘
                          │ Agregaciones, KPIs, métricas de negocio por zona
                          ▼
   ┌──────────────────────────────────────────────┐
   │           GOLD POR ZONA / DATA MARTS         │
   │   (Tablas listas para consumo analítico)     │
   └──────────────────────┬───────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   [ Dashboards BI ]  [ Mapas / GIS ]  [ Modelos ML / Analítica ]
```

## 2. Capas de la arquitectura

### Bronze / Raw — datos crudos
- Ingesta tal cual de las fuentes (DATIC, SIMUR, Cámara de Comercio, SIMAT, NDVI/Sentinel-2, censo arbóreo, etc.).
- **No se transforma.** Se conserva el dato original con su linaje (origen, fecha de corte, fecha de ingesta) y metadatos.
- En el datalake actual corresponde a `s3://aca-prod-calitrack-itt-datalake/raw/` (zona protegida: **no modificar**).

### Silver Global — datos limpios y estandarizados
- Limpieza, tipado de campos, parseo de fechas, estandarización de **coordenadas/geometrías** (CRS homogéneo, p.ej. EPSG:4326).
- Enriquecimiento transversal (catálogos de `reference/`, normalización de categorías de delitos, etc.).
- Aún **sin partir por zona**: una vista global y consistente de cada fuente.
- Corresponde a `curated/` en el datalake.

### Silver Particionado por Zona (estrategia recomendada)
- Filtrado espacial / **geo-fencing** contra el polígono de cada zona (Ciudad Paraíso, Roosevelt, Av. Ciudad de Cali, Barrio Obrero, Pulmón de Oriente).
- Atributos específicos por zona.
- Es el mismo principio del `geopandas.sjoin` que ya hacen los notebooks (verificación espacial real contra el polígono), llevado al pipeline.

### Gold por Zona / Data Marts — listo para consumo
- Agregaciones, **KPIs y métricas de negocio por zona**: scores por dimensión y el ITT.
- Tablas listas para consumo analítico (equivalente al Excel consolidado y a `data.json` del sitio, pero servidas desde el datalake).
- Corresponde a `analytics/` en el datalake.

## 3. Dos estrategias de partición

| Estrategia | Descripción | Cuándo conviene |
|---|---|---|
| **Recomendada:** Silver → partición por zona → Gold por zona | Se parte en Silver, cada zona agrega sus KPIs | Zonas con reglas/atributos distintos; escalable al agregar zonas |
| **Alternativa:** Gold consolidado y luego partir | Se calcula un Gold global y después se derivan vistas por zona | Si los KPIs son idénticos entre zonas y se prioriza una sola tabla maestra |

## 4. Consumo final

- **Dashboards BI** — tableros de seguimiento del ITT.
- **Mapas / GIS** — visualización geoespacial (equivalente al mapa folium actual).
- **Modelos ML / Analítica** — evaluación de impacto, series temporales, territorio espejo.

## 5. Correspondencia con el datalake actual

| Capa medallón | Zona S3 actual | Notas |
|---|---|---|
| Bronze / Raw | `raw/` | Protegida — no modificar |
| Silver Global | `curated/` | Limpio y estandarizado |
| Silver por Zona | `curated/<zona>/` (propuesto) | Filtrado espacial por polígono |
| Gold por Zona | `analytics/` | Tablas de consumo (scores, ITT) |
| Sandbox | `pruebas/` | Hoy aloja `itt_Ciudad_Paraiso/` con dimensiones 1-6 |

> Hoy los datos de Ciudad Paraíso viven en `pruebas/itt_Ciudad_Paraiso/`. La hoja de
> ruta plantea promoverlos a raw → curated → analytics siguiendo el flujo medallón.

## 6. Pendientes / decisiones abiertas

- Definir qué servicio orquesta el pipeline (Lambda por etapa, Glue, Step Functions).
- Formato de almacenamiento en Silver/Gold (GeoParquet vs. GeoJSON) para escala y GIS.
- Idempotencia por fecha de corte (`curated/<fuente>/<YYYY-MM-DD>/`, ver protocolo).
- Elegir estrategia de partición (sección 3) según cómo evolucionen las zonas.
