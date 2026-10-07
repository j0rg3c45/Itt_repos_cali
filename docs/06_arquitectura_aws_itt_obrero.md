# Migración a AWS — ITT Barrio Obrero como caso de referencia

## Propósito de este documento

Este documento es un **handoff técnico** para que otro agente (o equipo de ingeniería) diseñe y construya en AWS una réplica productiva del cálculo del Índice de Transformación Territorial (ITT), usando como caso de referencia `notebooks/04_itt_barrio_obrero_5dim.ipynb` — el notebook del repo que está metodológicamente limpio y corre de punta a punta sin errores (ver `docs/02_metodologia_itt.md` y `agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md` para el marco conceptual completo).

No es un documento de negocio: asume que quien lo lee va a escribir infraestructura y código, y necesita el detalle exacto del pipeline actual (archivos, columnas, filtros, fórmulas) para no tener que re-derivarlo leyendo 94 celdas de Jupyter.

**Alcance:** solo la zona Barrio Obrero. El patrón es extensible a Roosevelt (corredor con buffer) y Avenida Ciudad de Cali (corredor con 8 tramos), pero esas dos zonas tienen problemas metodológicos activos (ver sección 9) que no se deben replicar sin corregir primero.

---

## 1. Qué hace el notebook hoy, en una frase

Toma ~10 archivos fuente (GeoJSON de eventos georreferenciados + 1 polígono + 4 rasters NDVI + Excel de referencia + Excel de matrícula escolar vía Google Drive), los filtra al polígono de Barrio Obrero (Comuna 9, Cali), calcula 5 dimensiones normalizadas 0-100 por año (2023-2026), las combina en un índice ponderado (ITT), y exporta un Excel de 9 hojas más ~15 gráficas PNG. Se ejecuta manualmente en Google Colab o localmente en Jupyter.

El objetivo de la migración es que este cálculo corra como **pipeline automatizado**, no como notebook manual.

---

## 2. Entradas (fuentes de datos)

Todas bajo `data/itt_barrio_obrero/` en el repo actual. Tamaños pequeños (el barrio es un polígono único, no un corredor con miles de eventos).

| Clave interna | Archivo | Formato | Dimensión | Notas de filtrado |
|---|---|---|---|---|
| `poligono` | `Geojson_Barrio_Obrero.geojson` | GeoJSON | Base espacial | CRS original ESRI:103599 → reproyectar a EPSG:4326 |
| `homicidios` | `1_Dimension_Seguridad/DATIC_homicidios_2023_2026T1_Barrio_O.geojson` | GeoJSON | Seguridad | Campo fecha `fechah`, formato `%m/%d/%Y`. Filtrar `barrio == "BARRIO OBRERO"` (el archivo trae otros barrios) |
| `hurtos` | `1_Dimension_Seguridad/DATIC_hurtos_2023_2026T1_Barrio_O.geojson` | GeoJSON | Seguridad | Campo fecha `fecha_hech`, ISO. Filtrar `nom_barrio == "Barrio Obrero"` |
| `comparendos` | `1_Dimension_Seguridad/DATIC_comparendos_2023_2026T1_Barrio_O.geojson` | GeoJSON | Seguridad/Cohesión | Campo fecha `fecha_hech`. Se filtra dos veces con distinto criterio: `agrupado == "RIÑAS"` + `nom_barrio == "OBRERO"` para riñas; `agrupado == "SUSTANCIAS PSICOACTIVAS"` + `nom_barrio == "OBRERO"` para SPA |
| `cai` | `1_Dimension_Seguridad/CAI_MECAL_CALI_OBRERO.geojson` | GeoJSON | Seguridad (solo mapa) | 1 punto, no entra al score |
| `vif` | `2_Dimensión_Cohesion_Social/DATIC_violencia_intrafamiliar_2023_2026T1_Barrio_O.geojson` | GeoJSON | Cohesión | Campo fecha `fecha_hech`, ISO. Filtrar `nom_barrio == "Barrio Obrero"` |
| `vbg` | `2_Dimensión_Cohesion_Social/VBG_2025_OBRERO.geojson` | GeoJSON | Cohesión (contexto) | No entra al score, solo referencia |
| `siniestros` | `3_Dimension_Movilidad/BD_SINIESTROS_2023_2026_COMUNA_BARRIO_OBRERO.geojson` | GeoJSON | Movilidad | Campo fecha `Fecha`, ISO. Filtrar `barrio == "Barrio Obrero"`. Se subdivide por `Tipo_Confi == "Lesiones"` / `"Mortal"` para lesionados/mortales; el conteo total es "siniestralidad" |
| `arboles` | `5_Entorno_Urbano/Arboles_Dagma_OBRERO.geojson` | GeoJSON | Entorno Urbano | Solo se usa `len(features)` como conteo estático (densidad árb/ha), no serie temporal |
| NDVI | `5_Entorno_Urbano/NDVI_Barrio_Obrero/Barrio_Obrero_ndvi_{2023..2026}.tif` | GeoTIFF | Entorno Urbano | 1 raster por año. Requiere `rasterio` |
| `sedes` | `6_Educacion/Sedes_educativas_oficiales_OBRERO.geojson` | GeoJSON | Educación (solo mapa) | No entra al score |
| `registro_mercantil` | `4_Desarrollo_Economico/registro_mercantil_2025_con_coordenadas_poligono_Barrio_Obrero.geojson` | GeoJSON | Desarrollo Económico | Filtrar `BARRIO == "Barrio Obrero"`. Columnas clave: `INGRESOS_A`, `PERSONAL_O`, `Mes_Dia_An` (fecha de matrícula mercantil en texto español "12 de marzo de 2023"), `TAMANO957` (tamaño empresa) |

