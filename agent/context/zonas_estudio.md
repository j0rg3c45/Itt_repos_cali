# Zonas de estudio

## ITT Roosevelt

- Estado: implementado.
- Notebook: `notebooks/01_itt_roosevelt.ipynb`
- Unidad de analisis: corredor con buffer de 100 m.
- Metodo espacial: uso de capa buffer y eventos territoriales de la zona.
- Periodo: 2023-2025.
- Metodologia: usa `ref_min/ref_max` fijos y la estructura funcional de Barrio Obrero.
- Referentes provisionales: Entorno Urbano 39.2, Educacion y Desarrollo 54.9, Vulnerabilidad 54.1.
- Datos en repo: `Roosevelt.zip` presente y carpeta descomprimida de trabajo disponible.
- Observacion: notebook operativo, pendiente de afinacion futura de referentes si se incorporan nuevos indicadores de entorno.

## ITT Avenida Ciudad de Cali

- Estado: implementado y actualizado (ref_min/ref_max fijos, 3 ZIPs, heatmaps por tramo con orden geografico).
- Notebook: `notebooks/02_itt_avenida_ciudad_de_cali.ipynb` — 42 celdas.
- Unidad de analisis: 8 tramos buffer de 100 m sobre corredor vial (~4.5 km).
- Metodo espacial: spatial join de eventos a tramos usando `gdf_tramos['tramo'].astype(int)` (orden norte→sur).
- Periodo: 2023-2026 T1. Movilidad solo 2023-2025 (sin datos 2026 — peso redistribuido en ITT).
- Metodologia: usa `ref_min/ref_max` fijos por indicador. ITT 2026 excluye Movilidad (NaN, no proxy).
- Referentes provisionales: Entorno Urbano 39.2, Educacion y Desarrollo 54.9, Vulnerabilidad 54.1.
- Datos en repo: 3 ZIPs versionados en `data/itt_avenida_ciudad_de_cali/`.
- Fuentes: ZIP1 (poligono + estaticas), ZIP2 (DATIC seguridad/cohesion), ZIP3 (siniestros movilidad).
- Tramo sin datos: T8 (extremo sur) tiene 0 siniestros en ZIP3 — dato real confirmado.
- Ejecucion Colab: celda git pull (si repo ya existe) + Cell 3A extrae 3 ZIPs + Cell 3 verifica paths.

## ITT Barrio Obrero

- Estado: implementado y actualizado (DATIC 2023-2026 T1, paleta Okabe-Ito, heatmaps cividis, graficas linea+relleno).
- Notebook: `notebooks/03_itt_barrio_obrero.ipynb`
- Unidad de analisis: poligono unico del barrio.
- Metodo espacial: no requiere spatial join por tramo — eventos pre-filtrados a la zona.
- Periodo: 2023-2026 T1. `ANIOS = [2023, 2024, 2025, 2026]`.
- Metodologia: usa `ref_min/ref_max` fijos por indicador.
- Referentes base: `REF_ENTORNO_U = 39.2`, `REF_EDUC_DES = 54.9`, `REF_VULNERABILIDAD = 54.1`.
- Entorno Urbano: notebook puede sobrescribir `39.2` con proxy experimental de `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx` (Comuna 9 como proxy, corte anual 2024).
- Visualizaciones: heatmaps cividis por dimension, graficas trimestrales linea+relleno con paleta Okabe-Ito.
- Tratamiento 2026: DATIC cubre hasta Q1; Q2/Q3/Q4 = `NaN` en `corr_trim`. Siniestros: cubre hasta 2026-Q2 (1 evento 2026-04-15); Q3/Q4 = `NaN`.
- Datos en repo: archivos GeoJSON directamente en subcarpetas por dimension (sin ZIP). Git clone entrega todo.
- Estructura de datos: `1_Dimension_Seguridad/`, `2_Dimensión_Cohesion_Social/`, `3_Dimension_Movilidad/`, `4_Desarrollo_Economico/` (vacia), `5_Entorno_Urbano/` (incluye NDVI 2023-2026), `6_Educacion/`.
- Fuentes DATIC: `DATIC_homicidios_*` (campo `fechah` MM/DD/YYYY), `DATIC_hurtos_*`, `DATIC_comparendos_*`, `DATIC_violencia_intrafamiliar_*` (campo `fecha_hech` ISO).
- CRS: poligono ESRI:103599 → reproyectado a EPSG:4326 en notebook. Comparendos de transito EPSG:9377 — no entra al calculo ITT.
- Indicador contextual pendiente: Concentracion de vulnerabilidad activa = 54.1 por 1.000 hab (73 personas Sub PyE 2025 / ~1.349 hab). Solo 2025, sin serie — mantener como contexto, no implementado en ITT.

## ITT Ciudad Paraíso (Comuna 3)

- Estado: implementado y verificado (local con `uv` + Colab).
- Notebook: `notebooks/08_itt_ciudad_paraiso_5dim.ipynb`
- Unidad de analisis: poligono unico de la zona de renovacion urbana (San Pascual, El Calvario, San Juan Bosco, Santa Rosa). Area: 33.70 ha (337,039.2 m²).
- Periodo: 2023-2026 (2026 parcial — cobertura incompleta en todas las fuentes; su nivel se marca "Parcial — no comparable").
- Metodologia: `ref_min/ref_max` fijos; 5 dimensiones (Seguridad 27%, Movilidad 22%, DesSocial 19%, EntornoU 17%, DesEco 15%).
- Entorno Urbano: **datos propios** (NO proxy). NDVI anual 2023-2026 (4 rasters) + censo arboreo (312 arboles, 303 vivos/nuevos). `score_entorno_u = mean(score_ndvi, score_arbolado)`.
- Verificacion espacial: `geopandas.sjoin` contra el poligono real (los campos nom_barrio/comuna de las fuentes no son confiables en esta zona).
- Educacion y Desarrollo: fuera de alcance de este repo (otro repositorio). DesSocial = solo VIF+Riñas+SPA.
- Datos en repo: `data/Ciudad_Paraiso/` con subcarpetas 1-6 por dimension + `5_Dimension_Entorno_Urbano/` (censo + NDVI) + poligono (geojson y shape).
- ITT resultante: 2023=44.1, 2024=55.5, 2025=58.5 (Consolidacion), 2026=81.4 (Parcial).
- Publicacion: resultados en el sitio GitHub Pages (`github_pages/`, ver contexto_proyecto.md).
