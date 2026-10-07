# Datos — ITT Avenida Ciudad de Cali

Corredor vial Avenida Ciudad de Cali, 8 tramos con buffer 100 m, ~4.5 km.  
Periodo: 2023–2026 T1.

## Archivos versionados en este directorio

| Archivo ZIP | Contenido | Extrae a (Colab) |
|---|---|---|
| `Geojson_Ciudad_de_Cali (1).zip` | Poligono corredor + capas estaticas (VBG, arboles, sedes educativas, CAI/MECAL) | `/content/Geojson_Ciudad_de_Cali/` |
| `geojson_filtrado_ciudad_de_Cali_100m.zip` | DATIC: homicidios, hurtos, VIF, comparendos 2023-2026 T1 | `/content/geojson_filtrado_ciudad_de_Cali_100m/` |
| `geojson_Movilidad_ciudad_de_Cali_100m.zip` | Siniestros viales 2023-2025 filtrados al buffer 100m | `/content/movilidad_acc/geojson_filtrado_ciudad_de_Cali_100m/` |

## Archivos clave por ZIP

### ZIP1 — Geojson_Ciudad_de_Cali (1).zip
- `ciudad_de_Cali_100m.geojson` — poligono corredor (8 tramos, campo `tramo` con orden geografico norte=1 → sur=8)
- `VBG_2025_tramos.geojson`
- `arboles_tramos.geojson`
- `Sedes_educativas_oficiales_tramos.geojson`
- `CAI_MECAL_CALI_tramos.geojson`

### ZIP2 — geojson_filtrado_ciudad_de_Cali_100m.zip (DATIC 2023-2026 T1)
- `DATIC_homicidios_2023_2026T1_filtrado_ciudad_de_Cali_100m.geojson`
- `DATIC_hurtos_2023_2026T1_filtrado_ciudad_de_Cali_100m.geojson`
- `DATIC_violencia_intrafamiliar_2023_2026T1ciudad_de_Cali_100m.geojson`
- `DATIC_comparendos_2023_2026T1_filtrado_ciudad_de_Cali_100m.geojson`

### ZIP3 — geojson_Movilidad_ciudad_de_Cali_100m.zip (siniestros actualizados)
- `BD_SINIESTROS_2023_2025_COMUNA_BARRIO_4326_filtrado_ciudad_de_Cali_100m.geojson` — 745 eventos, campos `Fecha`, `Tipo_Confi` (Lesiones/Daños/Mortal), geometry Point WGS84
- `BD_COMPARENDOS_2025_COMUNA_BARRIO_filtrado_ciudad_de_Cali_100m.geojson` — no usado actualmente en calculo

## Nota sobre tramos

El campo `tramo` del archivo `ciudad_de_Cali_100m.geojson` contiene la numeracion geografica real (1=norte, 8=sur).
El orden de las geometrias en el archivo NO coincide con el orden geografico.
Siempre usar `gdf_tramos['_tramo_num'] = gdf_tramos['tramo'].astype(int)` para etiquetas correctas.

**T8 (extremo sur) tiene 0 siniestros en ZIP3** — dato real, no error de codigo.

## Por que ZIP3 extrae a carpeta separada

ZIP3 contiene internamente la misma carpeta `geojson_filtrado_ciudad_de_Cali_100m/` que ZIP2.
Se extrae a `/content/movilidad_acc/` para evitar sobreescribir los archivos DATIC de ZIP2.
