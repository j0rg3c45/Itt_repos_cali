"""
Genera el MAPA SEGURO para el sitio público (github_pages/site/mapa.html).

Qué incluye:
  - Polígono real de la zona
  - Red peatonal OpenStreetMap (líneas)
  - Censo arbóreo (patrimonio ambiental público)
  - Overlays NDVI 2023-2026 (vegetación)
  - Puntos de eventos por tipo: Homicidio, Hurto, VIF, Siniestro, Riña, SPA

Criterio de privacidad (definido por el usuario): de cada evento se publica SOLO la
UBICACIÓN (punto) y el TIPO de delito. NUNCA se publican los demás atributos del
registro (dirección exacta, fecha, sexo, edad, nacionalidad, placas, antecedentes,
feminicidio, etc.). Esto se garantiza extrayendo únicamente la geometría del GeoJSON
y asignando una etiqueta de tipo fija — las `properties` crudas no llegan al HTML.

Uso:
    uv run python github_pages/build_map.py
"""
import io
import base64
import json
from pathlib import Path

import numpy as np
import geopandas as gpd
import folium
import matplotlib.cm as cm
import rasterio
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
SITE = HERE / "site"
D = ROOT / "data" / "Ciudad_Paraiso"

POLIGONO = D / "geojson_area_ciudad_Paraiso" / "poligono_ciudad_Paraiso.geojson"
CENSO = D / "5_Dimension_Entorno_Urbano" / "CENSO_ARBOREO_ciudad_Paraiso.geojson"
NDVI = {a: D / "5_Dimension_Entorno_Urbano" / "ciudad_Paraiso_ndvi" / f"ciudad_Paraiso_ndvi_{a}.tif"
        for a in [2023, 2024, 2025, 2026]}

# ─────────────────────────────────────────────────────────────────────────────
# CAPAS DE EVENTOS — se publican SOLO: ubicación (punto) + tipo de delito.
#
# REGLA DE PRIVACIDAD ESTRICTA: de cada registro se toma ÚNICAMENTE la geometría
# (lat/lon) y se le asigna una etiqueta de TIPO fija definida aquí. NUNCA se pasan
# las `properties` del GeoJSON crudo al mapa — esas columnas traen direccion exacta,
# sexo, edad, nacionalidad, placas, antecedentes, feminicidio, etc. (datos sensibles).
# El tooltip del punto muestra solo el tipo (p.ej. "Homicidio"), nada más.
# ─────────────────────────────────────────────────────────────────────────────
EVENTOS_PUNTOS = {
    # etiqueta_tipo : (archivo, color, filtro_opcional_por_propiedad)
    "Homicidio":  (D / "1_Dimension_Seguridad" / "DATIC_homicidios_2023_2026T1_poligono_ciudad_Paraiso.geojson", "darkred", None),
    "Hurto":      (D / "1_Dimension_Seguridad" / "DATIC_hurtos_2023_2026T1_poligono_ciudad_Paraiso.geojson", "purple", None),
    "VIF":        (D / "2_Dimensión_Cohesion_Social" / "DATIC_violencia_intrafamiliar_2023_2026T1_poligono_ciudad_Paraiso.geojson", "cadetblue", None),
    "Siniestro":  (D / "3_Dimension_Movilidad" / "BD_SINIESTROS_2023_2026_COMUNA_BARRIO_84_poligono_ciudad_Paraiso.geojson", "orange", None),
}
# Comparendos: se separan por categoria del campo 'agrupado' (solo riñas y SPA).
EVENTOS_COMPARENDOS = D / "1_Dimension_Seguridad" / "DATIC_comparendos_2023_2026T1_poligono_ciudad_Paraiso.geojson"


def coords_dentro(path, poly_wgs, filtro=None):
    """Devuelve SOLO [(lat, lon), ...] de los puntos dentro del poligono.
    Descarta por completo las properties (no se publican)."""
    if not path.exists():
        return []
    g = gpd.read_file(path).to_crs("EPSG:4326")
    g = g[g.geometry.geom_type == "Point"]
    if filtro is not None:
        g = g[filtro(g)]
    g = g[g.within(poly_wgs)]
    # Se extrae UNICAMENTE la coordenada: ninguna columna/atributo viaja al mapa.
    return [(geom.y, geom.x) for geom in g.geometry]


