"""Preprocesa (UNA sola vez) SIMAT (Anexo 6A) + SIMPADE del repo OFICIAL de educación,
filtrando a los colegios dentro del polígono de Pulmón de Oriente, y deja un JSON liviano
que el notebook lee al instante. Mismo flujo que San Fernando (calamine, rápido).

Colegios (DANE) dentro del polígono de Pulmón de Oriente (spatial join de sedes, aprobado):
  Gabriela Mistral, Nuevo Latir, Llano Verde, Santa Rosa, Jesús Villafañe Franco,
  Humberto Jordán Mazuera, Monseñor Ramón Arcila, La Anunciación, Bartolomé Loboguerrero,
  Siete de Agosto.

Uso:  python scripts_educ/build_educacion_pulmon_oriente.py
"""
import csv
import json
import os
import time

from python_calamine import CalamineWorkbook

EXT = "data/Educacion_2026/SIMAT y SIMPADE anonimizado + DUE"
OUT = "data/itt_pulmon_oriente/6_Dimension_Educacion/educacion_PO_consolidado.json"

DANES_IE = {
    "176001017374": "IE Gabriela Mistral",
    "176001043791": "IE Nuevo Latir",
    "176001800052": "IE Llano Verde",
    "176001025946": "IE Santa Rosa",
    "176001024273": "IE Jesús Villafañe Franco",
    "176001020693": "IE Humberto Jordán Mazuera",
    "176001027001": "IE Monseñor Ramón Arcila",
    "176001014359": "IE La Anunciación",
    "176001003161": "IE Bartolomé Loboguerrero",
    "176001005970": "IE Siete de Agosto",
}
DANES = set(DANES_IE)
GRADOS_EFIC = set(list(range(0, 12)) + [99])

ANEXO6A = {
    2023: EXT + "/Anexo 6A/12.1 Anexo 6a Diciembre 2023.xlsx",
    2024: EXT + "/Anexo 6A/12.1 Anexo 6a Diciembre 2024.xlsx",
    2025: EXT + "/Anexo 6A/12.1 Anexo 6a Diciembre 2025.xlsx",
    2026: EXT + "/Anexo 6A/3.1 Anexo 6a Marzo 2026.xlsx",
}
SIMPADE = {
    2023: (EXT + "/SIMPADE/SIMPADE_2023-11.xlsx", "xlsx"),
    2024: (EXT + "/SIMPADE/SIMPADE_2024-11.xlsx", "xlsx"),
    2025: (EXT + "/SIMPADE/SIMPADE_2025-11.csv", "csv"),
}


def _norm(h):
    return str(h).strip().upper().replace(" ", "_") if h is not None else ""


def _rows(path):
    wb = CalamineWorkbook.from_path(path)
    data = wb.get_sheet_by_index(0).to_python(skip_empty_area=True)
    return data[0], data[1:]


def _s(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def simat(path):
    header, rows = _rows(path)
    hn = [_norm(h) for h in header]
    i_dane = next((k for k, h in enumerate(hn) if "CODIGO_DANE" in h and "SEDE" not in h), None)
    i_sec = hn.index("SECTOR") if "SECTOR" in hn else None
    i_gra = hn.index("GRADO") if "GRADO" in hn else None
    i_rep = hn.index("REPITENTE") if "REPITENTE" in hn else None
    mat = rep = 0
    for r in rows:
        if _s(r[i_dane]) not in DANES:
            continue
        if _s(r[i_sec]).upper() != "OFICIAL":
            continue
        try:
            g = int(float(r[i_gra]))
        except (TypeError, ValueError):
            continue
        if g not in GRADOS_EFIC:
            continue
        mat += 1
        if _s(r[i_rep]).upper() == "S":
            rep += 1
    return mat, rep


def simpade(path, fmt):
    des = 0
    if fmt == "xlsx":
        header, rows = _rows(path)
        hn = [_norm(h) for h in header]
        i_dane = hn.index("DANE_EE") if "DANE_EE" in hn else None
        i_sec = hn.index("SECTOR") if "SECTOR" in hn else None
        i_gra = hn.index("GRADO") if "GRADO" in hn else None
        for r in rows:
            if _s(r[i_dane]) not in DANES or _s(r[i_sec]).upper() != "OFICIAL":
                continue
            grado = _s(r[i_gra]).upper() if i_gra is not None else ""
            if "CICLO" in grado or "ADULTO" in grado:
                continue
            des += 1
    else:
        with open(path, encoding="utf-8-sig", newline="") as f:
            rd = csv.reader(f, delimiter=";")
            hn = [str(h).strip().upper() for h in next(rd)]
            i_dane = hn.index("DANE_EE") if "DANE_EE" in hn else None
            i_sec = hn.index("SECTOR") if "SECTOR" in hn else None
            i_gra = hn.index("GRADO") if "GRADO" in hn else None
            for r in rd:
                if len(r) <= max(i_dane, i_sec) or str(r[i_dane]).strip() not in DANES:
                    continue
                if str(r[i_sec]).strip().upper() != "OFICIAL":
                    continue
                grado = str(r[i_gra]).upper() if (i_gra is not None and i_gra < len(r)) else ""
                if "CICLO" in grado or "ADULTO" in grado:
                    continue
                des += 1
    return des


def main():
    t0 = time.time()
    print("=== SIMAT Anexo 6A (calamine) — Pulmón de Oriente ===", flush=True)
    mat, rep = {}, {}
    for a, p in ANEXO6A.items():
        m, r = simat(p)
        mat[a], rep[a] = m, r
        print(f"  {a}: matricula={m} repitentes={r}", flush=True)
    print("=== SIMPADE ===", flush=True)
    des = {}
    for a, (p, fmt) in SIMPADE.items():
        des[a] = simpade(p, fmt)
        print(f"  {a}: desertores={des[a]}", flush=True)
    des[2026] = None   # SIMPADE 2026 no existe (año no cerrado)

    out = {
        "generado_de": "SIMAT Anexo 6A (Dic 2023/2024/2025 + Marzo 2026) + SIMPADE (2023/2024/2025) del repo oficial, filtrado a los colegios dentro del poligono de Pulmon de Oriente.",
        "colegios": sorted(DANES),
        "colegios_nombre": DANES_IE,
        "nota": "Matricula/repitentes: Anexo 6A oficial, grados 0-11 + aceleracion (99). Desertores: SIMPADE oficial, sin ciclos/adultos. 2026 = corte marzo (SIMAT); SIMPADE 2026 no disponible -> NaN.",
        "matricula": {str(a): mat[a] for a in ANEXO6A},
        "repitentes": {str(a): rep[a] for a in ANEXO6A},
        "desertores": {str(a): des[a] for a in [2023, 2024, 2025, 2026]},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nEscrito: {OUT}  (total {time.time()-t0:.1f}s)", flush=True)
    print(json.dumps({k: out[k] for k in ("matricula", "repitentes", "desertores")}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
