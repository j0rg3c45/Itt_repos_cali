# Metodologia ITT — Barrio Obrero | Cali

**Zona:** Barrio Obrero — Comuna 9, Cali  
**Periodo analizado:** 2023 – 2025 (trimestral donde aplica)  
**Notebook:** `notebooks/03_itt_barrio_obrero.ipynb`

---

## 1. Estructura general del ITT

El **Indice de Transformacion Territorial (ITT)** agrega 6 dimensiones ponderadas en una escala de 0 a 100, donde valores mayores indican mejores condiciones territoriales.

### Formula ITT (6 dimensiones)

```
ITT = 0.27 * Seguridad
    + 0.22 * Movilidad
    + 0.09 * Cohesion Social
    + 0.17 * Entorno Urbano
    + 0.10 * Educacion y Desarrollo
    + 0.15 * Desarrollo Economico
```

### Niveles de clasificacion

| Rango | Nivel |
|---|---|
| 0 – 40 | Emergencia |
| 40 – 60 | Consolidacion |
| 60 – 80 | Avance |
| 80 – 100 | Transformacion |

---

## 2. Normalizacion de indicadores

Todos los indicadores se convierten a escala 0–100 mediante umbrales fijos calibrados con la serie historica de la zona:

```python
def score_ref(valor, ref_min, ref_max, inverso=False):
    raw = clip((valor - ref_min) / (ref_max - ref_min) * 100, 0, 100)
    return (100 - raw) if inverso else raw
```

- **Inverso = True**: indicadores negativos (criminalidad, accidentes). Menos casos = mejor score.
- **Inverso = False**: indicadores positivos (negocios, empleos). Mas = mejor score.
- Los refs son anuales. Para el calculo trimestral se dividen por 4 (`REFS_Q`).

---

## 3. Dimensiones

### 3.1 Seguridad — Peso: 27%

Mide la incidencia de criminalidad en el territorio.

| Indicador | Fuente | Ref Min | Ref Max | Tipo |
|---|---|---:|---:|---|
| Homicidios anuales | DATIC — Delitos | 0 | 5 | Inverso |
| Hurtos anuales | DATIC — Delitos | 10 | 60 | Inverso |

**Fuente:** Sistema de Informacion DATIC de la Secretaria de Seguridad de Cali. GeoJSON de hechos delictivos georreferenciados y filtrados al poligono del Barrio Obrero.

**Calculo:**
```
score_seguridad = (score_homicidios + score_hurtos) / 2
```

---

### 3.2 Movilidad — Peso: 22%

Mide la siniestralidad vial en el territorio.

| Indicador | Fuente | Ref Min | Ref Max | Tipo |
|---|---|---:|---:|---|
| Siniestros viales anuales | DATIC — Accidentes | 1 | 15 | Inverso |
| Accidentes con lesionados anuales | DATIC — Accidentes | 1 | 12 | Inverso |
| Accidentes mortales anuales | DATIC — Accidentes | 0 | 3 | Inverso |

**Fuente:** Sistema DATIC — registros de accidentalidad vial georreferenciados y filtrados al poligono del Barrio Obrero.

**Calculo:**
```
score_movilidad = (score_siniestralidad + score_lesionados + score_mortales) / 3
```

---

### 3.3 Cohesion Social — Peso: 9%

Mide la conflictividad social y el consumo de sustancias en el territorio.

| Indicador | Fuente | Ref Min | Ref Max | Tipo |
|---|---|---:|---:|---|
| VIF — Violencia Intrafamiliar anual | DATIC — Delitos | 1 | 15 | Inverso |
| Rinas / Conflictividad anual | DATIC — Delitos | 0 | 10 | Inverso |
| SPA — Comparendos Sust. Psicoactivas anual | DATIC — Comparendos | 0 | 10 | Inverso |

**Fuente:**
- VIF y Rinas: GeoJSON de delitos DATIC filtrado al poligono, categoria `agrupado`.
- SPA: GeoJSON de comparendos DATIC filtrado al poligono, categoria `agrupado == 'SUSTANCIAS PSICOACTIVAS'`. Se computa directamente desde `raw_comp` ya que no es un delito sino un comparendo.

**Referente adicional (contexto):** `REF_VULNERABILIDAD = 54.1` — score de vulnerabilidad socioeconmica del ITT Pulmon de Oriente. Se usa como referencia de contexto pero **no entra al calculo del score**.

**Calculo:**
```
score_cohesion = (score_vif + score_rinas + score_spa) / 3
```

---

### 3.4 Entorno Urbano — Peso: 17%

Mide la calidad del entorno fisico y ambiental del territorio a partir de dos indicadores con datos reales del poligono del Barrio Obrero.

**Fuentes:**
- **Rasters NDVI** (archivos `.tif` por ano, 2023–2026): imagenes de indice de vegetacion de diferencia normalizada sobre el poligono del barrio.
- **Inventario de arboles DAGMA** (GeoJSON 2025): 151 arboles georreferenciados dentro del poligono.

**Indicadores y normalizacion:**

