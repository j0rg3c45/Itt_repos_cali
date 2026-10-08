# github_pages — Sitio estático público (ITT Ciudad Paraíso)

Sitio estático con los **resultados agregados** del ITT para publicar en GitHub Pages.
No corre Python en el servidor: son archivos HTML/JSON/PNG servidos tal cual.

## Privacidad por diseño

Este sitio publica **únicamente datos agregados** (conteos anuales/trimestrales y
scores del Índice de Transformación Territorial). **No** incluye:

- Registros individuales ni PII (nombres, cédulas, direcciones).
- Coordenadas exactas de casos de seguridad o violencia (homicidios, hurtos, VIF, riñas, SPA).

Los eventos de seguridad se representan en el mapa **solo como densidad agregada**
(heatmap difuminado), que no permite ubicar un caso concreto. El censo arbóreo sí se
muestra por ser patrimonio ambiental público (no es dato personal).

## Estructura

```
github_pages/
├── build_site.py        # genera site/data.json + copia graficos + index.html
├── build_map.py         # genera site/mapa.html (mapa seguro, solo agregados)
├── template/
│   └── index.html       # plantilla del sitio (tablas DataTables + galeria + mapa)
└── site/                # SALIDA publicable (se regenera; no editar a mano)
    ├── index.html
    ├── data.json        # tablas agregadas
    ├── mapa.html        # mapa folium (polígono + OSM + NDVI + heatmap densidad)
    ├── .nojekyll
    └── assets/          # PNG de graficos
```

## Generar el sitio localmente

```bash
# requiere el Excel consolidado generado por el notebook 08
uv run python github_pages/build_site.py
uv run python github_pages/build_map.py
# abrir github_pages/site/index.html en el navegador
```

## Stack de visualización

- **Tablas:** DataTables (CDN) — búsqueda, orden, paginación, responsive.
- **Gráficos:** PNG de matplotlib/seaborn (galería responsive).
- **Mapa:** Folium/Leaflet (HTML autocontenido) con capas agregadas.

## Despliegue

El workflow `.github/workflows/deploy-pages.yml` regenera el sitio y lo publica en
GitHub Pages en cada push a `master` que toque datos/notebook, o manualmente desde la
pestaña Actions.
