# -*- coding: utf-8 -*-
"""
ETL centralizado ITT — extractor de dimensiones por polígono (Geofencing On-the-Fly).

Modelo Data Lakehouse: la data cruda/curada vive UNA sola vez en la carpeta maestra
`data/01_Dimensiones_ITT_general/` (capa Silver, Cali completa). Este módulo recibe el
GeoJSON perimetral de CUALQUIER zona y devuelve, por cada una de las 6 dimensiones, solo
los registros que caen dentro del polígono — ya reproyectados y recortados.

REGLAS (heredadas de la validación de Roosevelt):
  - Inmutabilidad: este módulo NO toca los notebooks originales. Se consume desde V3.
  - Fechas: pd.to_datetime(..., format="mixed", dayfirst=False) + coalescencia de columnas
    (histórico vs extensión 2026) para no mandar 2026 a NaT.
  - Línea base intacta + extensión 2026: se CONCATENA, no se sobreescribe el histórico.
  - Filtro espacial estricto: sjoin within / clip contra el polígono real; NO confiar en
    los campos barrio/comuna de las fuentes.
  - CRS por fuente:
      * homicidios/hurtos: x/y = lon/lat WGS84 (EPSG:4326)
      * comparendos/VIF:   lon/lat WGS84 (EPSG:4326)
      * siniestros:        X/Y métrico EPSG:3115 (Magna-Sirgas Cali Oeste) -> reproyectar
  - Rendimiento: pre-filtro por bounding box (.cx) antes del sjoin exacto en capas pesadas
    (comparendos, censo arbóreo ~674k árboles).
  - El extractor NO calcula el ITT ni aplica pesos/umbrales: solo entrega datos filtrados.
    Las fórmulas, ref_min/ref_max y PESOS por zona viven en el notebook V3.

Uso:
    from src.etl_itt_centralizado import ITTZoneExtractor, extraer_dimensiones_zona
    data = extraer_dimensiones_zona(
        poligono_path="data/itt_roosevelt/tramos_Roosevelt_Buffer_100.geojson",
        repo_general_path="data/01_Dimensiones_ITT_general",
    )
    data["seguridad"]["homicidios"]   # GeoDataFrame recortado a la zona
    data["seguridad"]["conteos"]      # dict de conteos por año
"""
from __future__ import annotations

import os
import glob
import warnings

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

warnings.filterwarnings("ignore")

CRS_GEO = "EPSG:4326"       # lon/lat de las fuentes DATIC/CCC
CRS_METRICO = "EPSG:3116"   # Magna-Sirgas Bogotá para longitudes/áreas/buffers (parametrizable)
CRS_SINIESTROS = "EPSG:3115"  # X/Y de la BD de siniestros (Magna-Sirgas Cali Oeste)
ANIOS = [2023, 2024, 2025, 2026]


# ──────────────────────────────────────────────────────────────────────────────
# Utilidades
# ──────────────────────────────────────────────────────────────────────────────
def _to_num(s):
    return pd.to_numeric(s, errors="coerce")


def _fecha_mixed(serie):
    """Parseo tolerante de fechas (format='mixed'); evita NaT por formatos heterogéneos."""
    return pd.to_datetime(serie, format="mixed", dayfirst=False, errors="coerce")


def _coalesce_fecha(df, candidatos):
    """Coalesce de varias columnas de fecha (histórico vs extensión) -> primera no nula por fila."""
    out = pd.Series(pd.NaT, index=df.index)
    for c in candidatos:
        if c in df.columns:
            out = out.fillna(_fecha_mixed(df[c]))
    return out


def _leer_csv(path, usecols=None):
    """Lee CSV grande robusto a encoding y comillas raras."""
    return pd.read_csv(path, usecols=usecols, dtype=str, encoding="utf-8",
                       encoding_errors="replace", low_memory=False)


def _leer_xlsx(path):
    """Lee la primera hoja de un xlsx con calamine (rápido) -> DataFrame."""
    from python_calamine import CalamineWorkbook
    wb = CalamineWorkbook.from_path(path)
    data = wb.get_sheet_by_index(0).to_python(skip_empty_area=True)
    header = [str(h).strip() for h in data[0]]
    return pd.DataFrame(data[1:], columns=header)


