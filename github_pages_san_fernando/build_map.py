"""
Genera el MAPA SEGURO para el sitio público de San Fernando
(github_pages_san_fernando/site/mapa.html).

Qué incluye:
  - Polígono real de la zona + 3 subzonas internas + punto focal Yawa
  - Red peatonal OpenStreetMap (líneas) + nodos + heatmap de intersecciones
  - Censo arbóreo (patrimonio ambiental público) + overlays NDVI 2023-2026
  - Puntos de eventos por tipo: Homicidio, Hurto, Siniestro, Riña, SPA
  - VIF y VBG: SOLO MAPA DE CALOR (nunca puntos) — en una zona pequeña un punto
    de violencia intrafamiliar/de género podría permitir re-identificar a la víctima.
    El heatmap difumina la ubicación: muestra concentración sin exponer casos.

Criterio de privacidad (definido por el usuario): de cada evento se publica SOLO la
UBICACIÓN y el TIPO. NUNCA las properties crudas (dirección, fecha, sexo, edad,
nacionalidad, placas, antecedentes, feminicidio, etc.). VIF/VBG ni siquiera como punto.

Uso:
    uv run python github_pages_san_fernando/build_map.py
"""
import io
import base64
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
D = ROOT / "data" / "itt_Corredor_San_fernando_Yawa"

POLIGONO = D / "geojson_Corredor_San_fernando.geojson"
SUBZONAS = {
    "Subzona 1": D / "Corredor_San_fernando_zona_01.geojson",
    "Subzona 2": D / "Corredor_San_fernando_zona_02.geojson",
    "Subzona 3": D / "Corredor_San_fernando_zona_03.geojson",
}
YAWA = D / "yawa.geojson"
CENSO = D / "5_Dimension_Entorno_Urbano" / "geojson_filtrado" / "CENSO_ARBOREO_filtrado.geojson"
NDVI = {a: D / "5_Dimension_Entorno_Urbano" / "NDVI_Corredor_San_fernando_Yawa" / f"Corredor_San_fernando_Yawa_ndvi_{a}.tif"
        for a in [2023, 2024, 2025, 2026]}

# ── Eventos como PUNTOS (ubicación + tipo). Base + extensión 2026 por fuente. ──
EVENTOS_PUNTOS = {
    "Homicidio": ([D / "1_Dimension_Seguridad" / "DATIC_homicidios_2023_2026T1.geojson",
                   D / "1_Dimension_Seguridad" / "DATIC_homicidios_04012026_26092026.geojson"], "darkred"),
    "Hurto":     ([D / "1_Dimension_Seguridad" / "DATIC_hurtos_2023_2026T1.geojson",
                   D / "1_Dimension_Seguridad" / "DATIC_hurtos_04012026_09302026.geojson"], "purple"),
    "Siniestro": ([D / "3_Dimension_Movilidad" / "BD_SINIESTROS_2023_2026_COMUNA_BARRIO.geojson",
                   D / "3_Dimension_Movilidad" / "BD_SINIESTROS_ABRIL_JUNIO_2026_COMUNA_BARRIO.geojson"], "orange"),
}
COMPARENDOS = [D / "1_Dimension_Seguridad" / "DATIC_comparendos_2023_2026T1.geojson",
               D / "1_Dimension_Seguridad" / "DATIC_comparendos_04012026_09302026.geojson"]
# ── Eventos SOLO HEATMAP (sensibles, nunca puntos): VIF (y VBG si existe) ──
VIF_FILES = [D / "2_Dimension_Cohesion_Social" / "DATIC_violencia_intrafamiliar_2023_2026T1.geojson",
             D / "2_Dimension_Cohesion_Social" / "DATIC_violencia_intrafamiliar_04012026_09302026.geojson"]
VBG_FILES = [D / "2_Dimension_Cohesion_Social" / "VBG_2025.geojson"]  # si existe