Fuentes **externas al repo**, cargadas en tiempo de ejecución (esto es un punto crítico a resolver para AWS — ver sección 6):

| Fuente | Cómo se carga hoy | Dimensión |
|---|---|---|
| SIMPADE (deserción escolar) | Archivos locales ya versionados en `data/referencia/educacion/SIMPADE/SIMPADE_{2023,2024,2025}-*.{xlsx,csv}` | Educación |
| SIMAT Anexo 6A diciembre (matrícula + repitencia) | **Google Drive, por ID de archivo hardcodeado**, descargado con `gdown` solo si `/content` existe (Colab). Localmente esta celda no hace nada y las tasas quedan en NaN | Educación |
| `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx` | Ya versionado en `data/referencia/vivienda/`, usado como proxy de Entorno Urbano para Comuna 9 (ver sección 4.4) | Entorno Urbano |

IE de referencia para educación: DANE `176001005368` (IE República de Argentina), único colegio oficial georreferenciado dentro del polígono.

---

## 3. Parámetros fijos del modelo (deben vivir como config, no hardcodeados en código de negocio)

### 3.1 Pesos por dimensión (`PESOS`, suman 1.00)

```text
Seguridad  = 0.27
Movilidad  = 0.22
DesSocial  = 0.19   # fusión de Cohesión Social + Educación y Desarrollo
EntornoU   = 0.17
DesEco     = 0.15   # Desarrollo Económico
```

> Nota de nomenclatura importante: "DesSocial" en el código **no** es solo Cohesión Social — es el promedio de VIF, Riñas, SPA (eventos de conflictividad) **y** Matrícula, Deserción (educación), fusionados en una sola dimensión. Si se construye un modelo de datos con nombres de dimensión como atributo de negocio, documentar esto explícitamente para que no se interprete como "solo cohesión".

### 3.2 Umbrales fijos `ref_min/ref_max` (`REFS`) — calibrados para zona pequeña tipo barrio

| Indicador | ref_min | ref_max | Inverso | Dimensión |
|---|---:|---:|---|---|
| homicidios | 0 | 5 | Sí | Seguridad |
| hurtos | 10 | 60 | Sí | Seguridad |
| siniestralidad | 1 | 15 | Sí | Movilidad |
| lesionados | 1 | 12 | Sí | Movilidad |
| mortales | 0 | 3 | Sí | Movilidad |
| vif | 1 | 15 | Sí | DesSocial |
| rinas | 0 | 10 | Sí | DesSocial |
| spa | 0 | 10 | Sí | DesSocial |

Fórmula de normalización (idéntica en todo el proyecto):

```python
def score_ref(valor, ref_min, ref_max, inverso):
    if ref_max == ref_min:
        return 100.0
    raw = np.clip((valor - ref_min) / (ref_max - ref_min) * 100, 0, 100)
    return 100 - raw if inverso else raw
```

### 3.3 Valores/umbrales adicionales fuera de `REFS` (dispersos en celdas separadas — consolidar en config)

