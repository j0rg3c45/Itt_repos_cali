"""Preprocesa (UNA sola vez) la data pesada de educacion de Cali y deja un JSON
liviano con los indicadores de la IE Republica de Argentina (Barrio Obrero).
El notebook 04_itt_barrio_obrero_5dim solo lee ese JSON (lectura instantanea),
sin depender de descargas de Google Drive (Colab).

Metodo identico a build_educacion_san_fernando.py: CALAMINE (lector Rust) para
parsear los Anexo 6A (~40 MB) en segundos, filtrando por el DANE del colegio.

Fuente: data/Educacion_2026/SIMAT y SIMPADE anonimizado + DUE/
Salida:  data/itt_barrio_obrero/6_Educacion/educacion_BO_2023_2026_consolidado.json
"""
import csv
import json
import os
import time

from python_calamine import CalamineWorkbook

EXT = "data/Educacion_2026/SIMAT y SIMPADE anonimizado + DUE"
OUT = "data/itt_barrio_obrero/6_Educacion/educacion_BO_2023_2026_consolidado.json"

DANES_IE = {"176001005368"}   # IE Republica de Argentina (Barrio Obrero)
GRADOS_EFIC = set(list(range(0, 12)) + [99])   # 0..11 + aceleracion (99)

ANEXO6A = {
    2023: EXT + "/Anexo 6A/12.1 Anexo 6a Diciembre 2023.xlsx",
    2024: EXT + "/Anexo 6A/12.1 Anexo 6a Diciembre 2024.xlsx",
    2025: EXT + "/Anexo 6A/12.1 Anexo 6a Diciembre 2025.xlsx",
    2026: EXT + "/Anexo 6A/3.1 Anexo 6a Marzo 2026.xlsx",   # corte marzo (anio no cerrado)
}
SIMPADE = {
    2023: (EXT + "/SIMPADE/SIMPADE_2023-11.xlsx", "xlsx"),
    2024: (EXT + "/SIMPADE/SIMPADE_2024-11.xlsx", "xlsx"),
    2025: (EXT + "/SIMPADE/SIMPADE_2025-11.csv", "csv"),
}


def _norm(h):
    return str(h).strip().upper().replace(" ", "_") if h is not None else ""


def _rows_calamine(path):
    wb = CalamineWorkbook.from_path(path)
    sheet = wb.get_sheet_by_index(0)
    data = sheet.to_python(skip_empty_area=True)
    return data[0], data[1:]


def _as_str(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v).strip()


def procesar_simat_6a(path, anio):
    t0 = time.time()
    header, rows = _rows_calamine(path)
    hn = [_norm(h) for h in header]
    i_dane = next((k for k, h in enumerate(hn) if "CODIGO_DANE" in h and "SEDE" not in h), None)
    i_sec = hn.index("SECTOR") if "SECTOR" in hn else None
    i_gra = hn.index("GRADO") if "GRADO" in hn else None
    i_rep = hn.index("REPITENTE") if "REPITENTE" in hn else None
    if None in (i_dane, i_sec, i_gra, i_rep):
        raise RuntimeError(f"columnas no encontradas en {os.path.basename(path)}: "
                           f"dane={i_dane} sec={i_sec} gra={i_gra} rep={i_rep}")
    mat = rep = 0
    for r in rows:
        if _as_str(r[i_dane]) not in DANES_IE:
            continue
        if _as_str(r[i_sec]).upper() != "OFICIAL":
            continue
        try:
            g = int(float(r[i_gra]))
        except (TypeError, ValueError):
            continue
        if g not in GRADOS_EFIC:
            continue
        mat += 1
        if _as_str(r[i_rep]).upper() == "S":
            rep += 1
    print(f"  SIMAT {anio}: matricula={mat} repitentes={rep}  ({time.time()-t0:.1f}s)", flush=True)
    return mat, rep


def procesar_simpade(path, fmt, anio):
    t0 = time.time()
    des = 0
    if fmt == "xlsx":
        header, rows = _rows_calamine(path)
        hn = [_norm(h) for h in header]
        i_dane = hn.index("DANE_EE") if "DANE_EE" in hn else None
        i_sec = hn.index("SECTOR") if "SECTOR" in hn else None
        i_gra = hn.index("GRADO") if "GRADO" in hn else None
        if i_dane is None or i_sec is None:
            raise RuntimeError(f"SIMPADE sin DANE_EE/SECTOR: {os.path.basename(path)}")
        for r in rows:
            if _as_str(r[i_dane]) not in DANES_IE:
                continue
            if _as_str(r[i_sec]).upper() != "OFICIAL":
                continue
            grado = _as_str(r[i_gra]).upper() if i_gra is not None else ""
            if "CICLO" in grado or "ADULTO" in grado:
                continue
            des += 1
    else:  # csv
        with open(path, encoding="utf-8-sig", newline="") as f:
            rd = csv.reader(f, delimiter=";")
            header = next(rd)
            hn = [str(h).strip().upper() for h in header]
            i_dane = hn.index("DANE_EE") if "DANE_EE" in hn else None
            i_sec = hn.index("SECTOR") if "SECTOR" in hn else None
            i_gra = hn.index("GRADO") if "GRADO" in hn else None
            if i_dane is None or i_sec is None:
                raise RuntimeError(f"SIMPADE csv sin DANE_EE/SECTOR: {os.path.basename(path)}")
            for r in rd:
                if len(r) <= max(i_dane, i_sec):
                    continue
                if str(r[i_dane]).strip() not in DANES_IE:
                    continue
                if str(r[i_sec]).strip().upper() != "OFICIAL":
                    continue
                grado = str(r[i_gra]).upper() if (i_gra is not None and i_gra < len(r)) else ""
                if "CICLO" in grado or "ADULTO" in grado:
                    continue
                des += 1
    print(f"  SIMPADE {anio}: desertores={des}  ({time.time()-t0:.1f}s)", flush=True)
    return des


def main():
    t_all = time.time()
    print("=== SIMAT Anexo 6A (calamine) — Barrio Obrero ===", flush=True)
    mat, rep = {}, {}
    for a, p in ANEXO6A.items():
        m, r = procesar_simat_6a(p, a)
        mat[a], rep[a] = m, r

    print("=== SIMPADE (calamine/csv) ===", flush=True)
    des = {}
    for a, (p, fmt) in SIMPADE.items():
        des[a] = procesar_simpade(p, fmt, a)
    des[2026] = None   # SIMPADE 2026 no existe (anio no cerrado) -> desercion NaN

    out = {
        "generado_de": "SIMAT Anexo 6A (Dic 2023/2024/2025 + Marzo 2026) + SIMPADE (2023/2024/2025), filtrado al DANE del colegio de Barrio Obrero.",
        "colegios": sorted(DANES_IE),
        "colegios_nombre": {"176001005368": "IE Republica de Argentina"},
        "nota": "Matricula/repitentes: Anexo 6A oficial, grados 0-11 + aceleracion (99). Desertores: SIMPADE oficial, sin ciclos/adultos. 2026 = corte marzo (SIMAT); SIMPADE 2026 no disponible -> desercion NaN.",
        "matricula": {str(a): mat[a] for a in ANEXO6A},
        "repitentes": {str(a): rep[a] for a in ANEXO6A},
        "desertores": {str(a): des[a] for a in [2023, 2024, 2025, 2026]},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nEscrito: {OUT}  (total {time.time()-t_all:.1f}s)", flush=True)
    print(json.dumps(out, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
