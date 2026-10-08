"""
Genera el MAPA SEGURO para el sitio público (github_pages/site/mapa.html).

Qué incluye (todo agregado / no sensible):
  - Polígono real de la zona
  - Red peatonal OpenStreetMap (líneas) + intersecciones
  - Overlays NDVI 2023-2026 (vegetación)
  - Mapa de calor de DENSIDAD de eventos agregados (sin marcadores por caso)

Qué NO incluye (privacidad por diseño):
  - NINGÚN marcador individual de homicidios, hurtos, VIF, riñas, SPA ni siniestros
  - NINGÚN popup con fecha/dato de caso
Los eventos de seguridad/violencia solo se representan como densidad difuminada
(heatmap), que no permite ubicar un caso concreto.

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
from folium.plugins import HeatMap
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

# Fuentes de eventos: SOLO se usan para construir el heatmap de densidad agregada.
# Nunca se publican sus puntos como marcadores individuales.
EVENTOS_DENSIDAD = {
    "Hurtos":     D / "1_Dimension_Seguridad" / "DATIC_hurtos_2023_2026T1_poligono_ciudad_Paraiso.geojson",
    "Siniestros": D / "3_Dimension_Movilidad" / "BD_SINIESTROS_2023_2026_COMUNA_BARRIO_84_poligono_ciudad_Paraiso.geojson",
}


def puntos_dentro(path, poly_wgs):
    """Devuelve [[lat, lon], ...] de los puntos de una fuente, recortados al poligono.
    Se usa SOLO para densidad agregada (heatmap), nunca como marcadores."""
    if not path.exists():
        return []
    g = gpd.read_file(path).to_crs("EPSG:4326")
    g = g[g.geometry.geom_type == "Point"]
    dentro = g[g.within(poly_wgs)]
    return [[geom.y, geom.x] for geom in dentro.geometry]


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

    # Poligono de la zona
    folium.GeoJson(
        gdf_zona.__geo_interface__, name="Polígono Ciudad Paraíso",
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

    # Heatmap de DENSIDAD agregada de eventos (sin marcadores individuales)
    heat = []
    for nombre, path in EVENTOS_DENSIDAD.items():
        pts = puntos_dentro(path, poly)
        heat.extend(pts)
        print(f"Densidad {nombre}: {len(pts)} puntos agregados al heatmap")
    if heat:
        fg_heat = folium.FeatureGroup(name="Densidad de eventos (agregado)", show=True)
        HeatMap(heat, radius=22, blur=18, min_opacity=0.3).add_to(fg_heat)
        fg_heat.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    out = SITE / "mapa.html"
    m.save(str(out))
    print(f"Mapa seguro generado -> {out}")


if __name__ == "__main__":
    main()
