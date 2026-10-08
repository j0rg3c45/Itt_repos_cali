# github_pages — Sitio estático público (ITT Ciudad Paraíso)

Sitio estático con los resultados del ITT de **Ciudad Paraíso** para publicar en GitHub Pages.
No corre Python en el servidor: son archivos HTML/JSON/PNG servidos tal cual.

**Sitio en vivo:** https://j0rg3c45.github.io/Itt_repos_cali/

## Qué muestra

- **Tablas** (DataTables): indicadores agregados por año/trimestre + scores del ITT. Búsqueda,
  orden, paginación, responsive. Celdas vacías se muestran como `—`.
- **Gráficos**: 12 figuras del notebook (ITT global, radar, heatmaps, series trimestrales,
  Entorno Urbano). Clic en una imagen la **amplía en un lightbox**.
- **Mapa** (Folium/Leaflet): polígono de la zona, red peatonal OSM (osmnx), nodos,
  mapa de calor de intersecciones, overlays NDVI 2023–2026, censo arbóreo y eventos por tipo.
- **Acerca de**: resumen del proyecto, metodología y nota de privacidad (dentro del propio sitio).

## Privacidad por diseño

**Tablas y gráficos:** solo datos **agregados** (conteos y scores). Sin registros individuales ni PII.

**Mapa:** cada evento (homicidio, hurto, VIF, riña, SPA, siniestro) se publica con **solo su
ubicación + tipo**. De cada registro se extrae únicamente la geometría (lat/lon) y se le asigna una
etiqueta de tipo fija; **nunca** se publican las `properties` del dato crudo (dirección exacta,
fecha, sexo, edad, nacionalidad, placas, antecedentes, feminicidio, etc.).

`audit_privacy.py` revisa el `mapa.html` generado y falla (exit 1) si encuentra atributos sensibles
o properties embebidas distintas de la geometría. El workflow lo ejecuta antes de desplegar, así un
cambio accidental que exponga datos **bloquea la publicación**.

## Estructura

```
github_pages/
├── build_site.py        # genera site/data.json (tablas) + galeria + index.html
├── build_map.py         # genera site/mapa.html (poligono, OSM, NDVI, eventos por tipo)
├── audit_privacy.py     # verifica que el mapa no filtre datos sensibles (bloquea deploy)
├── template/
│   └── index.html       # plantilla del sitio (pestañas Tablas/Graficos/Mapa/Acerca de)
├── charts/              # 12 PNG de graficos (versionados; los copia build_site)
└── site/                # SALIDA publicable (ignorada en git; la regenera el workflow)
    ├── index.html
    ├── data.json
    ├── mapa.html
    ├── .nojekyll
    └── assets/
```

## Generar el sitio localmente

Requiere el Excel consolidado (`outputs/itt_ciudad_paraiso/ITT_Ciudad_Paraiso_Consolidado.xlsx`),
generado por el notebook 08. Con el entorno `uv` del repo:

```bash
uv run python github_pages/build_site.py     # tablas + galeria + index.html  (corre PRIMERO)
uv run python github_pages/build_map.py      # mapa.html (ubicacion + tipo)
uv run python github_pages/audit_privacy.py  # verifica que no haya fuga de datos
# abrir github_pages/site/index.html (o: uv run python -m http.server --directory github_pages/site)
```

Orden importante: `build_site.py` limpia la carpeta `site/` (sin borrar `mapa.html` si ya existe),
luego `build_map.py` crea el mapa, y `audit_privacy.py` valida.

## Stack

- Tablas: DataTables + jQuery (CDN). Idioma español **inline** (sin fetch externo frágil).
- Gráficos: PNG de matplotlib/seaborn + lightbox en CSS/JS puro.
- Mapa: Folium/Leaflet + osmnx (red peatonal) + rasterio/PIL (overlays NDVI).

## Despliegue (GitHub Actions)

`.github/workflows/deploy-pages.yml` regenera y publica el sitio en Pages ante push a `master`
(que toque `github_pages/`, `outputs/itt_ciudad_paraiso/` o `data/Ciudad_Paraiso/`), o manualmente
desde la pestaña Actions. El workflow usa sparse-checkout de `data/Ciudad_Paraiso` completa y corre
la auditoría de privacidad antes de desplegar.

## Historial de construcción (resumen)

Este sitio y su mapa se construyeron en iteraciones, resolviendo en el camino:

1. **Dimensión 5 con datos propios** — Entorno Urbano pasó de un proxy de déficit habitacional al
   cálculo real con NDVI anual (2023–2026) + censo arbóreo.
2. **Mapa interactivo** — se añadieron 5 capas base, red peatonal OSM, nodos, heatmap de
   intersecciones, overlays NDVI y eventos por tipo.
3. **Privacidad del mapa** — los eventos se publican como ubicación + tipo únicamente; se añadió
   `audit_privacy.py` para garantizarlo en cada deploy.
4. **Correcciones del sitio** — `data.json` con `NaN` → `null` (era inválido para el navegador),
   i18n de DataTables inline, carga robusta con manejo de errores visible, y lightbox para ampliar
   gráficos.
5. **Despliegue** — se incluyó `data/Ciudad_Paraiso` completa en el sparse-checkout (faltaba la
   carpeta de VIF con tilde en el nombre, que dejaba el mapa con VIF en cero).