| Parámetro | Valor | Uso |
|---|---:|---|
| `REF_VERDE_MIN, REF_VERDE_MAX` | 0, 30 | % área verde NDVI → score Entorno Urbano |
| `REF_ARBOLES_MIN, REF_ARBOLES_MAX` | 0, 50 | árboles/ha → score Entorno Urbano |
| `NDVI_UMBRAL` | 0.20 | píxel se considera "verde" si NDVI ≥ este valor |
| `REF_DES_MIN, REF_DES_MAX` | 0, 15 | tasa deserción % → score educación |
| `REF_REP_MIN, REF_REP_MAX` | 0, 20 | tasa repitencia % → score educación |
| `REF_MIN_DEFICIT_CUAL, REF_MAX_DEFICIT_CUAL` | 86.0, 20179.0 | proxy Entorno Urbano (déficit habitacional), fijos sobre las 38 comunas/corregimientos del Excel, no de la muestra local |
| `REF_MIN_DEFICIT_PCT, REF_MAX_DEFICIT_PCT` | 69.8, 96.6 | ídem, componente de intensidad relativa |
| `REF_ENTORNO_U` (fallback) | 39.2 | referente provisional heredado de Pulmón de Oriente, se usa solo si no hay NDVI/árboles |
| `REF_EDUC_DES` (fallback) | 54.9 | ídem, si no hay SIMAT/SIMPADE |
| `REF_DES_ECO` (fallback) | 50.0 | ídem, si no hay Registro Mercantil |
| `REF_VULNERABILIDAD` | 54.1 | dato de contexto (Sub PyE 2025), **no entra al cálculo del ITT** |

### 3.4 Desarrollo Económico — ⚠️ usa normalización relativa, no fija (ver sección 9.2)

```python
REF_EST_MIN, REF_EST_MAX = 0, len(df_de)                                    # total negocios en el dataset
REF_PERS_STOCK_MIN, REF_PERS_STOCK_MAX = 0, df_de['personal_limpio'].sum()  # suma total observada
REF_ING_STOCK_MIN, REF_ING_STOCK_MAX = 0, log1p(df_de['ingresos_limpio'].sum())
```

Esto es min-max calculado desde la propia muestra (el máximo observado define el 100), a diferencia de Seguridad/Movilidad/DesSocial que sí usan umbrales fijos y documentados. **Es una inconsistencia real del notebook de referencia**, no solo de los notebooks problemáticos — ver sección 9.2 para el porqué y qué hacer al respecto antes de automatizar.

---

## 4. Lógica de transformación, por dimensión

### 4.1 Seguridad (peso 27%)

1. Cargar `homicidios`, `hurtos` como GeoJSON → DataFrame de `properties`.
2. Parsear fecha, derivar `año` y `trimestre`.
3. Filtrar por nombre de barrio (ver tabla de la sección 2 — el campo y el valor exacto cambian por archivo).
4. Agregar conteo anual (`groupby('año').size()`, reindexado a `[2023,2024,2025,2026]`, `fill_value=0`) y trimestral.
5. `score_homicidios = score_ref(homicidios, 0, 5, inverso=True)`; igual para hurtos con (10, 60).
6. `score_seguridad = mean(score_homicidios, score_hurtos)`.
7. 2026 es parcial: DATIC solo cubre hasta 2026-Q1 → en la tabla trimestral, trimestres 2026-Q2 a Q4 se ponen en `NaN` explícitamente (no en 0) para no mentir con "cero eventos".

### 4.2 Movilidad (peso 22%)

Mismo patrón que Seguridad sobre `siniestros`, subdividido por `Tipo_Confi` en `lesionados` y `mortales`; `siniestralidad` es el conteo total de registros de siniestros (sin filtrar por tipo). `score_movilidad = mean(score_siniestralidad, score_lesionados, score_mortales)`. 2026: siniestros cubre hasta Q2, por lo que Q3/Q4 2026 quedan en NaN (corte distinto al de Seguridad — **cada fuente tiene su propia fecha de corte real, no asumir que todas llegan al mismo trimestre**).

### 4.3 DesSocial — Cohesión + Educación fusionadas (peso 19%)

Componentes de conflictividad (serie real, trimestral):
- `vif`: conteo anual/trimestral de violencia intrafamiliar.
- `rinas`: comparendos filtrados por `agrupado == "RIÑAS"`.
- `spa`: comparendos filtrados por `agrupado == "SUSTANCIAS PSICOACTIVAS"` (se calcula aparte porque no viene en la tabla trimestral base, se deriva directo de `raw_comp`).

