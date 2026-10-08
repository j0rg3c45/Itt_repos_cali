# github_pages — Sitio estático público (ITT Ciudad Paraíso)

Sitio estático con los **resultados agregados** del ITT para publicar en GitHub Pages.
No corre Python en el servidor: son archivos HTML/JSON/PNG servidos tal cual.

## Privacidad por diseño

**Tablas y gráficos:** publican únicamente datos **agregados** (conteos anuales/trimestrales
y scores del ITT). No contienen registros individuales ni PII.

**Mapa:** muestra la **ubicación** de cada evento y su **tipo** (homicidio, hurto, VIF, riña,
SPA, siniestro) — y **nada más**. De cada registro se extrae solo la coordenada y una etiqueta
de tipo fija; **nunca** se publican los demás atributos del dato crudo (dirección exacta, fecha,
sexo, edad, nacionalidad, placas, antecedentes, feminicidio, etc.). Esto se garantiza en
`build_map.py` tomando solo la geometría del GeoJSON, nunca sus `properties`.

Hay un script de auditoría que verifica que el `mapa.html` publicado no filtre atributos
sensibles (ver sección "Auditoría" más abajo).

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
uv run python github_pages/build_site.py     # tablas + galeria + index.html
uv run python github_pages/build_map.py      # mapa.html (ubicacion + tipo)
uv run python github_pages/audit_privacy.py  # verifica que no haya fuga de datos
# abrir github_pages/site/index.html en el navegador
```

## Auditoría de privacidad

`audit_privacy.py` revisa el `mapa.html` generado y falla (exit 1) si encuentra
cualquier atributo sensible filtrado (dirección, fecha, sexo, edad, placas, etc.) o
properties embebidas distintas de la geometría. El workflow lo ejecuta antes de
desplegar, así un cambio accidental que exponga datos **bloquea la publicación**.

## Stack de visualización

- **Tablas:** DataTables (CDN) — búsqueda, orden, paginación, responsive.
- **Gráficos:** PNG de matplotlib/seaborn (galería responsive).
- **Mapa:** Folium/Leaflet (HTML autocontenido) con capas agregadas.

## Despliegue

El workflow `.github/workflows/deploy-pages.yml` regenera el sitio y lo publica en
GitHub Pages en cada push a `master` que toque datos/notebook, o manualmente desde la
pestaña Actions.
