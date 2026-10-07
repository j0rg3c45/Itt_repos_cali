# Contexto Maestro para Agente

Este archivo resume el contexto mas importante del repo para que otro agente pueda trabajar con buen criterio metodologico y operativo desde el inicio.

## 1. Objetivo del proyecto

El repositorio calcula el **Indice de Transformacion Territorial (ITT)** para zonas de intervencion urbana de Cali, Colombia.

El ITT busca medir transformacion positiva del territorio en escala `0-100` y permitir comparaciones entre zonas usando una metodologia comun.

## 2. Regla metodologica principal

La metodologia vigente del proyecto exige:

- Usar `ref_min/ref_max` fijos por indicador.
- No usar min-max relativo calculado desde la propia muestra de la zona cuando el territorio es pequeno o los conteos son bajos.
- Diferenciar entre datos reales, referentes provisionales y resultados efectivamente calculados.

La fuente metodologica principal y prioritaria es:

- `agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md`

Si hay contradiccion entre un resumen corto en `docs/` y la guia metodologica completa, debe priorizarse la guia metodologica completa y luego el estado real de los notebooks.

## 3. Dimensiones y pesos oficiales

El ITT vigente usa 5 dimensiones:

- Seguridad: `0.30`
- Movilidad: `0.25`
- Entorno Urbano: `0.20`
- Educacion y Desarrollo: `0.13`
- Cohesion Social: `0.12`

La suma de los pesos debe ser `1.0`.

## 4. Referentes provisionales actuales

Mientras una zona no tenga datos propios para ciertas dimensiones o indicadores, el proyecto usa referentes de `Pulmon de Oriente`.

Valores vigentes:

- `Entorno Urbano = 39.2`
- `Educacion y Desarrollo = 54.9`
- `Vulnerabilidad = 54.1`

Estos valores deben tratarse como **provisionales**, no como mediciones propias de la zona analizada.

Excepcion actual importante:

- En `notebooks/03_itt_barrio_obrero.ipynb`, `Entorno Urbano` ya puede dejar de usar `39.2` si se ejecuta la celda proxy basada en `deficit habitacional 2024`.

## 5. Estado real de notebooks

### Notebook de referencia principal

- `notebooks/03_itt_barrio_obrero.ipynb`

Este notebook es la referencia operativa mas importante del repo porque:

- Ya usa `ref_min/ref_max` fijos.
- Tiene la estructura metodologica vigente.
- Es el mejor punto de partida para revisar logica de calculo, normalizacion, pesos, series anuales y trimestrales, y exportacion.
- Ademas, ya documenta un caso real de reemplazo parcial del referente fijo de `Entorno Urbano` mediante un proxy territorial.

### Detalle actual de Entorno Urbano en Barrio Obrero

- La celda `3B` recalcula `REF_ENTORNO_U` con `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx`.
- La base territorial usada es `Comuna 9`, como aproximacion a `Barrio Obrero`.
- El proxy combina dos componentes:
  - `Deficit Cualitativo`
  - `Deficit Cualitativo / Deficit Habitacional`
- Ambos componentes se normalizan con referencias fijas y luego se promedian.
- La celda `3C` agrega una visualizacion `heatmap` de componentes del deficit cualitativo 2024.
- Ese insumo no tiene periodicidad mensual ni trimestral observada; es un corte anual `2024`.
- `Predios titulados` y `subsidios de mejoramiento` fueron revisados, pero no hacen parte del calculo actual de esta dimension.

### Roosevelt

- `notebooks/01_itt_roosevelt.ipynb`

Estado:

- Implementado.
- Ya migrado a `ref_min/ref_max` fijos.
- Replica la estructura de Barrio Obrero, adaptada a corredor con buffer.
- Usa referentes provisionales para `Entorno Urbano`, `Educacion y Desarrollo` y `Vulnerabilidad`.

### Avenida Ciudad de Cali

- `notebooks/02_itt_avenida_ciudad_de_cali.ipynb`

Estado:

- Implementado y actualizado — ya usa `ref_min/ref_max` fijos.
- Analiza 8 tramos buffer de 100 m sobre corredor vial (~4.5 km).
- Requiere `spatial join` de eventos a tramos usando `gdf_tramos['tramo'].astype(int)` (orden norte→sur).
- Periodo 2023-2026 T1. Movilidad solo 2023-2025 — peso redistribuido en ITT 2026.
- Paleta Okabe-Ito, heatmaps cividis por tramo.
- Datos: 3 ZIPs versionados en `data/itt_avenida_ciudad_de_cali/`.