| Indicador | Descripcion | Ref Min | Ref Max | Tipo |
|---|---|---:|---:|---|
| % area verde NDVI | Porcentaje del barrio con NDVI >= 0.20 | 0% | 30% | Positivo |
| Densidad de arboles | Arboles por hectarea (DAGMA) | 0 | 50 arb/ha | Positivo |

- **NDVI:** Para cada ano se lee el raster, se cuentan los pixeles con NDVI >= 0.20 (umbral de vegetacion), se calcula el area en m² y se expresa como porcentaje del area total del barrio. Este indicador varia por ano.
- **Arboles DAGMA:** Se calcula la densidad `N_arboles / area_ha`. Este valor es estatico (unico GeoJSON 2025) y se aplica igual a todos los anos.

**Calculo del score compuesto (anual):**
```
score_verde    = score_ref(pct_verde,    0, 30,  inverso=False)
score_arboles  = score_ref(dens_arb_ha,  0, 50,  inverso=False)
score_entorno_u = (score_verde + score_arboles) / 2
```

El score resultante es **anual** (varia segun el NDVI de cada ano) y se extiende plano a los 4 trimestres del mismo ano en la serie trimestral. El valor referencial usado en el ITT es aproximadamente **39.2**, derivado de esta formula con los datos del poligono.

---

### 3.5 Educacion y Desarrollo — Peso: 10%

Mide los indicadores educativos de la unica institucion educativa oficial dentro del poligono del Barrio Obrero: **IE Republica de Argentina** (DANE `176001005368`).

**Fuentes:**
- **SIMAT** — Anexo 6A corte diciembre: matricula total y repitentes por grado.
- **SIMPADE** — corte noviembre: estudiantes desertores por mes de retiro.
- Grados validos: 0 a 11 + Aceleracion del Aprendizaje (se excluyen adultos, PFC, jardin).

**Acceso a los archivos:**

| Archivo | Ubicacion | Notas |
|---|---|---|
| SIMPADE 2023 | `data/referencia/educacion/SIMPADE/SIMPADE_2023-11.xlsx` | Repo local |
| SIMPADE 2024 | `data/referencia/educacion/SIMPADE/SIMPADE_2024-11.xlsx` | Repo local |
| SIMPADE 2025 | `data/referencia/educacion/SIMPADE/SIMPADE_2025-11.csv` | Repo local |
| SIMAT 6A dic 2023 | Google Drive (descarga automatica en Colab) | ID: `196frGLmnvMgXR_ZD--IqdRcaEGDrVoME` |
| SIMAT 6A dic 2024 | Google Drive (descarga automatica en Colab) | ID: `1DEkO7Das1dcEt7qE-gJKHGJE9S5b9rRj` |
| SIMAT 6A dic 2025 | Google Drive (descarga automatica en Colab) | ID: `18rLE8paAcWuoRziRCgjA5Yz5lJdv--cR` |

Los archivos SIMAT no estan en el repositorio por su tamano. El notebook los descarga automaticamente desde Google Drive al ejecutarse en Colab usando la libreria `gdown`:

```python
# Celda ED-2 del notebook — descarga automatica en Colab
import gdown
for año, fid in SIMAT_DRIVE_IDS.items():
    dest = Path(f'/content/simat_6a_dic_{año}.xlsx')
    gdown.download(id=fid, output=str(dest), quiet=False)
```

Si se ejecuta fuera de Colab (localmente), los archivos SIMAT deben descargarse manualmente desde Drive y colocarse en la ruta `/content/simat_6a_dic_{año}.xlsx` o ajustar la ruta en el notebook. Sin SIMAT, las tasas de desercion y repitencia quedan como `NaN` y el score cae al valor provisional `54.9`.

**Indicadores calculados:**

| Indicador | Formula | Ref Min | Ref Max | Tipo |
|---|---|---:|---:|---|
| Tasa de desercion (%) | desertores / matricula × 100 | 0% | 15% | Inverso |
| Tasa de repitencia (%) | repitentes / matricula × 100 | 0% | 20% | Inverso |

**Calculo del score:**
```
tasa_des      = desertores_SIMPADE / matricula_SIMAT * 100
tasa_rep      = repitentes_SIMAT   / matricula_SIMAT * 100

score_des     = score_ref(tasa_des, 0, 15, inverso=True)
score_rep     = score_ref(tasa_rep, 0, 20, inverso=True)

score_educ_des = (score_des + score_rep) / 2
```

El score es **anual** (un valor por ano, extendido plano a los 4 trimestres). Para el ano 2026, donde no existe corte anual SIMAT/SIMPADE, se conserva el valor de referencia provisional `REF_EDUC_DES = 54.9`.

---

### 3.6 Desarrollo Economico — Peso: 15%

Mide la dinamica de creacion y formalidad empresarial en el territorio.

