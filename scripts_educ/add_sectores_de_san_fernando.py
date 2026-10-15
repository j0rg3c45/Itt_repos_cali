"""Enriquece (UNA sola vez) el consolidado de Desarrollo Económico de San Fernando
agregando a cada negocio su código CIIU y su SECTOR (Salud / Educación / Deporte y
recreación / Otros), por match de numeroInscrito con el registro mercantil 2025 que
trae el CIIU real (DESC CIIU).

Por qué: el CSV geocodificado del consolidado NO trae un CIIU utilizable (código interno
de la Cámara). El xlsx registro_mercantil_2025_con_coordenadas.xlsx sí trae CODIGO CIIU /
DESC CIIU (CIIU rev4). Se lee UNA vez con calamine y se escribe ciiu+sector dentro del
consolidado liviano que el notebook ya lee.

Clasificación por división CIIU (2 primeros dígitos):
  Salud                -> 86, 87, 88 (atención salud humana y asistencia social)
  Educación            -> 85
  Deporte y recreación -> 93 (actividades deportivas y recreativas) + 8541/8542 (enseñanza
                          deportiva/recreativa y cultural)

Uso:
    python scripts_educ/add_sectores_de_san_fernando.py
"""
import json
import time

from python_calamine import CalamineWorkbook

ROOT = "data/itt_Corredor_San_fernando_Yawa"
XLSX = ROOT + "/data_2025_2026/Camara_de_Comercio/registro_mercantil_2025_con_coordenadas.xlsx"
CONS = ROOT + "/4_Dimension_Desarrollo_Economico/registro_mercantil_SF_2023_2026_consolidado.json"


def _k(v):
    s = str(v).replace("=", "").replace('"', "").strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def sector(ciiu):
    div = ciiu[:2] if ciiu else ""
    if div in ("86", "87", "88"):
        return "Salud"
    if div == "85":
        return "Educación"
    if div == "93" or ciiu in ("8541", "8542"):
        return "Deporte y recreación"
    return "Otros"


def main():
    t0 = time.time()
    wb = CalamineWorkbook.from_path(XLSX)
    data = wb.get_sheet_by_index(0).to_python(skip_empty_area=True)
    h = [str(x).strip() for x in data[0]]
    iN, iC, iD = h.index("NUM INSCRITO"), h.index("CODIGO CIIU"), h.index("DESC CIIU")
    ciiu_map, desc_map = {}, {}
    for r in data[1:]:
        k = _k(r[iN])
        ciiu_map[k] = _k(r[iC])
        desc_map[k] = str(r[iD]).strip() if r[iD] is not None else ""
    print(f"CIIU xlsx leido en {time.time()-t0:.1f}s | {len(ciiu_map)} negocios", flush=True)

    cj = json.load(open(CONS, encoding="utf-8"))
    counts = {}
    matched = 0
    for reg in cj["registros"]:
        k = str(reg["numeroInscrito"]).strip()
        ciiu = ciiu_map.get(k)
        reg["ciiu"] = ciiu
        reg["desc_ciiu"] = desc_map.get(k, "")
        sec = sector(ciiu) if ciiu else "Sin clasificar"
        reg["sector"] = sec
        counts[sec] = counts.get(sec, 0) + 1
        if ciiu:
            matched += 1
    cj["nota"] = cj.get("nota", "") + " | CIIU/sector (Salud/Educación/Deporte) agregado del registro mercantil 2025."
    cj["n_con_ciiu"] = matched
    with open(CONS, "w", encoding="utf-8") as f:
        json.dump(cj, f, ensure_ascii=False)
    print(f"Consolidado enriquecido con ciiu+sector ({matched}/{len(cj['registros'])} con CIIU). -> {CONS}")
    print("Distribución por sector:", counts)


if __name__ == "__main__":
    main()