def coords_dentro(paths, poly_wgs, filtro=None):
    """[(lat, lon), ...] de puntos dentro del polígono. Descarta TODAS las properties."""
    out = []
    for path in paths:
        if not path.exists():
            print(f"[AVISO] fuente no encontrada: {path.name} -> 0 puntos")
            continue
        g = gpd.read_file(path).to_crs("EPSG:4326")
        g = g[g.geometry.geom_type == "Point"]
        if filtro is not None:
            g = g[filtro(g)]
        g = g[g.within(poly_wgs)]
        out.extend((geom.y, geom.x) for geom in g.geometry)   # SOLO geometría
    return out


def main():
    SITE.mkdir(parents=True, exist_ok=True)

    gdf_zona = gpd.read_file(POLIGONO).to_crs("EPSG:4326")
    poly = gdf_zona.geometry.union_all()
    centroid = gdf_zona.to_crs("EPSG:3115").geometry.centroid.to_crs("EPSG:4326").iloc[0]

    # Capas base alternables. OpenStreetMap por defecto (no requiere API key).
    # CartoDB se omite a propósito: ahora exige API key y saldría en blanco en el sitio público.
    m = folium.Map(location=[centroid.y, centroid.x], zoom_start=15, tiles=None)
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap").add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Esri Satélite",
    ).add_to(m)
    folium.TileLayer(
        tiles="http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google", name="Google Streets", subdomains=["mt0", "mt1", "mt2", "mt3"],
    ).add_to(m)
    folium.TileLayer(
        tiles="http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google", name="Google Satélite", subdomains=["mt0", "mt1", "mt2", "mt3"],
    ).add_to(m)

    # Polígono — solo geometría (sin properties)
    poligono_geom = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {}, "geometry": g.__geo_interface__} for g in gdf_zona.geometry
    ]}
    folium.GeoJson(poligono_geom, name="Polígono Corredor San Fernando",
                   style_function=lambda x: {"color": "#1B4F8A", "weight": 2.5, "fill": False}).add_to(m)

    # Subzonas (contorno de color) — solo geometría
    _cols = {"Subzona 1": "#E65100", "Subzona 2": "#2E7D32", "Subzona 3": "#6A1B9A"}
    for nz, pz in SUBZONAS.items():
        if not pz.exists():
            continue
        gz = gpd.read_file(pz).to_crs("EPSG:4326")
        geom = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {}, "geometry": g.__geo_interface__} for g in gz.geometry]}
        col = _cols.get(nz, "#555")
        folium.GeoJson(geom, name=nz, show=False,
                       style_function=lambda x, c=col: {"color": c, "weight": 2, "dashArray": "6,4",
                                                        "fill": True, "fillColor": c, "fillOpacity": 0.06}).add_to(m)
    if YAWA.exists():
        gy = gpd.read_file(YAWA).to_crs("EPSG:4326")
        geom = {"type": "FeatureCollection", "features": [
            {"type": "Feature", "properties": {}, "geometry": g.__geo_interface__} for g in gy.geometry]}
        folium.GeoJson(geom, name="Yawa (punto focal)", show=True,   # única capa activa al abrir
                       style_function=lambda x: {"color": "#C62828", "weight": 3,
                                                "fill": True, "fillColor": "#EF9A9A", "fillOpacity": 0.2}).add_to(m)

    # Red peatonal OSM (opcional: requiere internet)
    try:
        import osmnx as ox
        G = ox.graph_from_polygon(poly, network_type="walk", simplify=False)
        nodes, edges = ox.graph_to_gdfs(G)
        edges = edges.to_crs("EPSG:4326")
        nodes = nodes.to_crs("EPSG:4326")
        folium.GeoJson(edges[["geometry"]].__geo_interface__, name="Red peatonal OSM", show=False,
                       style_function=lambda x: {"color": "#2A9C8A", "weight": 2, "opacity": 0.7}).add_to(m)
        # Nodos / intersecciones (apagado por defecto)
        fg_nodos = folium.FeatureGroup(name="Nodos (intersecciones)", show=False)
        for g in nodes.geometry:
            folium.CircleMarker([g.y, g.x], radius=3, color="#E53935",
                                fill=True, fill_opacity=0.9, weight=1).add_to(fg_nodos)
        fg_nodos.add_to(m)
        # Heatmap de intersecciones reales (street_count > 2), apagado
        if "street_count" in nodes.columns:
            inter = nodes[nodes["street_count"] > 2]
        else:
            inter = nodes
        heat_inter = [[g.y, g.x] for g in inter.geometry]
        fg_heat = folium.FeatureGroup(name="Mapa de calor — intersecciones", show=False)
        HeatMap(heat_inter, radius=18, blur=15, min_opacity=0.3).add_to(fg_heat)
        fg_heat.add_to(m)
        print(f"Red peatonal OSM: {len(edges)} tramos | {len(nodes)} nodos | {len(heat_inter)} intersecciones")
    except Exception as e:
        print(f"[AVISO] red peatonal OSM omitida ({type(e).__name__}). El mapa se genera igual.")

    # Censo arbóreo (patrimonio ambiental público, no PII)
    if CENSO.exists():
        arb = gpd.read_file(CENSO).to_crs("EPSG:4326")
        arb = arb[arb.within(poly)]
        fg_arb = folium.FeatureGroup(name=f"Censo arbóreo ({len(arb)})", show=False)
        for g in arb.geometry:
            folium.CircleMarker([g.y, g.x], radius=2.5, color="green", fill=True,
                                fill_opacity=0.6, weight=1).add_to(fg_arb)
        fg_arb.add_to(m)

    # Overlays NDVI
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
            name=f"NDVI {ano}", opacity=0.65, show=False).add_to(m)

    # ── Eventos como PUNTOS: ubicación + tipo únicamente ──
    def capa_puntos(etiqueta, coords, color, show=True):
        fg = folium.FeatureGroup(name=f"{etiqueta} ({len(coords)})", show=show)
        for lat, lon in coords:
            folium.CircleMarker([lat, lon], radius=4, color=color, fill=True,
                                fill_color=color, fill_opacity=0.7, weight=1,
                                tooltip=etiqueta).add_to(fg)
        fg.add_to(m)

    # Todas las capas de eventos arrancan APAGADAS: al abrir solo se ve el Polígono + Yawa.
    total_pts = 0
    for etiqueta, (paths, color) in EVENTOS_PUNTOS.items():
        coords = coords_dentro(paths, poly)
        capa_puntos(etiqueta, coords, color, show=False)
        total_pts += len(coords)
        print(f"{etiqueta}: {len(coords)} puntos")

    # Comparendos -> Riña y SPA (puntos)
    rinas = coords_dentro(COMPARENDOS, poly,
                          filtro=lambda g: g["agrupado"].astype(str).str.startswith("RI"))
    spa = coords_dentro(COMPARENDOS, poly,
                        filtro=lambda g: g["agrupado"].astype(str) == "SUSTANCIAS PSICOACTIVAS")
    capa_puntos("Riña", rinas, "pink", show=False)
    capa_puntos("SPA (sustancias psicoactivas)", spa, "beige", show=False)
    total_pts += len(rinas) + len(spa)
    print(f"Riña: {len(rinas)} | SPA: {len(spa)} puntos")

    # ── VIF y VBG: SOLO MAPA DE CALOR (nunca puntos) — protección de víctimas ──
    def heat_coords(paths):
        return coords_dentro(paths, poly)

    vif = heat_coords(VIF_FILES)
    if vif:
        fg = folium.FeatureGroup(name=f"VIF — mapa de calor ({len(vif)})", show=False)
        HeatMap([[la, lo] for la, lo in vif], radius=22, blur=18, min_opacity=0.35).add_to(fg)
        fg.add_to(m)
        print(f"VIF: {len(vif)} eventos -> HEATMAP (sin puntos)")
    vbg = heat_coords(VBG_FILES)
    if vbg:
        fg = folium.FeatureGroup(name=f"VBG — mapa de calor ({len(vbg)})", show=False)
        HeatMap([[la, lo] for la, lo in vbg], radius=22, blur=18, min_opacity=0.35).add_to(fg)
        fg.add_to(m)
        print(f"VBG: {len(vbg)} eventos -> HEATMAP (sin puntos)")

    print(f"Total puntos publicados (ubicacion + tipo): {total_pts} | VIF/VBG solo heatmap")

    folium.LayerControl(collapsed=True).add_to(m)
    out = SITE / "mapa.html"
    m.save(str(out))
    print(f"Mapa seguro generado -> {out}")


if __name__ == "__main__":
    main()
