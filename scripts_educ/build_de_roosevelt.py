"""Construye el consolidado de Desarrollo Económico del Corredor Roosevelt replicando
la metodología de Barrio Obrero, con la data 2026 de la Cámara de Comercio (CCC).

FUENTES (dos, igual que Barrio Obrero):
 1. CSV 2026 corte sep-2026: data/Camara_de_Comercio/20260929-Reporte General Registro Mercantil.csv
    -> aporta fechaMatricula / fechaRenovacion / fechaCancelacion / ingresosOrdinarios HASTA 2026.
    Es la LINEA BASE + EXTENSION 2026 (historico intacto + registros nuevos 2026). Sin coords ni empleo.
 2. XLSX 2025 con coordenadas: data/Camara_de_Comercio/registro_mercantil_2025_con_coordenadas.xlsx
    -> aporta X/Y (para recortar al buffer) + PERSONAL_OCUPADO (empleo) + CIIU/sector.
    REGLA DEL PROYECTO: el empleo SIEMPRE sale de PERSONAL_OCUPADO del XLSX original, NO del CSV.

CRUCE: se recorta al buffer de Roosevelt usando las coordenadas del XLSX (spatial join within),
y para esos negocios (por numeroInscrito) se toman del CSV 2026 las fechas/ingresos actualizados.
El empleo se toma del XLSX (PERSONAL_OCUPADO). Asi el stock activo y los trimestres 2026 son reales.

El CSV no trae activoTotal poblado -> score DE = establecimientos + ingresos + empleo (3 componentes).

Uso:  python scripts_educ/build_de_roosevelt.py
"""
import csv
import json
import os
import re
import time

import geopandas as gpd
from shapely.geometry import Point
from python_calamine import CalamineWorkbook

CSV_2026 = "data/Camara_de_Comercio/20260929-Reporte General Registro Mercantil.csv"
XLSX = "data/Camara_de_Comercio/registro_mercantil_2025_con_coordenadas.xlsx"
POLY = "data/itt_roosevelt/tramos_Roosevelt_Buffer_100.geojson"
OUT = "data/itt_roosevelt/4_Desarrollo_Economico/registro_mercantil_Roosevelt_2023_2026_consolidado.json"


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
    """'2024-05-30 13:00:56' -> '2024-05-30'. Fechas centinela (0001-...) -> None."""
    if v is None:
        return None
    s = str(v).strip()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if not m:
        return None
    if m.group(1) in ("0001", "1900"):   # centinela de 'sin cancelacion'
        return None
    return m.group(0)


