"""
Generador del sitio estático público (GitHub Pages) para ITT Corredor San Fernando (Yawa).

PRINCIPIO DE PRIVACIDAD POR DISEÑO
----------------------------------
Publica SOLO datos agregados (conteos por año/trimestre y scores ITT) leídos del Excel
consolidado. NO lee fuentes crudas con registros individuales y NO publica coordenadas de
casos. El mapa (build_map.py) usa capas agregadas y, para VIF/VBG, SOLO mapa de calor
(nunca puntos), para no permitir re-identificar víctimas en una zona pequeña.

Salida: carpeta `github_pages_san_fernando/site/` lista para GitHub Pages.

Uso:
    uv run python github_pages_san_fernando/build_site.py
"""
import json
import math
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
SITE = HERE / "site"
ASSETS = SITE / "assets"
XLSX = ROOT / "outputs" / "itt_corredor_san_fernando" / "ITT_Corredor_San_Fernando_Consolidado.xlsx"

PNG_CHARTS = [
    ("corredor_san_fernando_itt_global.png",          "ITT Global — Corredor San Fernando (Yawa)"),
    ("corredor_san_fernando_radar_itt.png",           "ITT por dimensión — Corredor San Fernando (Yawa)"),
    ("corredor_san_fernando_heatmap_indicadores.png", "Indicadores crudos por dimensión — Corredor San Fernando"),
    ("corredor_san_fernando_eu_ndvi_arbolado_card.png", "Entorno Urbano · NDVI anual + censo arbóreo — Corredor San Fernando"),
    ("corredor_san_fernando_evol_trim_seguridad.png", "Seguridad — Evolución Trimestral | Corredor San Fernando"),
    ("corredor_san_fernando_evol_trim_movilidad.png", "Movilidad — Evolución Trimestral | Corredor San Fernando"),
    ("corredor_san_fernando_evol_trim_dessocial.png", "DesSocial (Cohesión + Educación) — Evolución Trimestral | Corredor San Fernando"),
    ("corredor_san_fernando_heatmap_trim_seguridad.png", "Seguridad — Heatmap Trimestral | Corredor San Fernando"),
    ("corredor_san_fernando_heatmap_trim_movilidad.png", "Movilidad — Heatmap Trimestral | Corredor San Fernando"),
    ("corredor_san_fernando_heatmap_trim_dessocial.png", "DesSocial — Heatmap Trimestral | Corredor San Fernando"),
    ("corredor_san_fernando_de_heatmap_trim.png",     "Desarrollo Económico — Heatmap Trimestral | Corredor San Fernando"),
    ("corredor_san_fernando_de_evolucion_anual.png",  "Creación de Negocios Nuevos por Año | Corredor San Fernando"),
    ("corredor_san_fernando_de_sectores.png",         "Desarrollo Económico por sector social (Salud/Educación/Deporte) | Corredor San Fernando"),
    ("corredor_san_fernando_comparacion_subzonas.png", "Comparación por subzonas | Corredor San Fernando"),
]

# Hojas del Excel AGREGADAS y seguras para publicar.
# NO se publican hojas con detalle por entidad: Educacion_LiceoDptal (colegio),
# Vivienda_SecVivienda (barrios/direcciones), ni listados individuales.
SHEETS_PUBLICABLES = [
    "ITT_Resumen", "Seguridad", "Movilidad", "Cohesion_y_Educacion",
    "Entorno_Urbano", "Desarrollo_Economico", "DE_Sectores_Salud_Dep_Edu",
    "Indicadores_Trimestrales", "Comparacion_Subzonas",
]
SHEET_TITULOS = {
    "ITT_Resumen":              "Resumen ITT",
    "Seguridad":                "Seguridad",
    "Movilidad":                "Movilidad",
    "Cohesion_y_Educacion":     "Cohesión + Educación",
    "Entorno_Urbano":           "Entorno Urbano",
    "Desarrollo_Economico":     "Desarrollo Económico",
    "DE_Sectores_Salud_Dep_Edu": "DE · Salud/Educación/Deporte",
    "Indicadores_Trimestrales": "Indicadores Trimestrales",
    "Comparacion_Subzonas":     "Comparación por Subzonas",
}


def leer_tablas_agregadas():
    if not XLSX.exists():
        raise FileNotFoundError(f"No existe {XLSX}. Ejecuta el notebook 09 para generar el Excel.")

    def limpiar(v):
        if v is None:
            return None
        try:
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                return None
        except TypeError:
            pass
        if pd.isna(v):
            return None
        if isinstance(v, np.integer):
            return int(v)
        if isinstance(v, np.floating):
            f = float(v)
            return None if (math.isnan(f) or math.isinf(f)) else f
        if isinstance(v, np.bool_):
            return bool(v)
        return v

    tablas = {}
    for sheet in SHEETS_PUBLICABLES:
        try:
            df = pd.read_excel(XLSX, sheet_name=sheet)
        except ValueError:
            continue
        filas = [[limpiar(v) for v in fila] for fila in df.values.tolist()]
        tablas[sheet] = {"titulo": SHEET_TITULOS.get(sheet, sheet),
                         "columnas": [str(c) for c in df.columns], "filas": filas}
    return tablas


def copiar_graficos():
    ASSETS.mkdir(parents=True, exist_ok=True)
    disponibles = []
    for fname, titulo in PNG_CHARTS:
        src = HERE / "charts" / fname
        if not src.exists():
            src = ROOT / fname
        if src.exists():
            shutil.copy2(src, ASSETS / fname)
            disponibles.append({"archivo": f"assets/{fname}", "titulo": titulo})
    return disponibles


def main():
    SITE.mkdir(parents=True, exist_ok=True)
    for item in SITE.iterdir():
        if item.name == "mapa.html":
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()
    ASSETS.mkdir(parents=True, exist_ok=True)

    tablas = leer_tablas_agregadas()
    graficos = copiar_graficos()

    shutil.copy2(HERE / "template" / "index.html", SITE / "index.html")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    datos = {
        "zona": "Corredor San Fernando (Yawa) — Comuna 19, Cali",
        "area_ha": 265.33,
        "area_m2": 2653275.0,
        "periodo": "2023–2026 (2026 datos a la fecha)",
        "tablas": tablas,
        "graficos": graficos,
        "nota_privacidad": (
            "Las tablas y gráficos publican datos agregados (conteos anuales/trimestrales y "
            "scores del ITT). En el mapa, los eventos de seguridad/movilidad se muestran como "
            "ubicación y tipo únicamente. Los casos de violencia intrafamiliar (VIF) y de género "
            "(VBG) se publican SOLO como mapa de calor, nunca como puntos individuales, para "
            "proteger la identidad de las víctimas. No se publican direcciones, fechas ni datos "
            "personales de ningún caso."
        ),
    }
    (SITE / "data.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=1, allow_nan=False), encoding="utf-8")

    print("Datos agregados exportados:")
    for s, t in tablas.items():
        print(f"  tabla  {s:28s} {len(t['filas'])} filas x {len(t['columnas'])} cols")
    print(f"  graficos copiados: {len(graficos)}")
    print(f"  -> {SITE / 'data.json'}")


if __name__ == "__main__":
    main()
