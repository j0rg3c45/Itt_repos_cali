# github_pages_san_fernando — Sitio estático público (ITT Corredor San Fernando / Yawa)

Sitio estático con los resultados del ITT del **Corredor San Fernando (Yawa)**, Comuna 19 de Cali,
para publicar en GitHub Pages. No corre Python en el servidor: son archivos HTML/JSON/PNG.

**Sitio en vivo:** https://j0rg3c45.github.io/Itt_repos_cali/san-fernando/
(Ciudad Paraíso sigue en la raíz: https://j0rg3c45.github.io/Itt_repos_cali/)

## Qué muestra

- **Tablas** (DataTables): indicadores agregados por año/trimestre + scores del ITT + comparación por
  subzonas. Celdas vacías se muestran como `—`.
- **Gráficos**: 13 figuras del notebook 09 (ITT global, radar, heatmaps, series trimestrales, Entorno
  Urbano, comparación por subzonas). Clic en una imagen la amplía en un lightbox.
- **Mapa** (Folium/Leaflet): polígono + 3 subzonas + punto focal Yawa, red peatonal OSM, censo arbóreo,
  overlays NDVI 2023-2026 y eventos por tipo.

## Privacidad por diseño

**Tablas y gráficos:** solo datos **agregados** (conteos y scores). NO se publican hojas con detalle por
entidad (colegio, barrios de vivienda, negocios individuales).

**Mapa:**
- Homicidio, Hurto, Siniestro, Riña, SPA → **punto + tipo** únicamente (se extrae solo la geometría; nunca
  las `properties` crudas: dirección, fecha, sexo, edad, placas, etc.).
- **VIF (violencia intrafamiliar) y VBG (violencia de género) → SOLO mapa de calor, nunca puntos.** En una
  zona pequeña, un punto individual de VIF/VBG podría permitir re-identificar a la víctima; el heatmap
  difumina la ubicación y muestra la concentración sin exponer casos.

`audit_privacy.py` revisa el `mapa.html` generado y **falla (exit 1)** si encuentra atributos sensibles,
properties embebidas, o VIF/VBG como punto. El workflow lo ejecuta antes de desplegar: un cambio accidental
que exponga datos **bloquea la publicación**.

## Estructura

```
github_pages_san_fernando/
├── build_site.py     # genera site/data.json (tablas) + galería + index.html
├── build_map.py      # genera site/mapa.html (polígono, subzonas, OSM, NDVI, eventos; VIF/VBG heatmap)
├── audit_privacy.py  # verifica que el mapa no filtre datos y que VIF/VBG no sean puntos
├── template/
│   └── index.html    # plantilla del sitio
├── charts/           # 13 PNG de gráficos (versionados; los copia build_site)
└── site/             # SALIDA publicable (ignorada en git; la regenera el workflow)
```

## Generar el sitio localmente

Requiere el Excel consolidado (`outputs/itt_corredor_san_fernando/ITT_Corredor_San_Fernando_Consolidado.xlsx`),
generado por el notebook 09. Con el entorno `uv` del repo:

```bash
uv run python github_pages_san_fernando/build_site.py     # tablas + galería + index.html (PRIMERO)
uv run python github_pages_san_fernando/build_map.py      # mapa.html (eventos + VIF/VBG heatmap)
uv run python github_pages_san_fernando/audit_privacy.py  # verifica que no haya fuga de datos
```

## Despliegue (GitHub Actions)

`.github/workflows/deploy-pages.yml` construye AMBOS sitios (Ciudad Paraíso en la raíz, San Fernando en
`/san-fernando/`), corre las dos auditorías de privacidad y publica un único artefacto en Pages ante push
a `master` que toque los datos/salidas/scripts de cualquiera de las dos zonas.