def main():
    t0 = time.time()

    # ── 1) XLSX 2025: coordenadas + empleo (PERSONAL_OCUPADO) + CIIU/sector ──────
    wb = CalamineWorkbook.from_path(XLSX)
    data = wb.get_sheet_by_index(0).to_python(skip_empty_area=True)
    h = [str(x).strip() for x in data[0]]
    ix = {n: h.index(n) for n in h}
    poly = gpd.read_file(POLY).to_crs("EPSG:4326").geometry.union_all()

    # negocios del XLSX dentro del buffer -> dict por numeroInscrito con coords+empleo+ciiu
    base_geo = {}
    for r in data[1:]:
        x, y = _num(r[ix["X"]]), _num(r[ix["Y"]])
        if x is None or y is None or not (-77.6 < x < -76.0 and 3.0 < y < 3.9):
            continue
        if not poly.contains(Point(x, y)):
            continue
        k = _k(r[ix["NUM INSCRITO"]])
        base_geo[k] = {
            "empleo": _num(r[ix["PERSONAL_OCUPADO"]]),
            "ingresos_xlsx": _num(r[ix["INGRESOS_ACTIVIDAD_ORDINARIA"]]),
            "codigo_ciiu": _k(r[ix["CODIGO CIIU"]]),
            "desc_ciiu": str(r[ix["DESC CIIU"]]).strip() if r[ix["DESC CIIU"]] is not None else "",
            "sector": str(r[ix["NOMBRE_SECTOR"]]).strip() if r[ix["NOMBRE_SECTOR"]] is not None else "",
            "categoria": str(r[ix["CATEGORIA"]]).strip() if r[ix["CATEGORIA"]] is not None else "",
            "tamano": str(r[ix["TAMANO957"]]).strip() if r[ix["TAMANO957"]] is not None else "",
            "latitud": str(y),
            "longitud": str(x),
        }
    print(f"XLSX leido en {time.time()-t0:.1f}s | {len(base_geo)} negocios en buffer (coords+empleo)", flush=True)

    # ── 2) CSV 2026: fechas (matricula/renovacion/cancelacion) + ingresos HASTA 2026 ──
    # Indice de columnas (0-based) del reporte general:
    #  1 numeroInscrito | 3 fechaMatricula | 4 fechaRenovacion | 5 fechaCancelacion
    #  35 ingresosOrdinarios_34
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
            # quedarse con la renovacion mas reciente si hay duplicados
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
    print(f"CSV 2026 cruzado: {len(csv_info)}/{len(base_geo)} negocios del buffer con registro 2026", flush=True)

    # ── 3) Ensamblar consolidado (base_geo = universo del buffer; CSV 2026 actualiza) ──
    registros = []
    for k, g in base_geo.items():
        info = csv_info.get(k)
        # Ingresos: SIEMPRE del XLSX (el CSV 2026 trae la columna financiera vacia).
        _ing = g["ingresos_xlsx"]
        if info is None:
            # negocio en el buffer (2025) sin match en CSV 2026 -> se mantiene con datos del XLSX
            reg = {
                "numeroInscrito": k, "estado": "Registro Activo",
                "fechaMatricula": None, "fechaRenovacion": None, "fechaCancelacion": None,
                "ingresosOrdinarios": _ing, "activoTotal": None,
            }
        else:
            reg = {
                "numeroInscrito": k, "estado": info["estado"],
                "fechaMatricula": info["fechaMatricula"],
                "fechaRenovacion": info["fechaRenovacion"],
                "fechaCancelacion": info["fechaCancelacion"],
                "ingresosOrdinarios": _ing,
                "activoTotal": None,
            }
        reg.update({
            "empleo": g["empleo"],
            "codigo_ciiu": g["codigo_ciiu"], "desc_ciiu": g["desc_ciiu"],
            "sector": g["sector"], "categoria": g["categoria"], "tamano": g["tamano"],
            "latitud": g["latitud"], "longitud": g["longitud"],
        })
        registros.append(reg)

    out = {
        "generado_de": "CSV 2026 (20260929-Reporte General Registro Mercantil.csv) para fechas/ingresos "
                       "HASTA 2026 + XLSX 2025 (registro_mercantil_2025_con_coordenadas.xlsx) para "
                       "coordenadas y empleo (PERSONAL_OCUPADO). Filtrado al buffer de Roosevelt por "
                       "spatial join within del XLSX, cruce por numeroInscrito.",
        "nota": "Linea base intacta + extension 2026 (matriculas/renovaciones/cancelaciones hasta "
                "sep-2026 del CSV). Empleo = PERSONAL_OCUPADO del XLSX; ingresos = "
                "INGRESOS_ACTIVIDAD_ORDINARIA del XLSX (el CSV 2026 trae financieros vacios). "
                "Sin activoTotal -> score DE = establecimientos + ingresos + empleo.",
        "n": len(registros),
        "registros": registros,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"negocios consolidados: {len(registros)} -> {OUT}", flush=True)

    # ── Diagnostico: stock activo + matriculas/empleo por año y trimestre 2026 ──────
    import pandas as pd
    dd = pd.DataFrame(registros)
    dd["fm"] = pd.to_datetime(dd["fechaMatricula"], errors="coerce")
    dd["fc"] = pd.to_datetime(dd["fechaCancelacion"], errors="coerce")
    dd["emp"] = pd.to_numeric(dd["empleo"], errors="coerce")
    for a in [2023, 2024, 2025, 2026]:
        mask = (dd["fm"].dt.year <= a) & (dd["fc"].isna() | (dd["fc"].dt.year > a))
        act = dd[mask]
        print(f"  {a}: stock activo={len(act)} | empleo={act['emp'].where(act['emp']>=0).sum():.0f}", flush=True)
    print("  Matriculas 2026 por trimestre:", flush=True)
    m26 = dd[dd["fm"].dt.year == 2026]
    print("   ", dict(m26["fm"].dt.quarter.value_counts().sort_index()), flush=True)
    print("  Cancelaciones 2026:", int((dd["fc"].dt.year == 2026).sum()), flush=True)


if __name__ == "__main__":
    main()
