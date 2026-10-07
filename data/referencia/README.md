# Datos de referencia

Usar esta carpeta para guardar insumos comunes a los tres ITT:

- Catalogos.
- Scores de referencia.
- Poligonos base.
- Limites administrativos.
- Diccionarios de variables.
- Parametros generales de comparacion.

## Archivos disponibles

| Archivo | Estado | Observaciones |
|---|---|---|
| `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx` | Usado experimentalmente en notebook 03 | Proxy de Entorno Urbano con Comuna 9 para Barrio Obrero. Corte anual 2024 unicamente |
| `BD_PREDIOS_TITULADOS 2023-2025 (1).xlsx` | En analisis, no en calculo | Indicador de formalizacion predial, pendiente de resolver equivalencia territorial |
| `BD_SUBSIDIOS_MEJORAMIENTO_VIV_AÑOS_2024_2025 (1).xlsx` | En analisis, no en calculo | Subsidios de mejoramiento de vivienda 2024-2025 |
| `bienestar_RA2026_base_limpia.xlsx` | Descartado para ITT | Registro de Atencion SBS 2026 — 12.937 personas en programas sociales. No apto: solo 2026, 72% sin comuna, mide asistencia no condicion territorial |

## Notas de uso

- El deficit habitacional es el mejor candidato actual para proxy de Entorno Urbano; ya se usa en `03_itt_barrio_obrero.ipynb`.
- No incorporar predios titulados ni subsidios al calculo sin resolver primero la equivalencia territorial (comuna vs barrio vs corredor buffer).
- El archivo de bienestar puede revisarse en el futuro si se resuelve el problema de georeferenciacion (72% sin comuna).
