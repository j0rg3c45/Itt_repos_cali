# Fuentes de datos

Este documento registra el inventario operativo de datos por zona y deja trazabilidad para el uso por notebooks y agentes.

## Estado actual por zona

### ITT Roosevelt

Estado actual:

- `data/itt_roosevelt/` ya contiene `Roosevelt.zip`.
- Existe carpeta de trabajo descomprimida `data/itt_roosevelt/Roosevelt_unzipped/`.
- El notebook `01_itt_roosevelt.ipynb` ya fue adaptado para esta estructura de insumos.

Insumos identificados en la zona Roosevelt:

| Indicador / capa | Archivo identificado | Observaciones |
|---|---|---|
| Buffer / tramos | `Geojson_tramos_Roosevelt_Buffer_100.geojson` | Base espacial del corredor |
| Tramos | `Geojson_tramos_Roosevelt.geojson` | Geometria auxiliar |
| Homicidios | `HOMICIDIOS_2023_2025_Roosevelt.geojson` | Eventos 2023-2025 |
| Hurtos | `HURTOS_2023_2025_Roosevelt.geojson` | Eventos 2023-2025 |
| Comparendos | `COMPARENDOS_2023_2025_Roosevelt.geojson` | Filtrar `agrupado="RINAS"` si aplica |
| Siniestros | `BD_SINIESTROS_2023_2025_COMUNA_BARRIO_4326_Roosevelt.geojson` | Base de movilidad |
| VIF | `VIOLENCIA_INTRAFAMILIAR_2023_2025_Roosevelt.geojson` | Cohesion social |
| VBG | `VBG_2025_Roosevelt.geojson` | Insumo complementario, aun no incorporado al ITT |
| Sedes | `Sedes_educativas_oficiales_Roosevelt.geojson` | Solo mapa / apoyo territorial |

### ITT Avenida Ciudad de Cali

Estado actual segun notebook `02_itt_avenida_ciudad_de_cali.ipynb` (3 ZIPs versionados en repo):

| ZIP | Indicador / capa | Archivo en repo | Observaciones |
|---|---|---|---|
| ZIP1 | Poligono corredor | `ciudad_de_Cali_100m.geojson` | 8 tramos, campo `tramo` orden norte→sur |
| ZIP1 | Capas estaticas | VBG, arboles, sedes, CAI | Solo mapa / apoyo territorial |
| ZIP2 | Homicidios | `DATIC_homicidios_2023_2026T1_filtrado_ciudad_de_Cali_100m.geojson` | DATIC 2023-2026 T1 |
| ZIP2 | Hurtos | `DATIC_hurtos_2023_2026T1_filtrado_ciudad_de_Cali_100m.geojson` | DATIC 2023-2026 T1 |
| ZIP2 | VIF | `DATIC_violencia_intrafamiliar_2023_2026T1ciudad_de_Cali_100m.geojson` | DATIC 2023-2026 T1 |
| ZIP2 | Comparendos | `DATIC_comparendos_2023_2026T1_filtrado_ciudad_de_Cali_100m.geojson` | Filtrar `agrupado` startswith 'RI' para rinas |
| ZIP3 | Siniestros | `BD_SINIESTROS_2023_2025_COMUNA_BARRIO_4326_filtrado_ciudad_de_Cali_100m.geojson` | 745 eventos, WGS84, campo `Fecha` ISO, `Tipo_Confi` |

Estado en repo:

- Los 3 ZIPs estan versionados en `data/itt_avenida_ciudad_de_cali/`.
- En Colab: celda git pull descarga repo → Cell 3A extrae los 3 ZIPs a sus carpetas respectivas.
- ZIP3 extrae a `/content/movilidad_acc/` para evitar colision con ZIP2 (mismo nombre de carpeta interna).

### ITT Barrio Obrero

Estado actual segun notebook `03_itt_barrio_obrero.ipynb` (archivos directamente en repo, sin ZIP):