def _puntos_wgs84(df, lon_col, lat_col):
    """Construye GeoDataFrame de puntos en WGS84 desde columnas lon/lat (descarta inválidos)."""
    lon = _to_num(df[lon_col]); lat = _to_num(df[lat_col])
    ok = lon.notna() & lat.notna() & (lon.between(-78, -75)) & (lat.between(2.5, 4.5))
    g = gpd.GeoDataFrame(df[ok].copy(),
                         geometry=gpd.points_from_xy(lon[ok], lat[ok]), crs=CRS_GEO)
    return g


def _recorte_bbox_then_within(gdf_pts, poly_gdf):
    """Pre-filtro por bounding box (.cx) y luego sjoin within exacto. Rápido en capas pesadas."""
    if len(gdf_pts) == 0:
        return gdf_pts
    minx, miny, maxx, maxy = poly_gdf.total_bounds
    sub = gdf_pts.cx[minx:maxx, miny:maxy]        # recorte grueso por bbox
    if len(sub) == 0:
        return sub
    dentro = gpd.sjoin(sub, poly_gdf[["geometry"]], predicate="within", how="inner")
    return dentro.drop(columns=[c for c in dentro.columns if c.startswith("index_right")])


def _conteo_anual(gdf, col_anio="anio"):
    if len(gdf) == 0 or col_anio not in gdf.columns:
        return {a: 0 for a in ANIOS}
    s = gdf.groupby(col_anio).size()
    return {a: int(s.get(a, 0)) for a in ANIOS}