Componentes de educación (serie anual, requiere fuentes externas):
- `matricula`: SIMAT Anexo 6A diciembre, filtrado a `DANE_EE == '176001005368'`, `SECTOR == 'OFICIAL'`, grado en `{0..11, 99}` (99 = aceleración). `score_matricula` normaliza con min/max de la propia serie observada (3 años), no con umbral fijo externo.
- `tasa_desercion = desertores_SIMPADE / matricula_SIMAT * 100`. SIMPADE filtra `DANE_EE == IE`, `SECTOR == 'OFICIAL'`, excluye grados que contengan "CICLO" o "ADULTO".
- `tasa_repitencia = repitentes_SIMAT / matricula_SIMAT * 100`.
- `score_desercion = score_ref(tasa_desercion, 0, 15, inverso=True)`; `score_repitencia` con (0,20) pero **no se usa en el score final de DesSocial** (se calcula pero queda fuera del `nanmean` final — confirmar si es intencional al reconstruir).

Fórmula final:
```python
score_des_social = nanmean([score_vif, score_rinas, score_spa, score_matricula, score_desercion])
```
`nanmean` ignora componentes faltantes — si SIMAT no cargó, la dimensión se calcula solo con los 3 componentes de conflictividad. 2026 no tiene corte educativo comparable → hereda el `score_des_social` de 2025 (carry-forward, no recalculado).

### 4.4 Entorno Urbano (peso 17%)

Dos fuentes independientes, promediadas:

1. **NDVI** (raster anual, `rasterio`): por cada año, leer el `.tif`, excluir `nodata`, calcular tamaño de píxel en m² (el raster está en CRS geográfico, se usa una aproximación `111320 m/° lon × cos(lat) ` y `110540 m/° lat` con `lat≈3.44°` fijo para Cali — **esto es una aproximación geográfica hardcodeada, no una reproyección real a un CRS proyectado**; para producción conviene reproyectar a EPSG:3115/9377 y usar el tamaño de píxel real). `pct_verde = (píxeles con NDVI≥0.20) / (píxeles válidos) × 100`. `score_verde = score_ref(pct_verde, 0, 30, inverso=False)`.
2. **Árboles DAGMA**: conteo estático (no varía por año) de `Arboles_Dagma_OBRERO.geojson`, dividido por el área del barrio en hectáreas (derivada del propio raster NDVI, primer año disponible) → árboles/ha. `score_arboles = score_ref(dens_arboles_ha, 0, 50, inverso=False)`. Mismo score se repite los 4 años (no hay serie temporal de árboles).

`score_entorno_u = mean(score_verde, score_arboles)` por año.

Hay además un **proxy alternativo** (Celda 3B) basado en déficit habitacional de Comuna 9 (`BD_DEFICIT_HABITACIONAL_COM_CORREG_2024.xlsx`), usado como **fallback/contexto** si no hay NDVI, no como el cálculo activo — en la corrida actual el NDVI+árboles sí está disponible y es el que manda. Mantener ambos si se automatiza, con el NDVI como fuente primaria.

### 4.5 Desarrollo Económico (peso 15%)

1. Cargar `registro_mercantil`, filtrar `BARRIO == 'Barrio Obrero'`.
2. Limpiar `INGRESOS_A` (negativo/cero → NaN) y `PERSONAL_O` (negativo → NaN).
3. Parsear `Mes_Dia_An` (fecha en español tipo "12 de marzo de 2023") con regex + diccionario de meses → `anio_mat`, `trim_mat`.
4. Para cada año de corte (2023, 2024, 2025, "2026" = proxy de 2025), construir el **stock acumulado** de negocios matriculados hasta ese año (no el flujo nuevo de ese año): `establecimientos_activos`, `empleabilidad_total` (suma de personal), `ingresos_operacionales` (suma de ingresos), `ingresos_log1p = log1p(ingresos_operacionales)`.
5. Normalizar cada componente con **min-max de la propia serie** (ver sección 3.4 / 9.2) y promediar: `score_des_eco = mean(score_establecimientos, score_empleabilidad, score_ingresos)`.

### 4.6 ITT compuesto

```python
ITT = 0.27*score_seguridad + 0.22*score_movilidad + 0.19*score_des_social \
    + 0.17*score_entorno_u + 0.15*score_des_eco

nivel = 'Activacion'     if ITT < 40
      = 'Consolidacion'  if 40 <= ITT < 60
      = 'Transformacion' if 60 <= ITT < 80
      = 'Escala'         if ITT >= 80
```

