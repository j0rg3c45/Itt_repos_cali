# Lambda — Generador de Mapa Interactivo (Emergencia Sísmica)

> **Origen:** proyecto **Emergencia Sísmica** del CDO (bucket `aca-prod-calitrack-sismo-cali`).
> Se guarda aquí como **plantilla de referencia** del patrón "Lambda lee `curated/` →
> genera HTML Leaflet → escribe en `analytics/`", que es el mismo patrón que usará el
> ITT para su mapa/visor. **Este código NO apunta al datalake del ITT**; es el molde a
> adaptar (ver sección "Adaptación al ITT").

## Qué hace

Lee cruces de datos de la emergencia sísmica desde `curated/` + el RUD georreferenciado
(IDECS), y genera un mapa interactivo HTML con Leaflet + MarkerCluster que escribe en
`analytics/mapa/`. Devuelve una URL pre-firmada (7 días).

Capas del mapa:
1. Reportes ciudadanos (Blend/InstantDB)
2. Evaluaciones técnicas (EDE)
3. RUD cruzado con reportes (por dirección)
4. RUD georreferenciado IDECS (geocodificación municipal)

## Configuración

| Variable de entorno | Valor por defecto |
|---|---|
| `S3_BUCKET` | `aca-prod-calitrack-sismo-cali` |
| `CRUCES_PREFIX` | `curated/cruces` |
| `RUD_GEO_PREFIX` | `curated/rud_georreferenciado` |
| `OUTPUT_PREFIX` | `analytics/mapa` |

Parámetros estándar (ver `docs/07_conexion_aws_calitrack.md`):
- Runtime: `python3.14`
- Layers: `AWSSDKPandas-Python314:11` (usa pandas) + `aca-prod-openpyxl-layer:1` si lee xlsx
- Tag: `Proyecto=CaliTrack`
- Región: `us-east-1`
- Dependencias: `boto3` (incluido en el runtime), `pandas` (via layer AWSSDKPandas)

## Entrada / salida

- **Entrada:** archivos en `curated/cruces/<fecha>/*.json`, `raw/blend_instantdb/reporte/<fecha>/reporte.json`, y CSV en `curated/rud_georreferenciado/`.
- **Salida:** `analytics/mapa/mapa_emergencia_cali.html` + URL pre-firmada.
- **Trigger:** invocación (manual / evento), toma siempre la fecha más reciente disponible.

## Adaptación al ITT (pendiente)

Para reusar este patrón en el ITT habría que:
- Apuntar `S3_BUCKET` a `aca-prod-calitrack-itt-datalake`.
- Leer de `analytics/` los scores/ITT por zona (Gold) en vez de los cruces de sismo.
- Cambiar las capas por: polígono de zona, red peatonal OSM, NDVI, eventos por tipo
  (manteniendo la **regla de privacidad**: solo ubicación + tipo, sin PII).
- Reusar el patrón de salida HTML + URL pre-firmada, o servirlo vía la capa API.

> Nota de privacidad: la plantilla original muestra direcciones y datos de damnificados
> (contexto de emergencia, acceso restringido vía URL pre-firmada). En el ITT público
> rige la regla de **solo ubicación + tipo** para eventos de seguridad/violencia.