# ──────────────────────────────────────────────────────────────────────────────
# Extractor
# ──────────────────────────────────────────────────────────────────────────────
class ITTZoneExtractor:
    def __init__(self, repo_general_path, crs_metrico=CRS_METRICO):
        self.base = repo_general_path
        self.crs_metrico = crs_metrico
        self.poly_wgs = None      # polígono en WGS84
        self.poly_union = None    # geometría unión (para contains rápido)

    # --- polígono ---
    def cargar_poligono(self, poligono_path):
        g = gpd.read_file(poligono_path)
        if g.crs is None:
            g = g.set_crs(CRS_GEO)
        self.poly_wgs = g.to_crs(CRS_GEO)
        self.poly_union = self.poly_wgs.geometry.union_all()
        return self.poly_wgs

    def _p(self, *rel):
        return os.path.join(self.base, *rel)

    # --- Dimensión 1: Seguridad ---
    def seguridad(self):
        D = "1_Dimension_Seguridad_general"
        res = {}
        # Homicidios (x/y = lon/lat; fechah MM/DD/YYYY)
        try:
            dfh = _leer_csv(self._p(D, "DATIC_homicidios_2023_2026T1.csv"))
            g = _puntos_wgs84(dfh, "x", "y")
            g["_f"] = _coalesce_fecha(g, ["fechah", "fechao"])
            g["anio"] = g["_f"].dt.year
            g = _recorte_bbox_then_within(g, self.poly_wgs)
            g = g[g["anio"].isin(ANIOS)]
            res["homicidios"] = g
        except Exception as e:
            res["homicidios"] = gpd.GeoDataFrame(geometry=[], crs=CRS_GEO); print(f"[seguridad] homicidios: {type(e).__name__}: {e}")
        # Hurtos (x/y lon/lat; anio ya viene)
        try:
            dfr = _leer_csv(self._p(D, "DATIC_hurtos_2023_2026T1.csv"))
            g = _puntos_wgs84(dfr, "x", "y")
            g["anio"] = _to_num(g["anio"]) if "anio" in g.columns else _coalesce_fecha(g, ["fecha_hecho", "fecha_hech"]).dt.year
            g = _recorte_bbox_then_within(g, self.poly_wgs)
            g = g[g["anio"].isin(ANIOS)]
            res["hurtos"] = g
        except Exception as e:
            res["hurtos"] = gpd.GeoDataFrame(geometry=[], crs=CRS_GEO); print(f"[seguridad] hurtos: {type(e).__name__}: {e}")
        # Comparendos (lat/lon; agrupado -> riñas/SPA). Base pesada -> bbox primero.
        try:
            dfc = _leer_csv(self._p(D, "DATIC_comparendos_2023_2026T1.csv"))
            gc = _puntos_wgs84(dfc, "lon", "lat")
            gc["_f"] = _coalesce_fecha(gc, ["fecha_hecho", "fecha_hech"])
            gc["anio"] = gc["_f"].dt.year
            gc = _recorte_bbox_then_within(gc, self.poly_wgs)
            gc = gc[gc["anio"].isin(ANIOS)]
            ag = gc["agrupado"].astype(str).str.upper() if "agrupado" in gc.columns else pd.Series("", index=gc.index)
            res["comparendos"] = gc
            res["rinas"] = gc[ag.str.contains("RI", na=False)].copy()           # criterio amplio (ajustable por zona)
            res["spa"] = gc[ag.str.strip() == "SUSTANCIAS PSICOACTIVAS"].copy()
        except Exception as e:
            for k in ("comparendos", "rinas", "spa"):
                res[k] = gpd.GeoDataFrame(geometry=[], crs=CRS_GEO)
            print(f"[seguridad] comparendos: {type(e).__name__}: {e}")
        res["conteos"] = {k: _conteo_anual(res[k]) for k in ("homicidios", "hurtos", "rinas", "spa") if k in res}
        return res

    # --- Dimensión 2: Cohesión Social ---
    def cohesion(self):
        D = "2_Dimensión_Cohesion_Social_general"
        res = {}
        try:
            dfv = _leer_csv(self._p(D, "DATIC_violencia_intrafamiliar_2023_2026T1.csv"))
            g = _puntos_wgs84(dfv, "x", "y")
            g["anio"] = _to_num(g["anio"]) if "anio" in g.columns else _coalesce_fecha(g, ["fecha_hecho", "fecha_hech"]).dt.year
            g = _recorte_bbox_then_within(g, self.poly_wgs)
            g = g[g["anio"].isin(ANIOS)]
            res["vif"] = g
        except Exception as e:
            res["vif"] = gpd.GeoDataFrame(geometry=[], crs=CRS_GEO); print(f"[cohesion] vif: {type(e).__name__}: {e}")
        res["conteos"] = {"vif": _conteo_anual(res.get("vif", gpd.GeoDataFrame()))}
        return res

    # --- Dimensión 3: Movilidad ---
    def movilidad(self):
        D = "3_Dimension_Movilidad_general"
        res = {}
        try:
            # La BD principal de siniestros YA cubre 2023-2026 completa y está limpia; la
            # extensión abr-may-jun ya está incluida en ella (verificado: sus puntos caen en
            # la base). Por eso NO se concatena la extensión ni se deduplica (eso removía
            # registros legítimos). Si en el futuro la base NO trajera 2026, reactivar la unión.
            base = _leer_xlsx(self._p(D, "BD_SINIESTROS_2023_2026_COMUNA_BARRIO.xlsx"))
            x = _to_num(base["X"]); y = _to_num(base["Y"]); ok = x.notna() & y.notna()
            g = gpd.GeoDataFrame(base[ok].copy(), geometry=gpd.points_from_xy(x[ok], y[ok]), crs=CRS_SINIESTROS).to_crs(CRS_GEO)
            g["_f"] = _coalesce_fecha(g, ["Fecha"])
            g["anio"] = g["_f"].dt.year
            g = _recorte_bbox_then_within(g, self.poly_wgs)
            g = g[g["anio"].isin(ANIOS)]
            res["siniestros"] = g
            res["lesionados"] = g[g["Tipo_Confi"] == "Lesiones"].copy() if "Tipo_Confi" in g.columns else g.iloc[0:0]
            res["mortales"] = g[g["Tipo_Confi"] == "Mortal"].copy() if "Tipo_Confi" in g.columns else g.iloc[0:0]
        except Exception as e:
            for k in ("siniestros", "lesionados", "mortales"):
                res[k] = gpd.GeoDataFrame(geometry=[], crs=CRS_GEO)
            print(f"[movilidad] siniestros: {type(e).__name__}: {e}")
        res["conteos"] = {k: _conteo_anual(res[k]) for k in ("siniestros", "lesionados", "mortales") if k in res}
        return res

    # --- Dimensión 4: Desarrollo Económico ---
    def desarrollo_economico(self):
        D = "4_Dimension_Desarrollo_Economico_general"
        res = {}
        try:
            df = _leer_csv(self._p(D, "unidades_productivas_curated.csv"))
            df.columns = [c.lstrip("\ufeff") for c in df.columns]
            lonc = next((c for c in ("longitud", "lon", "x") if c in df.columns), None)
            latc = next((c for c in ("latitud", "lat", "y") if c in df.columns), None)
            if lonc and latc:
                g = _puntos_wgs84(df, lonc, latc)
                g = _recorte_bbox_then_within(g, self.poly_wgs)
            else:
                g = gpd.GeoDataFrame(df.iloc[0:0], geometry=[], crs=CRS_GEO)
                print("[de] unidades_productivas_curated sin columnas lon/lat; "
                      "el empleo/stock se sigue tomando de data/Camara_de_Comercio (xlsx PERSONAL_OCUPADO).")
            res["unidades_productivas"] = g
            res["nota_empleo"] = ("Empleo/stock activo: fuente oficial sigue siendo "
                                  "data/Camara_de_Comercio (PERSONAL_OCUPADO + CSV 2026 de fechas); "
                                  "este curated es complementario hasta validar coords/empleo.")
        except Exception as e:
            res["unidades_productivas"] = gpd.GeoDataFrame(geometry=[], crs=CRS_GEO)
            print(f"[de] unidades_productivas: {type(e).__name__}: {e}")
        return res

    # --- Dimensión 5: Entorno Urbano ---
    def entorno(self):
        D = "5_Dimension_Entorno_Urbano_general"
        res = {}
        # Censo arbóreo (~674k): leer con bbox del polígono para no saturar RAM.
        try:
            shp = self._p(D, "DAMA", "CENSO_ARBOREO.shp")
            # bbox del polígono en el CRS del shp para filtrar en la lectura
            poly_any = self.poly_wgs
            arb = gpd.read_file(shp, bbox=tuple(poly_any.to_crs(gpd.read_file(shp, rows=1).crs).total_bounds))
            arb = arb.to_crs(CRS_GEO)
            arb = _recorte_bbox_then_within(arb, self.poly_wgs) if arb.geom_type.iloc[0] == "Point" else gpd.clip(arb, self.poly_wgs)
            res["censo_arboreo"] = arb
        except Exception as e:
            res["censo_arboreo"] = gpd.GeoDataFrame(geometry=[], crs=CRS_GEO); print(f"[entorno] censo_arboreo: {type(e).__name__}: {e}")
        # Estaciones MECAL (intersección / dentro)
        try:
            mec = gpd.read_file(self._p(D, "Estaciones_MECAL", "Estaciones_MECAL.shp")).to_crs(CRS_GEO)
            res["estaciones_mecal"] = mec[mec.within(self.poly_union)].copy()
        except Exception as e:
            res["estaciones_mecal"] = gpd.GeoDataFrame(geometry=[], crs=CRS_GEO); print(f"[entorno] mecal: {type(e).__name__}: {e}")
        # Intervenciones urbanas (clip vectorial)
        try:
            carp = self._p(D, "INTERV_AHDI_LEG_URBA_24_25_26_GeoJson")
            capas = {}
            for gj in glob.glob(os.path.join(carp, "*.geojson")):
                nombre = os.path.splitext(os.path.basename(gj))[0]
                cg = gpd.read_file(gj).to_crs(CRS_GEO)
                capas[nombre] = gpd.clip(cg, self.poly_wgs)
            res["intervenciones"] = capas
        except Exception as e:
            res["intervenciones"] = {}; print(f"[entorno] intervenciones: {type(e).__name__}: {e}")
        # NDVI NO está centralizado: sigue siendo por zona (raster local). Se documenta.
        res["nota_ndvi"] = "NDVI no está en la capa central; usar los rasters locales de la zona (data/itt_<zona>/5_.../NVDI)."
        return res

    # --- Dimensión 6: Educación ---
    def educacion(self, sedes_geocodificadas_path=None):
        """DUE no trae coords -> las sedes dentro del polígono se identifican por una capa
        de sedes geocodificadas (si se provee) o por los DANE de colegios cuya dirección
        esté en la zona. Devuelve los DANE candidatos y, si hay capa geo, las sedes dentro.
        La lectura de matrícula/deserción (Anexo 6A/SIMPADE) se hace en el build por DANE,
        NO aquí (optimización: no cargar los Anexo completos en el extractor)."""
        D = "6_Dimension_Educacion_genaral"
        res = {"danes_en_zona": [], "sedes": gpd.GeoDataFrame(geometry=[], crs=CRS_GEO)}
        try:
            due_path = self._p(D, "Educacion_2026", "SIMAT y SIMPADE anonimizado + DUE",
                               "DUE", "DUE_Clasificacion_Establecimientos_Sedes.xlsx")
            due = _leer_xlsx(due_path)
            res["due"] = due
            if sedes_geocodificadas_path and os.path.exists(sedes_geocodificadas_path):
                sedes = gpd.read_file(sedes_geocodificadas_path).to_crs(CRS_GEO)
                dentro = sedes[sedes.within(self.poly_union)].copy()
                res["sedes"] = dentro
                col_dane = next((c for c in dentro.columns if "dane" in c.lower() or c.lower() in ("codigo", "código")), None)
                if col_dane:
                    res["danes_en_zona"] = sorted(set(dentro[col_dane].astype(str)))
            else:
                res["nota"] = ("DUE sin coords y sin capa de sedes geocodificadas: proveer "
                               "sedes_geocodificadas_path (geojson con DANE) para filtrar por polígono. "
                               "Alternativa: usar el consolidado de educación por zona ya validado.")
        except Exception as e:
            print(f"[educacion] {type(e).__name__}: {e}")
        return res


