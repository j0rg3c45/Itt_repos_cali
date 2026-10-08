"""
Auditoría de privacidad del sitio público.

Verifica que el mapa publicado (github_pages/site/mapa.html) contenga ÚNICAMENTE
la ubicación de los eventos y su tipo, sin filtrar ningún atributo sensible de las
fuentes crudas (dirección, fecha, sexo, edad, nacionalidad, placas, antecedentes...).

Sale con código 1 si detecta una posible fuga (útil para encadenar en CI antes de
publicar). Uso:
    uv run python github_pages/audit_privacy.py
"""
import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent / "site"
MAPA = SITE / "mapa.html"

# Tokens de columnas sensibles que NUNCA deben aparecer en el HTML publicado.
SENSIBLES = [
    "direccion", "direcion", "dire_hecho", "ocupacion", "estado_civ",
    "escolarida", "nacionalid", "feminicidi", "placas", "antecedent",
    "anotacione", "lgtbi", "num_compar", "num_expedi", "identifica",
    "cedula", "razon_soci", "victima", "fecha_hech", "fechah", "hora_hecho",
    r"\bedad\b", r"\bsexo\b",
]
# Tipos permitidos (lo único que puede verse de cada evento)
TIPOS = ["Homicidio", "Hurto", "VIF", "Siniestro", "Riña", "SPA"]


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

    tipos_presentes = [t for t in TIPOS if t in html]

    print("=== AUDITORIA DE PRIVACIDAD DEL MAPA ===")
    print("Atributos sensibles en el HTML:", encontrados or "NINGUNO")
    print("Properties embebidas:", sorted(prop_keys) or "ninguna")
    print("Claves no permitidas (fuera de Id/area):", sorted(no_permitidas) or "NINGUNA")
    print("Tipos de evento presentes:", tipos_presentes)

    if encontrados or no_permitidas:
        print("\n*** ALERTA: posible fuga de datos sensibles — NO publicar ***")
        sys.exit(1)
    print("\nOK: el mapa publica solo ubicacion + tipo. Sin atributos sensibles.")


if __name__ == "__main__":
    main()