Nótese que los nombres de nivel difieren de los de `docs/02_metodologia_itt.md` ("Emergencia/Consolidación/Avance/Transformación") — el código usa "Activación/Consolidación/Transformación/Escala". Usar los nombres del código como fuente de verdad para cualquier UI/reporte automatizado, y señalar la discrepancia documental al equipo.

**Resultado actual (última corrida, commit `47647ce`):**

| Año | Seguridad | Movilidad | DesSocial | EntornoU | DesEco | **ITT** | Nivel |
|---|---:|---:|---:|---:|---:|---:|---|
| 2023 | 0.0 | 0.0 | 0.0 | 60.7 | 91.3 | **24.0** | Activación |
| 2024 | 0.0 | 22.2 | 0.0 | 64.3 | 95.4 | **30.1** | Activación |
| 2025 | 0.0 | 33.3 | 0.0 | 63.0 | 100.0 | **33.0** | Activación |
| 2026 | 40.0 | 67.9 | 0.0 | 57.2 | 100.0 | **50.5** | Consolidación |

(`score_des_social = 0.0` en 2023-2025 en esta tabla específica porque corresponde a una corrida intermedia antes de que la celda ED-3 inyecte los componentes educativos; si se reconstruye el pipeline en orden, el valor final de `score_des_social` para 2023-2025 debe incluir los componentes de matrícula/deserción. Replicar el orden de dependencia de celdas de la sección 5, no solo la fórmula final, para no reproducir este desfase.)

---

## 5. Orden de dependencia del pipeline (DAG real, no el orden visual del notebook)

El notebook tiene celdas de visualización intercaladas entre celdas de cálculo; el DAG de dependencias real es:

```
1. Cargar polígono + GeoJSON crudos (homicidios, hurtos, siniestros, vif, comparendos, árboles, sedes, cai)
2. Filtrar por barrio + parsear fechas → tabla anual + trimestral de Seguridad, Movilidad, VIF, Riñas
3. Calcular SPA desde comparendos (independiente, no viene de la tabla trimestral base)
4. Normalizar Seguridad, Movilidad, (VIF+Riñas+SPA parcial de DesSocial) con REFS fijos → ITT preliminar
   (en este punto EntornoU, Educación y DesEco siguen en sus valores fallback fijos)
5. Entorno Urbano:
   5a. Procesar 4 rasters NDVI → ndvi_mean, pct_verde, verde_m2 por año
   5b. Score NDVI + score árboles (estático) → score_entorno_u real → actualizar base → recalcular ITT
6. Educación:
   6a. Cargar SIMPADE (desertores) — ya local en repo
   6b. Cargar SIMAT Anexo 6A (matrícula, repitentes) — requiere Google Drive, solo funciona en Colab hoy
   6c. Calcular tasas, score_matricula, score_desercion → fusionar con score_vif/rinas/spa → score_des_social final → actualizar base → recalcular ITT
7. Desarrollo Económico:
   7a. Cargar Registro Mercantil, filtrar barrio, parsear fechas español
   7b. Construir stock acumulado por año de corte
   7c. Normalizar con min-max de la propia serie → score_des_eco → actualizar base → recalcular ITT (cálculo final)
8. Exportar Excel de 9 hojas + generar ~15 figuras PNG
```

Este orden importa porque cada bloque **reescribe `base['ITT']` completo**, no solo su propia columna — si se paraleliza sin cuidado (p. ej. como Step Functions en paralelo), hay condiciones de carrera sobre el DataFrame/tabla de resultados. En una reimplementación en AWS, cada bloque (4, 5, 6, 7) debería escribir **solo su propia columna de score** en el almacén curado, y el cálculo del ITT compuesto debe ser el último paso, ejecutado después de que las 4 ramas terminen (fan-in).

---

## 6. Puntos que SÍ o SÍ hay que resolver antes de automatizar (no son opcionales)

