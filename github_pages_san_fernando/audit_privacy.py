"""
Auditoría de privacidad del sitio público de San Fernando.

Verifica que el mapa (github_pages_san_fernando/site/mapa.html):
  1. NO contenga atributos sensibles de las fuentes crudas.
  2. NO embeba properties distintas de la geometría.
  3. VIF/VBG NO aparezcan como PUNTOS (tooltip de marcador) — solo como heatmap.

Sale con código 1 si detecta una posible fuga (para encadenar en CI antes de publicar).

Uso:
    uv run python github_pages_san_fernando/audit_privacy.py
"""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent / "site"
MAPA = SITE / "mapa.html"

SENSIBLES = [
    "direccion", "direcion", "dire_hecho", "ocupacion", "estado_civ",
    "escolarida", "nacionalid", "feminicidi", "placas", "antecedent",
    "anotacione", "lgtbi", "num_compar", "num_expedi", "identifica",
    "cedula", "razon_soci", "razonsocial", "numeroinscrito", "victima",
    "fecha_hech", "fechah", "hora_hecho", r"\bedad\b", r"\bsexo\b",
]
TIPOS_PUNTO_OK = ["Homicidio", "Hurto", "Siniestro", "Riña", "SPA"]


def main():
    if not MAPA.exists():
        print(f"[ERROR] No existe {MAPA}. Genera el mapa con build_map.py primero.")
        sys.exit(1)
    html = MAPA.read_text(encoding="utf-8")

    encontrados = sorted({t for t in SENSIBLES if re.search(t, html, re.IGNORECASE)})

    prop_keys = set()
    for b in re.finditer(r'"properties"\s*:\s*\{([^}]*)\}', html):
        prop_keys.update(re.findall(r'"([^"]+)"\s*:', b.group(1)))
    no_permitidas = prop_keys - {"Id", "area"}

    # VIF/VBG NO deben aparecer como tooltip de marcador (punto). Como heatmap sí (ok).
    # Un CircleMarker lleva "tooltip": "VIF". Buscamos ese patrón de punto.
    vif_como_punto = bool(re.search(r'"tooltip"\s*:\s*"VIF', html)) or \
                     bool(re.search(r'"tooltip"\s*:\s*"VBG', html))

    tipos_presentes = [t for t in TIPOS_PUNTO_OK if f'"tooltip": "{t}' in html or t in html]

    print("=== AUDITORIA DE PRIVACIDAD DEL MAPA (San Fernando) ===")
    print("Atributos sensibles en el HTML:", encontrados or "NINGUNO")
    print("Properties embebidas:", sorted(prop_keys) or "ninguna")
    print("Claves no permitidas (fuera de Id/area):", sorted(no_permitidas) or "NINGUNA")
    print("VIF/VBG como PUNTO (prohibido):", "SÍ" if vif_como_punto else "NO (correcto: solo heatmap)")
    print("Tipos de evento como punto:", tipos_presentes)

    fuga = bool(encontrados or no_permitidas or vif_como_punto)
    if fuga:
        print("\n*** ALERTA: posible fuga de datos sensibles — NO publicar ***")
        if vif_como_punto:
            print("    -> VIF/VBG debe ir SOLO como mapa de calor, nunca como punto.")
        sys.exit(1)
    print("\nOK: mapa publica solo ubicacion + tipo; VIF/VBG solo heatmap. Sin atributos sensibles.")


if __name__ == "__main__":
    main()
