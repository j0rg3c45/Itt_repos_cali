"""Construye el consolidado de Desarrollo Económico del Corredor Roosevelt, filtrando el
registro mercantil OFICIAL (ciudad completa) al buffer de 100 m de la zona.

Fuente oficial: data/Camara_de_Comercio/registro_mercantil_2025_con_coordenadas.xlsx
(trae X/Y + PERSONAL_OCUPADO + CODIGO CIIU + INGRESOS). Se filtra por spatial join 'within'
al buffer de Roosevelt, se dedup por NUM INSCRITO (ultima renovacion) y se escribe un JSON
liviano que el notebook lee. Mismo criterio que Pulmón de Oriente / San Fernando.

El xlsx oficial NO trae activoTotal ni fechaCancelacion (solo activos renovados), por lo que
el score DE de Roosevelt usa 3 componentes: establecimientos + ingresos + empleo.

Uso:  python scripts_educ/build_de_roosevelt.py
"""
import json
import os
import re
import time

import geopandas as gpd
from shapely.geometry import Point
from python_calamine import CalamineWorkbook

XLSX = "data/Camara_de_Comercio/registro_mercantil_2025_con_coordenadas.xlsx"
POLY = "data/itt_roosevelt/tramos_Roosevelt_Buffer_100.geojson"
OUT = "data/itt_roosevelt/4_Desarrollo_Economico/registro_mercantil_Roosevelt_2023_2026_consolidado.json"

MESES = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
         "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
         "noviembre": 11, "diciembre": 12}


def _fecha_es(v):
    """'23 de enero de 2024' -> '2024-01-23'. Devuelve None si no parsea."""
    if v is None:
        return None
    s = str(v).strip().lower()
    m = re.search(r"(\d{1,2})\s+de\s+([a-záéíóú]+)\s+de\s+(\d{4})", s)
    if m:
        d, mes, a = int(m.group(1)), MESES.get(m.group(2), 0), int(m.group(3))
        if mes:
            return f"{a:04d}-{mes:02d}-{d:02d}"
    m2 = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m2:
        return m2.group(0)
    return None


def _num(v):
    try:
        n = float(v)
        return n if n == n else None
    except (TypeError, ValueError):
        return None


def _k(v):
    s = str(v).replace("=", "").replace('"', "").strip()
    return s[:-2] if s.endswith(".0") else s


def main():
    t0 = time.time()
    wb = CalamineWorkbook.from_path(XLSX)
    data = wb.get_sheet_by_index(0).to_python(skip_empty_area=True)
    h = [str(x).strip() for x in data[0]]
    idx = {name: h.index(name) for name in h}
    iX, iY = idx["X"], idx["Y"]
    iNum = idx["NUM INSCRITO"]
    iMat = idx["Mes, Día, Año de FECHA_MATRICULA"]
    iRen = idx["Mes, Día, Año de FECHA_RENOVACION"]
    iCiiu = idx["CODIGO CIIU"]
    iDesc = idx["DESC CIIU"]
    iPers = idx["PERSONAL_OCUPADO"]
    iIng = idx["INGRESOS_ACTIVIDAD_ORDINARIA"]
    iSec = idx.get("NOMBRE_SECTOR")
    iCat = idx.get("CATEGORIA")
    iTam = idx.get("TAMANO957")
    print(f"xlsx leido en {time.time()-t0:.1f}s | {len(data)-1} filas", flush=True)

    poly = gpd.read_file(POLY).to_crs("EPSG:4326").geometry.union_all()

    registros = {}
    dentro = 0
    for r in data[1:]:
        x, y = _num(r[iX]), _num(r[iY])
        if x is None or y is None or not (-77.6 < x < -76.0 and 3.0 < y < 3.9):
            continue
        if not poly.contains(Point(x, y)):
            continue
        dentro += 1
        k = _k(r[iNum])
        ciiu = _k(r[iCiiu])
        reg = {
            "numeroInscrito": k,
            "estado": "Registro Activo",
            "fechaMatricula": _fecha_es(r[iMat]),
            "fechaRenovacion": _fecha_es(r[iRen]),
            "fechaCancelacion": None,   # el xlsx 2025 solo trae activos renovados
            "ingresosOrdinarios": _num(r[iIng]),
            "activoTotal": None,        # la fuente oficial no trae activo_total
            "empleo": _num(r[iPers]),
            "codigo_ciiu": ciiu,
            "desc_ciiu": str(r[iDesc]).strip() if r[iDesc] is not None else "",
            "sector": str(r[iSec]).strip() if (iSec is not None and r[iSec] is not None) else "",
            "categoria": str(r[iCat]).strip() if (iCat is not None and r[iCat] is not None) else "",
            "tamano": str(r[iTam]).strip() if (iTam is not None and r[iTam] is not None) else "",
            "latitud": str(y),
            "longitud": str(x),
        }
        prev = registros.get(k)
        if prev is None or (reg["fechaRenovacion"] or "") > (prev["fechaRenovacion"] or ""):
            registros[k] = reg

    regs = list(registros.values())
    out = {
        "generado_de": "registro_mercantil_2025_con_coordenadas.xlsx (Camara de Comercio OFICIAL, "
                       "filtrado al buffer de 100 m de Roosevelt por spatial join within)",
        "nota": "1 fila por negocio (ultima renovacion). Empleo = PERSONAL_OCUPADO; "
                "ingresos = INGRESOS_ACTIVIDAD_ORDINARIA (corte unico 2025). La fuente oficial NO "
                "trae activoTotal ni fechaCancelacion -> score DE = establecimientos + ingresos + empleo.",
        "n": len(regs),
        "registros": regs,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    print(f"dentro del buffer: {dentro} | negocios unicos: {len(regs)} -> {OUT}", flush=True)

    # Diagnóstico: stock activo por año (matriculado<=año)
    import pandas as pd
    dd = pd.DataFrame(regs)
    dd["fm"] = pd.to_datetime(dd["fechaMatricula"], errors="coerce")
    for a in [2023, 2024, 2025, 2026]:
        act = dd[dd["fm"].dt.year <= a]
        emp = pd.to_numeric(act["empleo"], errors="coerce").where(lambda s: s >= 0).sum()
        ing = pd.to_numeric(act["ingresosOrdinarios"], errors="coerce").where(lambda s: s > 0).sum()
        print(f"  {a}: stock={len(act)} | empleo={emp:.0f} | ingresos=${ing:,.0f}", flush=True)


if __name__ == "__main__":
    main()