1. **SIMAT depende de Google Drive + `/content` (Colab) y no corre fuera de ahí.** Hoy, si no está en Colab, esta celda simplemente imprime "No estamos en Colab" y las tasas de matrícula/deserción quedan en `NaN`. Para AWS: decidir una fuente estable (S3 con los 3 archivos Anexo 6A ya descargados y versionados, como ya se hizo con SIMPADE) en vez de depender de IDs de Google Drive en tiempo de ejecución.
2. **No hay versión por fecha de corte de los datos fuente.** Los GeoJSON de DATIC/siniestros/registro mercantil se sobrescriben en el repo cada vez que se actualizan (ver histórico de commits `233d246 update data obrero`). Un pipeline productivo necesita ingesta versionada (S3 con partición por fecha de carga) para poder auditar "con qué datos se calculó el ITT del mes X".
3. **Las fechas de corte real no son iguales entre fuentes** (DATIC hasta 2026-Q1, siniestros hasta 2026-Q2, Registro Mercantil solo 2025) — cualquier automatización debe tratar esto como metadato explícito por fuente, no asumir una fecha de corte global.
4. **`score_des_eco` usa min-max relativo de la propia serie** (sección 3.4/9.2) — si se automatiza con reingesta periódica del Registro Mercantil, el 100 de "hoy" se recalcula cada vez que llega un nuevo corte, y los scores históricos ya publicados cambiarían retroactivamente. Definir umbrales fijos antes de poner esto en un pipeline con ejecución recurrente.

---

## 7. Propuesta de arquitectura AWS

Patrón general: **ingesta → landing (raw) → transformación por dimensión → curado (scores) → agregación (ITT) → publicación**, con todo on versioned S3 + catálogo, para que sea auditable (requisito explícito del proyecto: "documentar siempre", sección 6.3 de la guía metodológica).

### 7.1 Componentes

| Capa | Servicio AWS | Qué hace aquí |
|---|---|---|
| Ingesta manual/periódica | S3 bucket `itt-raw-{zona}` con prefijos por dimensión y fecha de carga (`s3://itt-raw/barrio_obrero/seguridad/2026-10-02/...`) | Reemplaza las carpetas `data/itt_barrio_obrero/*` del repo. Subida vía consola, CLI o un pequeño formulario/Lambda si los equipos de origen (DATIC, DAGMA, Cámara de Comercio) entregan archivos manualmente, que es el caso hoy |
| Ingesta de SIMAT (reemplaza Google Drive) | S3 `itt-raw/educacion/simat_6a/` | Subir los 3 Anexo 6A directamente a S3 una vez, igual que ya se hizo con SIMPADE en el repo. Elimina la dependencia de Colab |
| Catálogo + validación de esquema | AWS Glue Data Catalog + Glue crawlers (opcional) | Detecta esquema de los GeoJSON/Excel entrantes, útil si las fuentes cambian de columnas entre cortes (ya pasó: `DATIC_hurtos` cambió de tamaño de 6046 a 32 líneas entre commits) |
| Transformación por dimensión | AWS Glue Jobs (PySpark o Python shell) o, dado el volumen pequeño (barrio único, cientos de registros), **Lambda + capa de `geopandas`/`rasterio`** por dimensión | Un job/función por dimensión (Seguridad, Movilidad, DesSocial, EntornoU, DesEco), cada uno como traducción 1:1 de las secciones 4.1-4.5. Esto es más mantenible que un monolito y refleja el DAG real de la sección 5 |
| Orquestación | AWS Step Functions | Estado paralelo (`Parallel`) para las 4 ramas independientes (Seguridad+Movilidad+DesSocial parcial, EntornoU, Educación→DesSocial final, DesEco), con un estado final de agregación (`CalcularITT`) que solo arranca cuando las 4 ramas terminan (fan-in, resuelve el riesgo de condición de carrera de la sección 5) |
| Almacén curado | S3 `itt-curated/barrio_obrero/` en Parquet, particionado por año, **o** una tabla en Aurora PostgreSQL / DynamoDB si se necesita servir resultados a una API con baja latencia | Un registro por `(zona, año, dimensión, indicador, valor, score, fuente, nota_estado)` — este esquema ya existe de facto en las 9 hojas del Excel de la sección 8, solo hay que normalizarlo a tabla |
| Consulta ad-hoc / BI | Amazon Athena sobre el S3 curado | Permite consultas SQL directas sobre los Parquet sin levantar base de datos, útil para analistas que hoy abren el Excel exportado |
| Publicación / reporte | Lambda que regenera el Excel de 9 hojas (misma lógica de la celda 92) + gráficas, o Amazon QuickSight apuntando a Athena para un dashboard vivo en vez de PNGs estáticos | El notebook ya genera ~15 figuras matplotlib — esas se pueden migrar a QuickSight (recomendado para un dashboard que se actualiza solo) o mantenerse como Lambda que genera PNG a S3 si se quiere preservar el estilo visual (paleta Okabe-Ito) tal cual |
| Config de parámetros del modelo | Archivo versionado en S3 o Parámetros en AWS Systems Manager Parameter Store / AppConfig | `PESOS`, `REFS`, umbrales de la sección 3 — **nunca hardcodeados dentro de las Lambdas/Glue jobs**, para poder recalibrar sin redeploy y mantener trazabilidad de cambios (regla explícita de la metodología: "documentar siempre" cada ref_min/ref_max) |
| Orquestación temporal | Amazon EventBridge Scheduler | Dispara el Step Functions cuando hay nueva data (ideal: EventBridge rule sobre `s3:ObjectCreated` en el bucket raw) o en cadencia fija (ej. mensual, alineado a la frecuencia real de actualización de DATIC) |
| IaC | AWS CDK (Python, para reusar el mismo lenguaje que el notebook) o Terraform | Todo lo anterior debe quedar declarado como código, no clickops, para poder replicar el mismo patrón en Roosevelt y Avenida Ciudad de Cali después |
| Permisos | IAM roles de mínimo privilegio por función (un rol de ejecución por Lambda/Glue job, con acceso de lectura solo a su prefijo S3 de entrada y escritura solo a su prefijo de salida) | El dato es sensible (homicidios, VIF georreferenciados) — restringir acceso de lectura al bucket raw a los roles del pipeline, no a usuarios finales |

