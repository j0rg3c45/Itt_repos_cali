"""
Generador del sitio estático público (GitHub Pages) para ITT Ciudad Paraíso.

PRINCIPIO DE PRIVACIDAD POR DISEÑO
----------------------------------
Este script publica SOLO datos agregados (conteos por año/trimestre y scores ITT)
leídos del Excel consolidado. NO lee las fuentes crudas con registros individuales
y NO publica coordenadas de casos de seguridad/violencia. El mapa del sitio usa
únicamente capas agregadas: polígono de la zona, red peatonal OSM, NDVI y un mapa
de calor de densidad — nunca marcadores por caso de homicidio/hurto/VIF/etc.

Salida: carpeta `github_pages/site/` lista para servir en GitHub Pages.

Uso:
    uv run python github_pages/build_site.py
"""
import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent          # raiz del repo
HERE = Path(__file__).resolve().parent                 # github_pages/
SITE = HERE / "site"                                   # salida publicable
ASSETS = SITE / "assets"
XLSX = ROOT / "outputs" / "itt_ciudad_paraiso" / "ITT_Ciudad_Paraiso_Consolidado.xlsx"

# Graficos agregados seguros (PNG). Excluimos nada sensible: son figuras de series.
PNG_CHARTS = [
    ("ciudad_paraiso_itt_global.png",            "Evolución del ITT global"),
    ("ciudad_paraiso_radar_itt.png",             "Radar ITT por dimensión"),
    ("ciudad_paraiso_heatmap_indicadores.png",   "Heatmap de indicadores (anual)"),
    ("ciudad_paraiso_eu_ndvi_arbolado_card.png", "Entorno Urbano: NDVI + arbolado"),
    ("ciudad_paraiso_evol_trim_seguridad.png",   "Seguridad — evolución trimestral"),
    ("ciudad_paraiso_evol_trim_movilidad.png",   "Movilidad — evolución trimestral"),
    ("ciudad_paraiso_evol_trim_dessocial.png",   "Cohesión social — evolución trimestral"),
    ("ciudad_paraiso_de_evolucion_anual.png",    "Desarrollo económico — evolución anual"),
]

# Hojas del Excel que son AGREGADAS y seguras para publicar.
SHEETS_PUBLICABLES = [
    "ITT_Resumen", "Seguridad", "Movilidad", "Cohesion_Social_DesSocial",
    "Entorno_Urbano_NDVI_arbol", "Desarrollo_Economico", "Indicadores_Trimestrales",
]
SHEET_TITULOS = {
    "ITT_Resumen":                "Resumen ITT",
    "Seguridad":                  "Seguridad",
    "Movilidad":                  "Movilidad",
    "Cohesion_Social_DesSocial":  "Cohesión Social",
    "Entorno_Urbano_NDVI_arbol":  "Entorno Urbano",
    "Desarrollo_Economico":       "Desarrollo Económico",
    "Indicadores_Trimestrales":   "Indicadores Trimestrales",
}


def leer_tablas_agregadas():
    """Lee del Excel solo las hojas agregadas publicables y las vuelve JSON seguro."""
    if not XLSX.exists():
        raise FileNotFoundError(
            f"No existe {XLSX}. Ejecuta primero el notebook para generar el Excel consolidado."
        )
    tablas = {}
    for sheet in SHEETS_PUBLICABLES:
        try:
            df = pd.read_excel(XLSX, sheet_name=sheet)
        except ValueError:
            continue  # hoja ausente: se omite sin romper
        df = df.where(pd.notnull(df), None)  # NaN -> None para JSON limpio
        tablas[sheet] = {
            "titulo": SHEET_TITULOS.get(sheet, sheet),
            "columnas": [str(c) for c in df.columns],
            "filas": df.values.tolist(),
        }
    return tablas


def copiar_graficos():
    """Copia los PNG de graficos al sitio. Busca primero en github_pages/charts/
    (versionado, lo usa el workflow) y como fallback en la raiz del repo (dev local)."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    disponibles = []
    for fname, titulo in PNG_CHARTS:
        src = HERE / "charts" / fname
        if not src.exists():
            src = ROOT / fname  # fallback: raiz (tras ejecutar el notebook localmente)
        if src.exists():
            shutil.copy2(src, ASSETS / fname)
            disponibles.append({"archivo": f"assets/{fname}", "titulo": titulo})
    return disponibles


def main():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    tablas = leer_tablas_agregadas()
    graficos = copiar_graficos()

    # Copiar el index.html del template al sitio
    shutil.copy2(HERE / "template" / "index.html", SITE / "index.html")
    # .nojekyll para que GitHub Pages no procese con Jekyll (sirve los archivos tal cual)
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    # Datos embebidos en un JSON que el index.html consume (todo agregado).
    datos = {
        "zona": "Ciudad Paraíso — Comuna 3, Cali",
        "area_ha": 33.70,
        "area_m2": 337039.2,
        "periodo": "2023–2026 (2026 parcial)",
        "tablas": tablas,
        "graficos": graficos,
        "nota_privacidad": (
            "Este sitio publica únicamente datos agregados (conteos anuales/trimestrales "
            "y scores del Índice de Transformación Territorial). No contiene registros "
            "individuales, datos personales ni ubicaciones de casos de seguridad o violencia."
        ),
    }
    (SITE / "data.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    print("Datos agregados exportados:")
    for s, t in tablas.items():
        print(f"  tabla  {s:28s} {len(t['filas'])} filas x {len(t['columnas'])} cols")
    print(f"  graficos copiados: {len(graficos)}")
    print(f"  -> {SITE / 'data.json'}")


if __name__ == "__main__":
    main()
