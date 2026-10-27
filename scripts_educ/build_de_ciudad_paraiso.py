"""Regenera el consolidado de Desarrollo Economico de Ciudad Paraiso CON empleo
(PERSONAL_OCUPADO), replicando la metodologia de Roosevelt (build_de_roosevelt.py).

DIFERENCIA con Roosevelt: aqui la fuente con coordenadas+empleo+ingresos ya viene RECORTADA
al poligono de Ciudad Paraiso (registro_mercantil_2025_con_coordenadas_poligono_Barrio_Obrero.geojson),
asi que NO hace falta spatial join: se usa tal cual (762 negocios del poligono).

FUENTES:
 1. GEOJSON recortado al poligono Ciudad Paraiso -> NUM_INSCRI, PERSONAL_O (empleo), INGRESOS_A (ingresos),
    CODIGO_CII/DESC_CIIU/NOMBRE_SEC/CATEGORIA/TAMANO957, X/Y. Es el universo del poligono.
 2. CSV global 2026 (20260929-Reporte General Registro Mercantil.csv) -> fechaMatricula /
    fechaRenovacion / fechaCancelacion / ingresosOrdinarios HASTA 2026, cruzado por numeroInscrito.

REGLA DEL PROYECTO: empleo = PERSONAL_OCUPADO de la fuente con coords; ingresos del geojson
(INGRESOS_A); el CSV 2026 actualiza fechas (stock activo real por año y trimestres 2026).

Uso:  python scripts_educ/build_de_barrio_obrero.py
"""
import csv
import json
import os
import re
import time

import geopandas as gpd
import pandas as pd

GEOJSON = "data/Ciudad_Paraiso/4_Dimension_Desarrollo_Economico/registro_mercantil_2025_con_coordenadas_poligono_ciudad_Paraiso.geojson"
CSV_2026 = "data/Camara_de_Comercio/20260929-Reporte General Registro Mercantil.csv"
OUT = "data/Ciudad_Paraiso/4_Dimension_Desarrollo_Economico/registro_mercantil_CP_2023_2026_consolidado.json"


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

    # ── 1) GEOJSON recortado al poligono Ciudad Paraiso: coords + empleo + ingresos + ciiu ──
    g = gpd.read_file(GEOJSON)
    base_geo = {}
    for _, r in g.iterrows():
        k = _k(r["NUM_INSCRI"])
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
    print(f"GEOJSON leido en {time.time()-t0:.1f}s | {len(base_geo)} negocios en poligono (coords+empleo)", flush=True)

    # ── 2) CSV 2026: fechas + estado, cruzado por numeroInscrito ──
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
                "ingresosOrdinarios": _num(row[35]),
            }
    print(f"CSV 2026 cruzado: {len(csv_info)}/{len(base_geo)} negocios con registro 2026", flush=True)

    # ── 3) Ensamblar consolidado (empleo del geojson; fechas del CSV 2026) ──
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
            "empleo": gg["empleo"],
            "codigo_ciiu": gg["codigo_ciiu"], "desc_ciiu": gg["desc_ciiu"],
            "sector": gg["sector"], "categoria": gg["categoria"], "tamano": gg["tamano"],
            "latitud": gg["latitud"], "longitud": gg["longitud"],
        })
        registros.append(reg)

    out = {
        "generado_de": "GEOJSON recortado al poligono Ciudad Paraiso (registro_mercantil_2025_con_coordenadas_"
                       "poligono_Barrio_Obrero.geojson) para coords+empleo(PERSONAL_O)+ingresos(INGRESOS_A) "
                       "+ CSV 2026 (20260929-Reporte General Registro Mercantil.csv) para fechas/estado HASTA 2026, "
                       "cruzado por numeroInscrito.",
        "nota": "Empleo = PERSONAL_OCUPADO (PERSONAL_O del geojson). Linea base + extension 2026 de fechas "
                "del CSV. Score DE = establecimientos + ingresos + empleo (3 componentes, igual que Roosevelt).",
        "n": len(registros),
        "registros": registros,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"negocios consolidados: {len(registros)} -> {OUT}", flush=True)

    # ── Diagnostico: stock activo + empleo por año ──
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