def extraer_dimensiones_zona(poligono_path, repo_general_path,
                             crs_metrico=CRS_METRICO, sedes_geocodificadas_path=None):
    """Orquesta la extracción de las 6 dimensiones para un polígono dado.
    Devuelve un dict con un GeoDataFrame (o sub-dict) por dimensión + 'conteos'."""
    ext = ITTZoneExtractor(repo_general_path, crs_metrico=crs_metrico)
    ext.cargar_poligono(poligono_path)
    return {
        "poligono": ext.poly_wgs,
        "seguridad": ext.seguridad(),
        "cohesion": ext.cohesion(),
        "movilidad": ext.movilidad(),
        "desarrollo_economico": ext.desarrollo_economico(),
        "entorno": ext.entorno(),
        "educacion": ext.educacion(sedes_geocodificadas_path=sedes_geocodificadas_path),
    }


if __name__ == "__main__":
    import sys, time
    poly = sys.argv[1] if len(sys.argv) > 1 else "data/itt_roosevelt/tramos_Roosevelt_Buffer_100.geojson"
    repo = sys.argv[2] if len(sys.argv) > 2 else "data/01_Dimensiones_ITT_general"
    t0 = time.time()
    data = extraer_dimensiones_zona(poly, repo)
    print(f"\n=== Extracción zona: {os.path.basename(poly)}  ({time.time()-t0:.1f}s) ===")
    print("Seguridad  :", data["seguridad"]["conteos"])
    print("Cohesion   :", data["cohesion"]["conteos"])
    print("Movilidad  :", data["movilidad"]["conteos"])
    print("DE unidades:", len(data["desarrollo_economico"]["unidades_productivas"]))
    print("Arboles    :", len(data["entorno"]["censo_arboreo"]))
    print("MECAL      :", len(data["entorno"]["estaciones_mecal"]))
    print("DANES zona :", data["educacion"].get("danes_en_zona"))
