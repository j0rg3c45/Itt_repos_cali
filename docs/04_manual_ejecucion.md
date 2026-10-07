# Manual de ejecucion

## 1. Preparar ambiente

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Librerias base del proyecto:

- `pandas`
- `numpy`
- `geopandas`
- `pyproj`
- `shapely`
- `matplotlib`
- `seaborn`
- `folium`
- `openpyxl`

## 2. Preparar datos

Ubicar los insumos de cada zona en:

```text
data/itt_roosevelt/
data/itt_avenida_ciudad_de_cali/
data/itt_barrio_obrero/
```

Notas practicas:

- Barrio Obrero: datos directamente en subcarpetas por dimension — no se requiere ZIP.
- Avenida Ciudad de Cali: 3 ZIPs versionados — `Geojson_Ciudad_de_Cali (1).zip`, `geojson_filtrado_ciudad_de_Cali_100m.zip`, `geojson_Movilidad_ciudad_de_Cali_100m.zip`.
- Roosevelt: `Roosevelt.zip` presente y carpeta descomprimida de trabajo en `data/itt_roosevelt/Roosevelt_unzipped/`.

## 3. Ejecutar notebooks por zona

Orden sugerido:

```text
notebooks/01_itt_roosevelt.ipynb
notebooks/02_itt_avenida_ciudad_de_cali.ipynb
notebooks/03_itt_barrio_obrero.ipynb
```

Estado recomendado de uso:

- `01_itt_roosevelt.ipynb`: implementado y alineado con la estructura de Barrio Obrero.
- `02_itt_avenida_ciudad_de_cali.ipynb`: implementado y actualizado — ref_min/ref_max fijos, 3 ZIPs, heatmaps por tramo con orden geografico norte→sur.
- `03_itt_barrio_obrero.ipynb`: referencia actual de implementacion para zonas tipo barrio/poligono unico.

Nota operativa para Roosevelt:

- Mantener la convencion `año` en las tablas del notebook para evitar inconsistencias entre celdas.
- Si se ejecuta en Colab despues de cambios locales, conviene reiniciar entorno y correr desde la celda que construye `base`.

Nota operativa para Avenida Ciudad de Cali:

- En Colab, la celda de git clone tiene logica git pull si el repo ya existe (evita error de directorio existente).
- Cell 3A extrae los 3 ZIPs: ZIP1 y ZIP2 a `/content/`, ZIP3 a `/content/movilidad_acc/` (carpeta separada para evitar colision).
- Cell 3 verifica que todos los PATHS existan con check/cross visual antes de continuar.
- Los heatmaps por tramo usan `gdf_tramos['tramo'].astype(int)` para orden geografico norte→sur (T1=norte, T8=sur).
- 2026: solo T1 disponible. Movilidad se deja NaN (no proxy); ITT redistribuye el peso del 25% entre las 4 dimensiones restantes.

Nota operativa para Barrio Obrero:

- No se extrae ZIP — todos los GeoJSON estan directamente en subcarpetas por dimension dentro del repo.
- En Colab: `git clone https://github.com/j0rg3c45/Itt_repos_cali.git /content/itt_repos_cali` (o `git pull` si ya existe).
- Ruta base: `DATA_DIR = Path("/content/itt_repos_cali/data/itt_barrio_obrero")`.
- Celda 8 (git clone/pull) incluye verificacion visual de carpetas disponibles.
- Celda 10 define PATHS con rutas a dimension folders, REFS, PESOS, REF_ENTORNO_U, REF_EDUC_DES, REF_VULNERABILIDAD.
- Campo fecha homicidios: `fechah` formato `MM/DD/YYYY` — usar `formato_fecha="%m/%d/%Y"` en `procesar()`. Resto de DATIC: `fecha_hech` ISO.
- 2026: DATIC cubre hasta Q1. Celda 22 aplica mascara NaN para Q2/Q3/Q4 en DATIC y todo 2026 en siniestros.
- Visualizaciones: paleta Okabe-Ito, heatmaps cividis por dimension, graficas trimestrales linea+relleno.
- El notebook incluye Celda 3B para recalcular `Entorno Urbano` con proxy de `deficit habitacional` (Comuna 9, corte 2024).

## 4. Criterio metodologico

Metodo vigente:

- Usar `ref_min/ref_max` fijos por indicador.
- Mantener como provisionales las dimensiones con referentes de Pulmon de Oriente.
- No usar min-max relativo para la muestra de una zona pequena.
- En Barrio Obrero, `Entorno Urbano` puede sobrescribir el referente fijo con un proxy experimental de `Comuna 9` usando `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx`.
- Ese proxy de `Entorno Urbano` es anual `2024`; no debe presentarse como serie mensual o trimestral observada.

Referencia principal:

```text
agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md
```

## 5. Exportar resultados

Cada notebook debe exportar sus salidas a:

```text
outputs/itt_roosevelt/
outputs/itt_avenida_ciudad_de_cali/
outputs/itt_barrio_obrero/
```

Hoy el repo no contiene outputs generados; solo la estructura base.

## 6. Ejecutar comparativo

Luego ejecutar:

```text
notebooks/05_comparativo_itt_zonas.ipynb
```

Condicion para que tenga sentido:

- Deben existir resultados homologos de las zonas a comparar.

Las salidas consolidadas van en:

```text
outputs/consolidado/
```

## 7. Alimentar agentes

Actualizar estas carpetas despues de cambios metodologicos o nuevos resultados:

```text
agent/context/
agent/knowledge_base/
```

Minimo recomendado para agentes:

- Contexto del proyecto.
- Estado de notebooks y zonas.
- Metodologia vigente.
- Fuentes disponibles y faltantes.
- Resultados exportados.