| Dimension | Archivo | Carpeta | Registros | Cobertura real | Campo fecha | CRS |
|---|---|---|---|---|---|---|
| Base | `Geojson_Barrio_Obrero.geojson` | raiz | — | — | — | ESRI:103599 → reproyectar |
| Seguridad | `DATIC_homicidios_2023_2026T1_Barrio_O.geojson` | `1_Dimension_Seguridad/` | 3 | 2024-Q1→2025-Q1 | `fechah` (MM/DD/YYYY) | CRS84 |
| Seguridad | `DATIC_hurtos_2023_2026T1_Barrio_O.geojson` | `1_Dimension_Seguridad/` | 155 | 2023-Q1→2026-Q1 | `fecha_hech` (ISO) | CRS84 |
| Seguridad / Cohesion | `DATIC_comparendos_2023_2026T1_Barrio_O.geojson` | `1_Dimension_Seguridad/` | 374 | 2023-Q1→2026-Q1 | `fecha_hech` | CRS84 |
| Ref. Seguridad | `CAI_MECAL_CALI_OBRERO.geojson` | `1_Dimension_Seguridad/` | 1 punto | — | — | CRS84 |
| Cohesion Social | `DATIC_violencia_intrafamiliar_2023_2026T1_Barrio_O.geojson` | `2_Dimensión_Cohesion_Social/` | 24 | 2023-Q1→2026-Q1 | `fecha_hech` | CRS84 |
| Ref. Cohesion | `VBG_2025_OBRERO.geojson` | `2_Dimensión_Cohesion_Social/` | 2 puntos | 2025 | — | CRS84 |
| Movilidad | `BD_SINIESTROS_2023_2026_COMUNA_BARRIO_OBRERO.geojson` | `3_Dimension_Movilidad/` | 16 | 2023→2026-Q2 (1 evento 2026-04-15) | `Fecha` (ISO) | CRS84 |
| Movilidad (no ITT) | `BD_COMPARENDOS_2025_COMUNA_BARRIO_OBRERO.geojson` | `3_Dimension_Movilidad/` | — | 2025 | — | EPSG:9377 |
| Entorno Urbano | `Arboles_Dagma_OBRERO.geojson` | `5_Entorno_Urbano/` | 151 | — | — | CRS84 |
| Entorno Urbano | `Barrio_Obrero_ndvi_2023/2024/2025/2026.tif` | `5_Entorno_Urbano/NDVI_Barrio_Obrero/` | 4 rasters | 2023-2026 | — | — |
| Educacion | `Sedes_educativas_oficiales_OBRERO.geojson` | `6_Educacion/` | 2 | — | — | CRS84 |

Estado en repo:

- Todos los GeoJSON estan directamente en subcarpetas por dimension — no se requiere extraccion de ZIP.
- `4_Desarrollo_Economico/` vacia — pendiente de datos.
- En Colab: `git clone` o `git pull` en `/content/itt_repos_cali` entrega todo. `DATA_DIR = Path("/content/itt_repos_cali/data/itt_barrio_obrero")`.

Categorias en comparendos DATIC (campo `agrupado`):

| Categoria | Eventos | Uso en ITT |
|---|---|---|
| ARMAS EXCEPTO DE FUEGO | 248 | No incorporado aun |
| DESACATO / IRRESPETO A LA AUTORIDAD | 76 | No incorporado |
| SUSTANCIAS PSICOACTIVAS | 41 | Analisis contextual (Cohesion Social) |
| RIÑAS | 9 | Indicador Cohesion Social — filtrar `agrupado=="RIÑAS"` |

Soporte metodologico adicional para `Entorno Urbano` en Barrio Obrero:

| Fuente complementaria | Uso actual en notebook | Periodicidad real | Observaciones |
|---|---|---|---|
| `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx` | Proxy experimental de `Entorno Urbano` | Anual `2024` | Usa `Comuna 9` como proxy territorial para Barrio Obrero |
| `BD_PREDIOS_TITULADOS 2023-2025 (1).xlsx` | No usado en calculo actual | Anual `2023-2025` | Contexto de formalizacion |
| `BD_SUBSIDIOS_MEJORAMIENTO_VIV_AÑOS_2024_2025 (1).xlsx` | No usado en calculo actual | Anual `2024-2025` | Contexto de intervencion en vivienda |

## Recomendaciones de trazabilidad

Para cada insumo registrar:

- Nombre exacto del archivo.
- Entidad fuente.
- Fecha de entrega o descarga.
- Periodo cubierto.
- CRS.
- Campos clave.
- Transformaciones aplicadas antes del notebook.
- Observaciones de calidad.

## Nota para agentes

Si una fuente no esta presente en el repo, debe marcarse como:

- No versionada en repositorio.
- Disponible solo en Colab o carga manual.
- Pendiente de entrega.

## Referencias territoriales en data/referencia/

| Archivo | Uso potencial | Estado |
|---|---|---|
| `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx` | Proxy de `Entorno Urbano` por deficit habitacional | Usado experimentalmente en `03_itt_barrio_obrero.ipynb` con Comuna 9 como proxy de Barrio Obrero |
| `BD_PREDIOS_TITULADOS 2023-2025 (1).xlsx` | Indicador de formalizacion / gestion | En analisis, no usado en calculo actual |
| `BD_SUBSIDIOS_MEJORAMIENTO_VIV_AÑOS_2024_2025 (1).xlsx` | Indicador de intervencion en vivienda | En analisis, no usado en calculo actual |
| `bienestar_RA2026_base_limpia.xlsx` | Registro de Atencion SBS 2026 — 12.937 personas atendidas en programas sociales | **Descartado para calculo ITT:** solo 2026 (sin serie), 72% sin comuna, mide asistencia a programas no condicion territorial |

Nota metodologica sobre el archivo de deficit habitacional:

- No tiene granularidad mensual ni trimestral; solo aporta un corte anual 2024.
- En Barrio Obrero la visualizacion es un heatmap de componentes del deficit cualitativo 2024, no una serie temporal observada.

Nota sobre bienestar_RA2026:

- Contiene: Primera Infancia (70%), SIDICU, Victimas, prevencion VBG, Discapacidad, entre otros programas.
- Podria usarse como complemento narrativo futuro si se resuelve que el 72% de registros no tiene comuna asignada.