### 7.2 Por qué Lambda y no Glue/EMR para este caso puntual

Barrio Obrero es un polígono único con cientos de eventos por indicador (no miles ni millones) y 4 archivos raster pequeños. Esto cabe cómodamente en el límite de memoria/tiempo de Lambda (hasta 10 GB RAM / 15 min) empaquetando `geopandas` y `rasterio` como container image de Lambda (no como capa zip, por el tamaño de las dependencias geoespaciales). Reservar Glue/EMR para cuando se escale a Avenida Ciudad de Cali con sus 8 tramos y rasters más grandes, o si se agregan más zonas con volumen mayor.

### 7.3 Diagrama de flujo (texto)

```
[Fuentes externas: DATIC, DAGMA, Cámara Comercio, SIMAT/SIMPADE]
        │  (carga manual o automatizada)
        ▼
[S3 itt-raw/barrio_obrero/{dimension}/{fecha_carga}/...]
        │
        ▼ (EventBridge: ObjectCreated o cron)
[Step Functions: ITT-BarrioObrero-Pipeline]
        │
        ├─▶ [Lambda: Seguridad]      ──┐
        ├─▶ [Lambda: Movilidad]      ──┤
        ├─▶ [Lambda: EntornoU]       ──┤─▶ (fan-in)
        ├─▶ [Lambda: DesSocial]      ──┤      │
        │     (necesita SIMAT/SIMPADE)─┤      ▼
        └─▶ [Lambda: DesEco]         ──┘  [Lambda: CalcularITT]
                                              │
                                              ▼
                              [S3 itt-curated/barrio_obrero/ (Parquet)]
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        ▼                     ▼                     ▼
                 [Athena: consulta SQL] [QuickSight: dashboard] [Lambda: export Excel 9 hojas → S3]
```

---

## 8. Esquema de datos curados (derivado directo de las 9 hojas del Excel actual)

Para que el otro agente no tenga que inferir el modelo de datos desde cero, estas son las 9 "tablas" que ya produce el notebook (celda 92) y que deberían mapearse 1:1 a tablas/particiones Parquet o Athena:

1. `ITT_Resumen` — una fila por año: scores de las 5 dimensiones + ITT + nivel + nota de estado (real/parcial).
2. `ITT_Trimestral` — serie trimestral del ITT y sus componentes (depende de `df_evol`, construida en celdas del dashboard).
3. `Seguridad` — homicidios, hurtos (conteo + score) por año.
4. `Movilidad` — siniestralidad, lesionados, mortales (conteo + score) por año.
5. `Cohesion_Social` — vif, riñas, spa (conteo + score) por año. (Nombre de hoja no incluye el componente educativo, aunque `score_des_social` en `ITT_Resumen` sí lo tiene — inconsistencia a resolver en el modelo de datos nuevo: separar explícitamente "Cohesión" de "Educación" como sub-tablas de `DesSocial`.)
6. `Entorno_Urbano` — ndvi_mean, pct_verde, area_verde_m2, densidad_arboles, score.
7. `Educacion` — matrícula, desertores, repitentes, tasas, score.
8. `Desarrollo_Economico` — establecimientos activos, empleabilidad, ingresos, score, tipo_dato (Real/Proxy retrospectivo/Proxy referencial).
9. `Indicadores_Trimestrales` — tabla raw trimestral de Seguridad/Movilidad/Cohesión, con NaN explícito en los trimestres sin cobertura de la fuente.