def main():
    SITE.mkdir(parents=True, exist_ok=True)

    gdf_zona = gpd.read_file(POLIGONO).to_crs("EPSG:4326")
    poly = gdf_zona.geometry.union_all()
    # centroide calculado en CRS proyectado (EPSG:3115) para evitar imprecision en grados
    centroid = gdf_zona.to_crs("EPSG:3115").geometry.centroid.to_crs("EPSG:4326").iloc[0]

    # OpenStreetMap como base por defecto (no requiere API key, a diferencia de CartoDB)
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=16, tiles="OpenStreetMap")
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Esri Satélite",
    ).add_to(m)

    # Poligono de la zona — se publica SOLO la geometria (sin properties Id/area)
    poligono_geom = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {}, "geometry": g.__geo_interface__}
        for g in gdf_zona.geometry
    ]}
    folium.GeoJson(
        poligono_geom, name="Polígono Ciudad Paraíso",
        style_function=lambda x: {"color": "#1B4F8A", "fillColor": "#2E7D32",
                                  "fillOpacity": 0.10, "weight": 2},
    ).add_to(m)

    # Red peatonal OSM (opcional: requiere internet). No sensible.
    try:
        import osmnx as ox
        G = ox.graph_from_polygon(poly, network_type="walk", simplify=False)
        nodes, edges = ox.graph_to_gdfs(G)
        edges = edges.to_crs("EPSG:4326")
        folium.GeoJson(
            edges[["geometry"]].__geo_interface__, name="Red peatonal OSM",
            style_function=lambda x: {"color": "#2A9C8A", "weight": 2, "opacity": 0.7},
        ).add_to(m)
        print(f"Red peatonal OSM: {len(edges)} tramos")
    except Exception as e:
        print(f"[AVISO] red peatonal OSM omitida ({type(e).__name__}). El mapa se genera igual.")

    # Censo arbóreo: es patrimonio ambiental público (árboles), no es PII -> se puede mostrar
    if CENSO.exists():
        arb = gpd.read_file(CENSO).to_crs("EPSG:4326")
        arb = arb[arb.within(poly)]
        fg_arb = folium.FeatureGroup(name="Censo arbóreo", show=False)
        for geom in arb.geometry:
            folium.CircleMarker([geom.y, geom.x], radius=3, color="green",
                                fill=True, fill_opacity=0.6, weight=1).add_to(fg_arb)
        fg_arb.add_to(m)

    # Overlays NDVI 2023-2026
    for ano, tif in NDVI.items():
        if not tif.exists():
            continue
        with rasterio.open(tif) as src:
            data = src.read(1).astype(float)
            b = src.bounds
            if src.nodata is not None:
                data[data == src.nodata] = np.nan
            data[data <= -9999] = np.nan
        norm = np.clip((data - (-0.1)) / (0.5 - (-0.1)), 0, 1)
        rgba = (cm.YlGn(norm) * 255).astype(np.uint8)
        if np.any(np.isnan(data)):
            rgba[np.isnan(data), 3] = 0
        buf = io.BytesIO()
        Image.fromarray(rgba).save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        folium.raster_layers.ImageOverlay(
            image=f"data:image/png;base64,{b64}",
            bounds=[[b.bottom, b.left], [b.top, b.right]],
            name=f"NDVI {ano}", opacity=0.65, show=False,
        ).add_to(m)

    # ── Capas de eventos: punto + tipo de delito, SIN ningun otro atributo ──────
    def capa_puntos(etiqueta, coords, color, show=False):
        fg = folium.FeatureGroup(name=f"{etiqueta} ({len(coords)})", show=show)
        for lat, lon in coords:
            folium.CircleMarker(
                [lat, lon], radius=4, color=color, fill=True,
                fill_color=color, fill_opacity=0.7, weight=1,
                tooltip=etiqueta,   # SOLO el tipo; sin fecha/direccion/datos del caso
            ).add_to(fg)
        fg.add_to(m)

    # Las capas de eventos arrancan VISIBLES para que el mapa no se vea vacio al abrir.
    total = 0
    for etiqueta, (path, color, filtro) in EVENTOS_PUNTOS.items():
        coords = coords_dentro(path, poly, filtro)
        capa_puntos(etiqueta, coords, color, show=True)
        total += len(coords)
        print(f"{etiqueta}: {len(coords)} puntos (solo ubicacion + tipo)")

    # Comparendos -> Riñas y SPA como capas de tipo separadas
    import pandas as pd
    if EVENTOS_COMPARENDOS.exists():
        gc = gpd.read_file(EVENTOS_COMPARENDOS).to_crs("EPSG:4326")
        gc = gc[gc.geometry.geom_type == "Point"]
        gc = gc[gc.within(poly)]
        agr = gc["agrupado"].astype(str)
        rinas = [(g.y, g.x) for g in gc[agr.str.startswith("RI")].geometry]
        spa   = [(g.y, g.x) for g in gc[agr == "SUSTANCIAS PSICOACTIVAS"].geometry]
        capa_puntos("Riña", rinas, "pink", show=True)
        capa_puntos("SPA (sustancias psicoactivas)", spa, "beige", show=True)
        total += len(rinas) + len(spa)
        print(f"Riña: {len(rinas)} | SPA: {len(spa)} puntos (solo ubicacion + tipo)")

    print(f"Total puntos publicados (solo ubicacion + tipo): {total}")

    folium.LayerControl(collapsed=False).add_to(m)
    out = SITE / "mapa.html"
    m.save(str(out))
    print(f"Mapa seguro generado -> {out}")


if __name__ == "__main__":
    main()