### Pulmon de Oriente 2026

- `notebooks/04_itt_pulmon_oriente_2026.ipynb`

Estado:

- No es el notebook comparativo del proyecto.
- Es una salida parcial para `Seguridad T1 2026`.
- Debe tratarse como notebook de seguimiento, no como referencia integral del flujo principal.

Rol en el proyecto:

- Sirve como referencia parcial de seguimiento.
- Pulmon de Oriente tambien es la base de los referentes provisionales usados por otras zonas.

### Comparativo entre zonas

- `notebooks/05_comparativo_itt_zonas.ipynb`

Estado:

- Es la plantilla comparativa real que existe hoy en disco.
- Depende de resultados exportados por zona.
- Todavia no representa un flujo consolidado totalmente maduro.

## 6. Zonas del repo y como pensarlas

### Barrio Obrero

- Unidad de analisis: poligono unico.
- No requiere `spatial join` por tramo — eventos pre-filtrados a la zona.
- Periodo: 2023-2026 T1. `ANIOS = [2023, 2024, 2025, 2026]`.
- Caso mas limpio para entender la metodologia vigente.
- Caso actual mas importante para el uso experimental de `deficit habitacional` dentro de `Entorno Urbano`.
- Datos directamente en subcarpetas por dimension (sin ZIP): `1_Dimension_Seguridad/`, `2_Dimensión_Cohesion_Social/`, `3_Dimension_Movilidad/`, `4_Desarrollo_Economico/` (vacia), `5_Entorno_Urbano/` (con NDVI 2023-2026), `6_Educacion/`.
- Fuentes DATIC actualizadas: campo `fechah` (MM/DD/YYYY) en homicidios, `fecha_hech` (ISO) en el resto.
- Tratamiento 2026: DATIC cubre hasta Q1; Q2/Q3/Q4 enmascarados como `NaN`. Siniestros cubre hasta Q2 (1 evento 2026-04-15); Q3/Q4 = `NaN`.
- Visualizaciones: paleta Okabe-Ito, heatmaps cividis, graficas trimestrales linea+relleno.

### Roosevelt

- Unidad de analisis: corredor con buffer de 100 m.
- Periodo trabajado: `2023-2025`.
- Caso homologado a la metodologia vigente pero en contexto de corredor.

### Avenida Ciudad de Cali

- Unidad de analisis: 8 tramos buffer de 100 m.
- Metodo espacial: `spatial join` de eventos a tramos.
- Caso mas complejo espacialmente.
- Ya homologado a `ref_min/ref_max` fijos. Periodo 2023-2026 T1.

### Pulmon de Oriente

- Funciona como referencia metodologica.
- Aporta los scores provisionales usados en otras zonas.
- Tiene notebook propio parcial 2026, pero no equivale al flujo principal de comparacion entre zonas.

## 7. Disponibilidad real de datos

### Datos presentes en el repo

- `data/itt_roosevelt/`: `Roosevelt.zip` + carpeta descomprimida `Roosevelt_unzipped/`.
- `data/itt_barrio_obrero/`: GeoJSON directamente en subcarpetas por dimension — no requiere ZIP. Git clone entrega todo.
- `data/itt_avenida_ciudad_de_cali/`: 3 ZIPs versionados (`Geojson_Ciudad_de_Cali (1).zip`, `geojson_filtrado_ciudad_de_Cali_100m.zip`, `geojson_Movilidad_ciudad_de_Cali_100m.zip`).
- `data/itt_pulmon_oriente/`: datos de referencia para scores provisionales.

### Datos no versionados en el repo

- Todos los insumos clave estan versionados en el repo para las 3 zonas activas.
- `4_Desarrollo_Economico/` en Barrio Obrero: vacia, pendiente de datos.

## 8. Referencias territoriales y su estado actual

La carpeta `data/referencia/` contiene Excel de apoyo metodologico:

