# Datos — ITT Barrio Obrero

Poligono unico del barrio. Sin tramos. Periodo: 2023–2026 T1.

Los archivos estan organizados por dimension directamente en el repo — no se requiere extraccion de ZIP.

## Estructura de carpetas

```
itt_barrio_obrero/
├── Geojson_Barrio_Obrero.geojson        Poligono base (CRS: ESRI::103599 — reproyectar a EPSG:4326 en notebook)
├── 1_Dimension_Seguridad/
│   ├── DATIC_homicidios_2023_2026T1_Barrio_O.geojson   campo fecha: fechah (MM/DD/YYYY)
│   ├── DATIC_hurtos_2023_2026T1_Barrio_O.geojson        campo fecha: fecha_hech (ISO)
│   ├── DATIC_comparendos_2023_2026T1_Barrio_O.geojson   campo fecha: fecha_hech | campo categoria: agrupado
│   └── CAI_MECAL_CALI_OBRERO.geojson                    capa de referencia (1 punto)
├── 2_Dimension_Cohesion_Social/
│   ├── DATIC_violencia_intrafamiliar_2023_2026T1_Barrio_O.geojson   campo fecha: fecha_hech
│   └── VBG_2025_OBRERO.geojson                          capa de referencia (2 puntos, solo 2025)
├── 3_Dimension_Movilidad/
│   ├── BD_SINIESTROS_2023_2026_COMUNA_BARRIO_OBRERO.geojson   campo fecha: Fecha (ISO)   16 eventos 2023-2026-Q2
│   ├── BD_COMPARENDOS_2025_COMUNA_BARRIO_OBRERO.geojson        comparendos de transito 2025 (CRS: EPSG:9377)
│   └── BD_COMPARENDOS_2025_COMUNA_BARRIO_OBRERO.qmd            metadata QGIS
├── 4_Desarrollo_Economico/              vacía — pendiente de datos
├── 5_Entorno_Urbano/
│   ├── Arboles_Dagma_OBRERO.geojson     151 arboles registrados
│   └── NDVI_Barrio_Obrero/
│       ├── Barrio_Obrero_ndvi_2023.tif
│       ├── Barrio_Obrero_ndvi_2024.tif
│       ├── Barrio_Obrero_ndvi_2025.tif
│       └── Barrio_Obrero_ndvi_2026.tif
└── 6_Educacion/
    └── Sedes_educativas_oficiales_OBRERO.geojson   2 sedes oficiales
```

## Archivos clave por dimension y cobertura real

| Dimension | Archivo DATIC | Registros | Cobertura real | Campo fecha |
|---|---|---|---|---|
| Seguridad | `DATIC_homicidios_*` | 3 | 2024-Q1 → 2025-Q1 | `fechah` (MM/DD/YYYY) |
| Seguridad | `DATIC_hurtos_*` | 155 | 2023-Q1 → 2026-Q1 | `fecha_hech` |
| Seguridad / Cohesion | `DATIC_comparendos_*` | 374 | 2023-Q1 → 2026-Q1 | `fecha_hech` |
| Cohesion Social | `DATIC_violencia_intrafamiliar_*` | 24 | 2023-Q1 → 2026-Q1 | `fecha_hech` |
| Movilidad | `BD_SINIESTROS_2023_2026_*` | 16 | 2023 → 2026-Q2 | `Fecha` |

## Categorias en comparendos DATIC

| Categoria (`agrupado`) | Eventos | Uso en ITT |
|---|---|---|
| ARMAS EXCEPTO DE FUEGO | 248 | No incorporado aun |
| DESACATO / IRRESPETO A LA AUTORIDAD | 76 | No incorporado |
| SUSTANCIAS PSICOACTIVAS | 41 | Analisis contextual (Cohesion Social) |
| RIÑAS | 9 | Indicador de Cohesion Social |

## Notas de CRS

- Todos los archivos DATIC y de siniestros: `CRS84` (WGS84 / EPSG:4326).
- `Geojson_Barrio_Obrero.geojson`: `ESRI::103599` — el notebook lo reproyecta con `.to_crs('EPSG:4326')`.
- `BD_COMPARENDOS_2025_COMUNA_BARRIO_OBRERO.geojson`: `EPSG:9377` — no entra al calculo ITT.

## Tratamiento de 2026 en el notebook

- DATIC cubre hasta 2026-Q1. Los trimestres Q2/Q3/Q4 de 2026 se marcan como `NaN` en `corr_trim`.
- Siniestros cubre hasta 2026-Q2 (1 evento, 2026-04-15). Q3 y Q4 de 2026 = `NaN` en movilidad trimestral.
- Las graficas de linea muestran la serie hasta el ultimo dato valido con linea de corte punteada.
- El heatmap deja celdas NaN en blanco.

## Ejecucion en Colab

```python
# No se extrae ZIP — datos directamente en el repo
REPO = Path('/content/itt_repos_cali')
D    = REPO / 'data' / 'itt_barrio_obrero'
```

El notebook hace git clone / git pull automaticamente en la Celda 3A.
