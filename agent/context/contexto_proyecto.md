# Contexto para agente - Proyecto ITT

Este agente apoya consulta, interpretacion y explicacion del **Indice de Transformacion Territorial (ITT)** dentro del repositorio `itt-transformacion-territorial`.

## Objetivo del proyecto

Calcular el ITT para zonas de intervencion urbana en Cali y comparar resultados entre zonas.

## Zonas del repo

- ITT Roosevelt.
- Avenida Ciudad de Cali.
- Barrio Obrero.
- Ciudad Paraíso (Comuna 3) — proyecto de renovación urbana (San Pascual, El Calvario, San Juan Bosco, Santa Rosa). Área del polígono: 33.70 ha (337,039.2 m²).
- Pulmón de Oriente (seguimiento parcial).

## Repositorio y despliegue

- Repo GitHub: `https://github.com/j0rg3c45/Itt_repos_cali` (rama `master`). Los notebooks clonan este repo en Colab.
- Entorno local reproducible con `uv` (`.venv` + `requirements.txt`). Dependencias clave: geopandas, rasterio, folium, osmnx, pillow, matplotlib, seaborn, openpyxl.
- **Sitio público (GitHub Pages):** `https://j0rg3c45.github.io/Itt_repos_cali/` — publica resultados de Ciudad Paraíso (tablas + gráficos + mapa). Generado por `github_pages/` y desplegado con GitHub Actions.

## Estado actual

- `01_itt_roosevelt.ipynb`: implementado con estructura homologada a Barrio Obrero y `ref_min/ref_max` fijos. Periodo 2023-2025.
- `02_itt_avenida_ciudad_de_cali.ipynb`: implementado y actualizado — `ref_min/ref_max` fijos, 3 ZIPs, heatmaps por tramo con orden geografico norte→sur, paleta Okabe-Ito. Periodo 2023-2026 T1.
- `03_itt_barrio_obrero.ipynb`: implementado y actualizado — DATIC 2023-2026 T1, datos directamente en carpetas por dimension (sin ZIP), paleta Okabe-Ito, heatmaps cividis, graficas trimestrales linea+relleno, NaN enmascarado para 2026 Q2-Q4.
- `04_itt_pulmon_oriente_2026.ipynb`: salida parcial de seguimiento.
- `04_itt_barrio_obrero_5dim.ipynb` / `05_itt_roosevelt_5dim.ipynb` / `06_itt_avenida_ciudad_de_cali_5dim.ipynb`: versiones de 5 dimensiones.
- `05_comparativo_itt_zonas.ipynb`: plantilla comparativa.
- `08_itt_ciudad_paraiso_5dim.ipynb`: implementado y verificado (local + Colab). Periodo 2023-2026 (2026 parcial). 5 dimensiones. **Entorno Urbano calculado con datos propios** (NDVI anual 2023-2026 + censo arbóreo), NO con el proxy de déficit habitacional. Incluye mapa interactivo multicapa (5 bases, red peatonal OSM/osmnx, nodos, heatmap de intersecciones, overlays NDVI, eventos por tipo).

## Regla metodologica para agentes

La referencia metodologica vigente del proyecto esta en:

- `agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md`

Los agentes deben asumir como correcto:

- Uso de `ref_min/ref_max` fijos.
- Referentes provisionales para dimensiones sin datos propios.
- Necesidad de escalar refs segun tamano de zona.

Los agentes no deben asumir como vigente:

- Min-max relativo como metodo recomendado general.

## Uso esperado por el agente

El agente debe diferenciar entre:

- Metodologia vigente.
- Implementacion ya migrada.
- Implementacion pendiente de migrar.
- Datos presentes en el repo.
- Datos esperados pero no versionados.

## Seguimiento reciente

- Roosevelt ya dispone de datos fuente en `data/itt_roosevelt/`.
- Se revisaron errores de consistencia por `ano` y `año`; la convencion vigente en Roosevelt es `año`.
- Barrio Obrero migrado de ZIP a estructura de carpetas por dimension — archivos DATIC actualizados a 2023-2026 T1.
- Paleta Okabe-Ito y heatmaps cividis aplicados en notebooks 02 y 03.
- Graficas trimestrales cambiadas de barras agrupadas a linea+relleno con NaN para periodos sin datos.
- `data/referencia/` contiene ademas `Caracterizacion Personas Sub PyE (2025).xlsx` (24.087 registros, Secretaria de Bienestar Social) y `Caracterizacion R.A. 2026 corte may-6.xlsx`. Indicador contextual derivado: concentracion de vulnerabilidad activa = 54.1 por 1.000 hab — solo contexto, no implementado en ITT aun.
- `03_itt_barrio_obrero.ipynb` ya usa experimentalmente `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx` para recalcular `Entorno Urbano` con `Comuna 9` como proxy territorial.
- Ese insumo de `Entorno Urbano` es un corte anual `2024`; la visualizacion recomendada es un `heatmap` de componentes del deficit cualitativo.

