"""Consolidado de Desarrollo Economico de Avenida Ciudad de Cali CON empleo (PERSONAL_OCUPADO).

Diferencia con las otras zonas: la fuente con coords+empleo viene PARTIDA en 8 geojson (uno por
tramo T1..T8), ya recortados. Se CONCATENAN los 8, se deduplica por NUM_INSCRI (un negocio puede
caer en el buffer de >1 tramo) y se cruza con el CSV 2026 por numeroInscrito para fechas/estado.

Uso:  python scripts_educ/build_de_avenida_ciudad_de_cali.py
"""
import csv
import json
import os
import re
import time
import glob

import geopandas as gpd
import pandas as pd

GEOJSON_GLOB = "data/itt_avenida_ciudad_de_cali/4_Desarrollo_Economico/registro_mercantil_2025_con_coordenadas_poligono_ciudad_de_cali_T*.geojson"
CSV_2026 = "data/Camara_de_Comercio/20260929-Reporte General Registro Mercantil.csv"
OUT = "data/itt_avenida_ciudad_de_cali/4_Desarrollo_Economico/registro_mercantil_ACC_2023_2026_consolidado.json"


def _k(v):
    s = str(v).replace("=", "").replace('"', "").strip()
    return s[:-2] if s.endswith(".0") else s


def _num(v):
    try:
        n = float(v)
        return n if n == n else None
    except (TypeError, ValueError):
        return None


def _iso(v):
    if v is None:
        return None
    s = str(v).strip()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if not m:
        return None
    if m.group(1) in ("0001", "1900"):
        return None
    return m.group(0)


def main():
    t0 = time.time()

    # ── 1) Concatenar los 8 geojson por tramo (coords+empleo+ingresos), dedup por NUM_INSCRI ──
    base_geo = {}
    n_leidos = 0
    for f in sorted(glob.glob(GEOJSON_GLOB)):
        g = gpd.read_file(f)
        n_leidos += len(g)
        for _, r in g.iterrows():
            k = _k(r["NUM_INSCRI"])
            if k in base_geo:
                continue  # dedup: un negocio en el buffer de varios tramos se cuenta una vez
            base_geo[k] = {
                "empleo": _num(r.get("PERSONAL_O")),
                "ingresos_src": _num(r.get("INGRESOS_A")),
                "codigo_ciiu": _k(r.get("CODIGO_CII")),
                "desc_ciiu": str(r.get("DESC_CIIU") or "").strip(),
                "sector": str(r.get("NOMBRE_SEC") or "").strip(),
                "categoria": str(r.get("CATEGORIA") or "").strip(),
                "tamano": str(r.get("TAMANO957") or "").strip(),
                "latitud": str(r.get("Y")),
                "longitud": str(r.get("X")),
            }
    print(f"8 tramos leidos en {time.time()-t0:.1f}s | {n_leidos} filas -> {len(base_geo)} negocios unicos", flush=True)

    # ── 2) CSV 2026: fechas + estado por numeroInscrito ──
    csv_info = {}
    with open(CSV_2026, encoding="utf-8", errors="replace") as f:
        rd = csv.reader(f, delimiter=";")
        next(rd)
        for row in rd:
            if len(row) < 36:
                continue
            k = _k(row[1])
            if k not in base_geo:
                continue
            fren = _iso(row[4])
            prev = csv_info.get(k)
            if prev is not None and (prev["fechaRenovacion"] or "") >= (fren or ""):
                continue
            csv_info[k] = {
                "estado": str(row[2]).strip() or "Registro Activo",
                "fechaMatricula": _iso(row[3]),
                "fechaRenovacion": fren,
                "fechaCancelacion": _iso(row[5]),
            }
    print(f"CSV 2026 cruzado: {len(csv_info)}/{len(base_geo)} negocios con registro 2026", flush=True)

    # ── 3) Ensamblar ──
    registros = []
    for k, gg in base_geo.items():
        info = csv_info.get(k)
        _ing = gg["ingresos_src"]
        if info is None:
            reg = {"numeroInscrito": k, "estado": "Registro Activo",
                   "fechaMatricula": None, "fechaRenovacion": None, "fechaCancelacion": None,
                   "ingresosOrdinarios": _ing, "activoTotal": None}
        else:
            reg = {"numeroInscrito": k, "estado": info["estado"],
                   "fechaMatricula": info["fechaMatricula"], "fechaRenovacion": info["fechaRenovacion"],
                   "fechaCancelacion": info["fechaCancelacion"],
                   "ingresosOrdinarios": _ing, "activoTotal": None}
        reg.update({
            "empleo": gg["empleo"], "codigo_ciiu": gg["codigo_ciiu"], "desc_ciiu": gg["desc_ciiu"],
            "sector": gg["sector"], "categoria": gg["categoria"], "tamano": gg["tamano"],
            "latitud": gg["latitud"], "longitud": gg["longitud"],
        })
        registros.append(reg)

    out = {
        "generado_de": "8 geojson de registro mercantil por tramo (T1..T8) de Avenida Ciudad de Cali "
                       "(coords+empleo PERSONAL_O+ingresos INGRESOS_A), concatenados y deduplicados por "
                       "NUM_INSCRI + CSV 2026 (20260929) para fechas/estado por numeroInscrito.",
        "nota": "Empleo = PERSONAL_OCUPADO. Linea base + extension 2026. Score DE = establecimientos + "
                "ingresos + empleo (3 componentes, como las demas zonas).",
        "n": len(registros),
        "registros": registros,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"negocios consolidados: {len(registros)} -> {OUT}", flush=True)

    dd = pd.DataFrame(registros)
    dd["fm"] = pd.to_datetime(dd["fechaMatricula"], errors="coerce")
    dd["fc"] = pd.to_datetime(dd["fechaCancelacion"], errors="coerce")
    dd["emp"] = pd.to_numeric(dd["empleo"], errors="coerce")
    for a in [2023, 2024, 2025, 2026]:
        mask = (dd["fm"].dt.year <= a) & (dd["fc"].isna() | (dd["fc"].dt.year > a))
        act = dd[mask]
        print(f"  {a}: stock activo={len(act)} | empleo={act['emp'].where(act['emp']>=0).sum():.0f}", flush=True)


if __name__ == "__main__":
    main()