Cada fila de las hojas 3-8 ya trae una columna `nota_estado` (`'Real'`, `'Parcial Q1-Q2'`, `'Proxy referencial = 2025'`, etc.) — **preservar este campo de linaje/calidad de dato en el modelo de AWS**, es la única trazabilidad que el proyecto tiene hoy de qué número es dato real vs. proxy vs. referencial.

---

## 9. Problemas metodológicos conocidos — no replicar sin decisión explícita del usuario

### 9.1 Nomenclatura "DesSocial"
Ya cubierto en 3.1. No es un bug, pero sin este documento un agente nuevo lo leería como un error.

### 9.2 Desarrollo Económico usa min-max relativo de la propia muestra
A diferencia de Seguridad/Movilidad que usan `REFS` fijos y documentados (sección 3.2), Desarrollo Económico (sección 3.4) calcula `ref_max` como el máximo/total observado en el propio dataset. Esto significa:
- El año más reciente con datos completos (2025) **siempre** sale con score ≈100, por construcción, no porque el desempeño sea objetivamente óptimo.
- Si se automatiza con reingesta periódica del Registro Mercantil, cada nueva corrida redefine el 100 y los scores históricos ya publicados cambian retroactivamente — inaceptable para un índice que se usa para comparar "antes vs. después" de una intervención pública.
- **Antes de automatizar esta dimensión**, se necesita que el usuario (o el equipo metodológico) defina umbrales fijos de `establecimientos_activos`, `empleabilidad_total` e `ingresos_log1p` igual que se hizo para Seguridad/Movilidad, probablemente calibrados con benchmark de otras comunas o un crecimiento histórico razonable, no con el máximo de los propios datos de Barrio Obrero.

### 9.3 No replicar el patrón de Avenida Ciudad de Cali (notebook 06)
Ese notebook sí tiene el mismo problema de min-max relativo pero aplicado a **todas** las dimensiones (Seguridad, Movilidad, etc.), no solo a Desarrollo Económico, y además mezcla un año parcial (2026, solo ~Q1) con años completos dentro del mismo rango de normalización, lo que produce mejoras artificiales en 2026 en casi todos los tramos. Si el objetivo final es construir el pipeline AWS genérico para las 3 zonas, Barrio Obrero (este documento) es la base correcta; Avenida Ciudad de Cali necesita corregirse metodológicamente antes de generalizar el patrón.

### 9.4 Roosevelt (notebook 05) tiene un error de ejecución activo
`KeyError: 'negocios_nuevos'` en la celda de visualización de Desarrollo Económico, y dos celdas con lógica distinta y conflictiva para `score_des_eco` cuyos resultados no corresponden a una sola corrida lineal. Si se extiende el pipeline AWS a Roosevelt, la lógica de Desarrollo Económico debe reconstruirse desde una sola fuente de verdad (revisar con el usuario cuál de las dos celdas es la vigente), no traducirse tal cual del notebook.

---

## 10. Checklist de implementación sugerido (orden de trabajo)

1. Definir el esquema de las 9 tablas curadas (sección 8) como contrato de datos (JSON Schema o definición de tabla Glue).
2. Subir a S3 los insumos actuales de `data/itt_barrio_obrero/` tal cual existen hoy, con partición por fecha de carga, como primera "foto" versionada.
3. Resolver el punto 9.2 (umbrales fijos de Desarrollo Económico) con el usuario antes de escribir el Lambda correspondiente — es el único bloqueador metodológico real de esta zona.
4. Migrar SIMAT a S3 (eliminar dependencia de Google Drive/Colab).
5. Traducir las secciones 4.1-4.5 a 5 funciones Lambda independientes, cada una probada contra los valores de la tabla de la sección 4.6 como caso de regresión (si la Lambda de Seguridad da otro número para 2023 que no sea consistente con el recálculo completo, hay un error de traducción).
6. Montar el Step Functions con fan-out/fan-in como en el diagrama de 7.3.
7. Escribir el curado a Parquet en S3 con el esquema de la sección 8, incluyendo siempre el campo `nota_estado`.
8. Conectar Athena + (QuickSight o el export Excel vía Lambda) para paridad de reporte con lo que el usuario ya usa hoy.
9. Solo después de validar Barrio Obrero end-to-end, extender el mismo patrón a Roosevelt (corrigiendo 9.4) y Avenida Ciudad de Cali (corrigiendo 9.3).