## Seguimiento sesión 2026-10-08 (Ciudad Paraíso + sitio público)

**Dimensión 5 (Entorno Urbano) con datos propios de Ciudad Paraíso:**
- Se agregó `data/Ciudad_Paraiso/5_Dimension_Entorno_Urbano/`: censo arbóreo (312 árboles, 303 vivos/nuevos usados) + serie NDVI anual 2023-2026 (4 rásters).
- Se reemplazó el proxy de déficit habitacional por el cálculo real: `score_entorno_u = mean(score_ndvi, score_arbolado)`, mismo método que Av. Ciudad de Cali. El NDVI aporta la señal temporal (el censo es corte único). Score EU por año ≈ 51 → 65 → 65 → 55.
- ITT resultante: 2023=44.1, 2024=55.5, 2025=58.5 (Consolidación), 2026=81.4 (marcado "Parcial — no comparable").

**Migración de repositorio:**
- El repo se migró de `Pabandres85/itt_repos_cali` a `j0rg3c45/Itt_repos_cali`. Todas las URLs de clonado en los 8 notebooks + `tools/build_acc_educacion.ps1` + `docs/04_manual_ejecucion.md` apuntan ahora al repo nuevo.
- Celda 1B del notebook 08 usa clone superficial + sparse-checkout (descarga ~12 MB en vez de ~250 MB) y es robusta ante force-push (reset --hard / re-clone).

**Fixes de ejecución del notebook 08:**
- Celda 1: instala rasterio, osmnx y pillow (Colab no los trae).
- Celda 3B autosuficiente (carga `gdf_zona_wgs` si falta).
- Celda 7: el loop de scores excluye ndvi/arbolado (se calculan tras el merge de df_entorno).
- Kernel corregido a Python 3 (se había corrompido a Julia al guardar).
- Área del polígono documentada en cabecera y Celda 4 (ha / m² / km²).

**Sitio público estático (`github_pages/`):**
- `build_site.py` genera `site/data.json` (tablas agregadas del Excel) + galería de gráficos + `index.html` (pestañas Tablas/Gráficos/Mapa con DataTables).
- `build_map.py` genera `site/mapa.html` (folium): polígono, red peatonal OSM, nodos, heatmap de intersecciones, overlays NDVI, censo arbóreo y eventos por tipo.
- **Privacidad por diseño:** tablas/gráficos solo agregados. En el mapa, los eventos (homicidio, hurto, VIF, riña, SPA, siniestro) muestran SOLO ubicación + tipo — nunca otros atributos del dato crudo (dirección, fecha, sexo, edad, placas, etc.). Se extrae solo la geometría, nunca las `properties`.
- `audit_privacy.py` verifica que `mapa.html` no filtre atributos sensibles; corre en el workflow y bloquea el deploy si detecta fuga.
- Workflow `.github/workflows/deploy-pages.yml`: regenera y despliega en Pages ante push a `master` (paths github_pages/outputs/data) o manual. Sparse-checkout incluye `data/Ciudad_Paraiso` completa.
- Bug resuelto: `data.json` tenía NaN literales (datos faltantes 2026) → inválido para el navegador. Se corrigió con NaN→null y `json.dumps(allow_nan=False)`.
- `.gitignore` ignora `github_pages/site/`, `cache/` (osmnx), PNG de la raíz, `_*.py` y `.venv/`.

**Ajustes de UI/UX posteriores (misma sesión):**
- Gráficos del sitio con **lightbox**: clic en una imagen la amplía sobre fondo oscuro (cierra con clic fuera, × o Escape).
- Pestaña **"Acerca de"** en el sitio: resumen del proyecto, 5 dimensiones, metodología y nota de privacidad (visible en el propio GitHub Pages, no solo en el repo). README de `github_pages/` ampliado con el historial de construcción.
- Títulos de los 12 gráficos tomados de los `suptitle` del notebook.
- Error del sitio resuelto: DataTables usaba `language.url` (fetch externo frágil) → se pasó a i18n **inline**; carga robusta con `DOMContentLoaded`, manejo de errores visible y celdas vacías como "—".
- Bug VIF: el sparse-checkout omitía `2_Dimensión_Cohesion_Social` (tilde) → mapa mostraba VIF(0). Se incluyó `data/Ciudad_Paraiso` completa.
- Capas de eventos del mapa arrancan **visibles** (antes `show=False` dejaba el mapa vacío al abrir).
- **Control de capas colapsable** (`LayerControl(collapsed=True)`): arranca como icono de capas y se despliega al tocarlo (notebook 08 y sitio).
- Celda 1B: se reemplazaron los magics `!...{expr}` por `subprocess`/`shutil` — Colab no interpola `{' '.join(...)}` en una línea magic (daba `SyntaxError: invalid syntax (cell 2, line 21)`).
- **Polígono de la zona: solo contorno, sin relleno** (`fill=False`) en el mapa — notebook 08 y sitio.