- `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx` — usado experimentalmente en notebook 03 para proxy Entorno Urbano.
- `BD_PREDIOS_TITULADOS 2023-2025 (1).xlsx` — no usado en calculo actual.
- `BD_SUBSIDIOS_MEJORAMIENTO_VIV_AÑOS_2024_2025 (1).xlsx` — no usado en calculo actual.
- `Caracterizacion Personas Sub PyE (2025).xlsx` — 24.087 registros, Secretaria de Bienestar Social. Indicador derivado: concentracion de vulnerabilidad activa 54.1 por 1.000 hab (73 personas Sub PyE / ~1.349 hab). Solo contexto, no implementado en ITT.
- `Caracterizacion R.A. 2026 corte may-6.xlsx` — Registro de Atencion SBS 2026. Descartado para calculo ITT: solo 2026 (sin serie), 72% sin comuna, mide asistencia a programas no condicion territorial.

Lectura correcta:

- Solo `deficit habitacional` esta incorporado al calculo (experimental, proxy Entorno Urbano Barrio Obrero).
- `Predios titulados`, `subsidios de mejoramiento`, `Sub PyE` y `RA2026` siguen fuera del calculo actual.
- `Sub PyE 2025` y `RA2026` pueden usarse como complemento narrativo futuro si se resuelve la cobertura territorial.

## 9. Donde vive el conocimiento

Para responder bien sobre este repo, un agente debe leer en este orden:

1. `agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md`
2. `agent/context/contexto_proyecto.md`
3. `agent/context/zonas_estudio.md`
4. `docs/03_fuentes_datos.md`
5. `notebooks/03_itt_barrio_obrero.ipynb`
6. `notebooks/01_itt_roosevelt.ipynb`
7. `notebooks/02_itt_avenida_ciudad_de_cali.ipynb`

## 10. Precauciones para otro agente

- No asumir que todo notebook implementado ya esta metodologicamente homologado.
- No confundir `04_itt_pulmon_oriente_2026.ipynb` con el comparativo entre zonas.
- No asumir que `outputs/` ya contiene resultados versionados listos para consolidacion.
- Tratar con cuidado textos con problemas de codificacion como `año`, `T1`, o caracteres especiales en algunos `.md` y notebooks.
- Distinguir siempre entre:
  - dato observado real
  - score normalizado
  - referente provisional
  - resultado exportado
- No presentar el proxy de `Entorno Urbano` de Barrio Obrero como serie mensual o trimestral observada.

## 11. Resumen ejecutivo para handoff rapido

Este repo tiene una metodologia consolidada y tres zonas activas. `Barrio Obrero` es la referencia operativa vigente: usa `ref_min/ref_max` fijos, DATIC 2023-2026 T1, datos directamente en carpetas por dimension (sin ZIP), paleta Okabe-Ito, heatmaps cividis y graficas trimestrales linea+relleno. `Roosevelt` esta alineado con esa metodologia para 2023-2025. `Avenida Ciudad de Cali` ya fue homologada a `ref_min/ref_max` fijos con 3 ZIPs y 8 tramos, periodo 2023-2026 T1. `Pulmon de Oriente` es la referencia metodologica de fondo y la fuente de los scores provisionales. En Barrio Obrero, `Entorno Urbano` puede recalcularse con proxy experimental de `deficit habitacional 2024` para `Comuna 9`. Hay datos contextuales adicionales en `data/referencia/` (Sub PyE 2025, RA2026) que aun no entran al calculo ITT.

## 12. Prompt sugerido para otro agente

Puedes iniciar a otro agente con este texto:

> Este repo calcula el ITT de zonas urbanas de Cali. La metodologia vigente exige `ref_min/ref_max` fijos por indicador y esta documentada en `agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md`. `notebooks/03_itt_barrio_obrero.ipynb` es la referencia operativa principal (DATIC 2023-2026 T1, datos en carpetas por dimension sin ZIP, Okabe-Ito, cividis, linea+relleno); `notebooks/01_itt_roosevelt.ipynb` ya esta alineado para 2023-2025; `notebooks/02_itt_avenida_ciudad_de_cali.ipynb` esta homologado con `ref_min/ref_max` fijos para 2023-2026 T1. Los referentes provisionales de Pulmon de Oriente son `Entorno Urbano = 39.2`, `Educacion y Desarrollo = 54.9` y `Vulnerabilidad = 54.1`. En Barrio Obrero `Entorno Urbano` puede sobrescribirse con proxy experimental de `deficit habitacional 2024` para `Comuna 9` (corte anual, no serie trimestral). En 2026 solo hay dato Q1 para DATIC — Q2/Q3/Q4 son `NaN` en `corr_trim`, y siniestros no tienen dato 2026. Distingue siempre entre datos reales, scores provisionales y metodologia vigente. No inventes outputs no versionados.