| Indicador | Fuente | Ref Min | Ref Max | Tipo | Transformacion |
|---|---|---:|---:|---|---|
| Negocios nuevos por ano | Registro Mercantil | 0 | 15 | Positivo | Ninguna |
| Personal de negocios nuevos | Registro Mercantil | 0 | 20 | Positivo | Ninguna |
| Ingresos de negocios nuevos | Registro Mercantil | 0 | 20.4 | Positivo | log1p |

**Fuente:** Registro Mercantil de la Camara de Comercio de Cali — snapshot 2025 de 123 negocios georreferenciados dentro del poligono del Barrio Obrero (94.1% microempresas).

**Construccion de la serie temporal:** A partir del campo `fecha_matricula` (formato texto en espanol: "5 de agosto de 2013") se determina el ano y trimestre de creacion de cada negocio, permitiendo reconstruir la evolucion 2023–2025. Los campos `PERSONAL_O` e `INGRESOS_A` son valores autodeclarados al momento del registro; celdas en $0 indican que el negocio no reporto ese dato, no necesariamente ausencia de actividad.

**Transformacion de ingresos:** Se aplica `log1p(ingresos)` para suavizar la alta variabilidad de los montos declarados (rango $0 – $555M por trimestre). El ref max de 20.4 corresponde a `log1p(720,000,000)`.

**Periodicidad en el ITT:** El score DE es **anual**. Se calcula una vez por ano agregando los tres indicadores del ano y se mantiene constante para los cuatro trimestres, en coherencia con la naturaleza del dato fuente (snapshot anual). Este tratamiento es identico al de Entorno Urbano y Educacion y Desarrollo.

**Calculo:**
```
score_des_eco = mean(score_negocios, score_personal, score_ingresos_log1p)
```

Resultados por ano:

| Ano | Negocios | Personal | Ingresos | Score DE |
|---|---:|---:|---|---:|
| 2023 | 5 | 18 | $640M | 74.2 |
| 2024 | 11 | 4 | $130M | 61.6 |
| 2025 | 10 | 8 | $2M | 59.3 |

---

## 4. Calculo trimestral del ITT Global

Para la evolucion trimestral, los indicadores con fuente trimestral (Seguridad, Movilidad, Cohesion) se normalizan con refs trimestrales (`ref_anual / 4`). Los indicadores anuales (Entorno Urbano, Educacion y Desarrollo, Desarrollo Economico) mantienen su valor del ano correspondiente en los 4 trimestres.

```
ITT_trimestre =
    0.27 * score_seguridad_trimestral
  + 0.22 * score_movilidad_trimestral
  + 0.09 * score_cohesion_trimestral
  + 0.17 * score_entorno_u_anual
  + 0.10 * score_educ_des_anual
  + 0.15 * score_des_eco_anual
```

---

## 5. Resultados ITT Global 2023–2025

| Ano | Seguridad | Movilidad | Cohesion | Entorno U. | Educ. y Des. | Des. Eco. | **ITT** | Nivel |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2023 | 79.0 | 57.1 | 37.6 | 29.5 | 54.9 | 74.2 | **58.9** | Consolidacion |
| 2024 | 43.0 | 86.8 | 82.9 | 33.1 | 54.9 | 61.6 | **58.5** | Consolidacion |
| 2025 | 67.0 | 92.2 | 42.4 | 31.8 | 54.9 | 59.3 | **62.0** | Avance |

---

## 6. Notas metodologicas

- **Refs fijos vs. min-max relativo:** Se usan umbrales fijos calibrados con la serie historica de la zona para evitar scores artificialmente extremos en territorios pequenos con conteos bajos.
- **Entorno Urbano:** El score se calcula desde datos reales del poligono (rasters NDVI anuales + inventario de arboles DAGMA). No es un valor heredado de otra zona. El resultado aproximado de ~39.2 refleja baja cobertura vegetal y densidad arborea moderada en el barrio.
- **Educacion y Desarrollo:** El score se calcula con datos reales SIMAT/SIMPADE para 2023-2025. El valor referencial `54.9` es unicamente el fallback para 2026, ano en que no existe corte anual disponible de esas fuentes.
- **Dimensiones anuales en serie trimestral:** Entorno Urbano, Educacion y Desarrollo y Desarrollo Economico se miden anualmente. En la evolucion trimestral del ITT su valor se extiende plano a los 4 trimestres del mismo ano. Esto es un efecto del dato, no del calculo.
- **Datos parciales Registro Mercantil:** Los campos `INGRESOS_A` y `PERSONAL_O` son autodeclarados al momento de la matricula del negocio. Un valor de $0 no implica inactividad economica, sino que el empresario no reporto ese dato en el formulario de registro.
- **SPA en Cohesion:** Los comparendos por sustancias psicoactivas se computan desde el GeoJSON de comparendos (no del GeoJSON de delitos) filtrado por `agrupado == 'SUSTANCIAS PSICOACTIVAS'`, y se incorporan como tercer componente de la dimension Cohesion Social.
- **REF_VULNERABILIDAD:** El valor 54.1 (score de vulnerabilidad socioeconomica del ITT Pulmon de Oriente) se conserva como dato de contexto pero **no entra al calculo del ITT** de Barrio Obrero.
