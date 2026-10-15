"""Enriquece (UNA sola vez) el consolidado de Desarrollo Económico de San Fernando
agregando el campo 'empleo' (PERSONAL_OCUPADO) a cada negocio, por match de
numeroInscrito con registro_mercantil_2025_con_coordenadas.xlsx (fuente de empleo
de Cámara de Comercio, todo Cali). Mismo criterio que Ciudad Paraíso.

Por qué: el CSV geocodificado del que salió el consolidado NO trae empleo. El xlsx que
sí lo trae (PERSONAL_OCUPADO) es de todo Cali (~122k filas, 14 MB); leerlo en el notebook
en cada corrida es lento. Aquí se lee UNA vez con calamine y se escribe el empleo dentro
del propio consolidado liviano que el notebook ya lee.

Uso:
    python scripts_educ/add_empleo_de_san_fernando.py
"""
import json
import time

import numpy as np
from python_calamine import CalamineWorkbook

ROOT = "data/itt_Corredor_San_fernando_Yawa"
XLSX = ROOT + "/data_2025_2026/Camara_de_Comercio/registro_mercantil_2025_con_coordenadas.xlsx"
CONS = ROOT + "/4_Dimension_Desarrollo_Economico/registro_mercantil_SF_2023_2026_consolidado.json"


def _k(v):
    s = str(v).replace("=", "").replace('"', "").strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def main():
    t0 = time.time()
    wb = CalamineWorkbook.from_path(XLSX)
    data = wb.get_sheet_by_index(0).to_python(skip_empty_area=True)
    header = [str(h).strip() for h in data[0]]
    i_num = header.index("NUM INSCRITO")
    i_per = header.index("PERSONAL_OCUPADO")
    empleo_map = {}
    for r in data[1:]:
        k = _k(r[i_num])
        try:
            p = float(r[i_per])
        except (TypeError, ValueError):
            p = None
        empleo_map[k] = p
    print(f"Empleo xlsx leido en {time.time()-t0:.1f}s | {len(empleo_map)} negocios con PERSONAL_OCUPADO", flush=True)

    cj = json.load(open(CONS, encoding="utf-8"))
    matched = 0
    for reg in cj["registros"]:
        k = str(reg["numeroInscrito"]).strip()
        e = empleo_map.get(k)
        reg["empleo"] = e   # None (sin dato) o nº de personas ocupadas
        if e is not None and not (isinstance(e, float) and np.isnan(e)):
            matched += 1
    cj["nota"] = (cj.get("nota", "") +
                  " | Empleo (PERSONAL_OCUPADO 2025) agregado por match de numeroInscrito con "
                  "registro_mercantil_2025_con_coordenadas.xlsx (corte 2025, estable en la serie).")
    cj["n_con_empleo"] = matched
    with open(CONS, "w", encoding="utf-8") as f:
        json.dump(cj, f, ensure_ascii=False)
    print(f"Consolidado enriquecido: {matched}/{len(cj['registros'])} negocios con empleo. -> {CONS}", flush=True)


if __name__ == "__main__":
    main()
