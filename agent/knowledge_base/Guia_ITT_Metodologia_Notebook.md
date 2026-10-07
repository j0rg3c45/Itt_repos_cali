# Metodología Completa ITT — Índice de Transformación Territorial

## Guía técnica para cálculo, calibración y replicación en nuevas zonas

**Versión:** 1.0  
**Última actualización:** Mayo 2026  
**Fuente base:** Metodología ITT Pulmón de Oriente · Sustento empírico ref_min/ref_max v1.2  
**Propósito:** Documento de referencia para un agente de IA que asista en la construcción y calibración del ITT en cualquier zona nueva.

---

## 1. Definición del ITT

El Índice de Transformación Territorial (ITT) es una medición compuesta que cuantifica el grado de transformación positiva que experimenta un territorio como resultado de la inversión pública y las intervenciones institucionales.

Opera en una escala de **0 a 100** donde valores más altos indican mayor nivel de transformación territorial. No mide solamente inversión ejecutada, sino resultados e impacto en condiciones de vida.

### Clasificación

| Rango | Nivel | Descripción |
|-------|-------|-------------|
| 0 – 40 | Nivel 1 · Emergencia | Condiciones críticas. Requiere intervención intensiva e inmediata |
| 40 – 60 | Nivel 2 · Consolidación | Avances visibles con resultados parciales en consolidación |
| 60 – 80 | Nivel 3 · Avance | Mejora territorial consolidada y sostenida |
| 80 – 100 | Nivel 4 · Transformación | Transformación robusta con capacidad de sostenerse y replicarse |

---

## 2. Dimensiones y ponderaciones

| Dimensión | Peso | Tipo general | Indicadores base |
|-----------|------|-------------|-----------------|
| Seguridad | 30% | Inverso | Homicidios, Hurtos |
| Movilidad | 25% | Inverso | Siniestralidad vial, Accidentes con lesionados, Muertes en vía |
| Entorno Urbano | 20% | Positivo/Mixto | NDVI, Área verde neta, Déficit AHDI |
| Educación y Desarrollo | 13% | Mixto | Matrícula, Deserción, Repitencia, Estudiantes/docente, Cobertura deportiva |
| Cohesión Social | 12% | Inverso/Neutro | VIF, Riñas/conflictividad, Concentración de vulnerabilidad activa |

**La suma de los pesos debe ser siempre 1.0 (100%).**

Los pesos reflejan la prioridad estratégica del Plan de Desarrollo para la zona de intervención. Seguridad tiene el mayor peso (30%) por ser la condición habilitante de las demás transformaciones.

---

## 3. Fórmula de cálculo — 3 pasos

### Paso 1 — Normalización por indicador con ref_min / ref_max

Cada indicador se transforma a una escala común de 0 a 100 mediante umbrales de referencia fijos.

**Fórmula base:**

```
score_raw = clamp( (valor - ref_min) / (ref_max - ref_min) × 100,  0, 100 )
```

**Para indicadores inversos** (menor valor = mejor resultado: homicidios, hurtos, siniestralidad, VIF, riñas...):

```
score = 100 - score_raw
```

**Para indicadores positivos** (mayor valor = mejor resultado: matrícula, área verde, cobertura deportiva...):

```
score = score_raw
```

El uso de `clamp(resultado, 0, 100)` garantiza que el score final permanezca dentro del rango 0-100 incluso cuando el valor observado supere los límites de referencia.

### Paso 2 — Score de dimensión (promedio simple)

Cada dimensión agrega sus indicadores con igual peso entre ellos:

```
Score_dim = (Score_ind1 + Score_ind2 + ... + Score_indN) / N
```

Ejemplos:
- Score_Seguridad = (Score_Homicidios + Score_Hurtos) / 2
- Score_Movilidad = (Score_Siniestralidad + Score_Lesionados + Score_Muertes) / 3
- Score_Cohesion = (Score_VIF + Score_Riñas + Score_Vulnerabilidad) / 3

### Paso 3 — Índice compuesto ITT (suma ponderada)

```
ITT = 0.30 × Seguridad + 0.25 × Movilidad + 0.20 × Entorno_Urbano + 0.13 × Educación + 0.12 × Cohesión
```

---

## 4. Umbrales ref_min / ref_max — Referencia Pulmón de Oriente

Los umbrales ref_min y ref_max son determinantes en la sensibilidad del score. Cambios en estos límites modifican directamente la posición relativa de cada indicador.

### 4.1 Indicadores con serie histórica real (12 trimestres, 2023-T1 a 2025-T4)

Estos indicadores tienen el mejor sustento empírico disponible. Las referencias dan margen operacional sobre el rango observado.

| Indicador | Dim. | Valor T4-25 | ref_min | ref_max | Obs. min (trim) | Obs. max (trim) | Tipo |
|-----------|------|-------------|---------|---------|-----------------|-----------------|------|
| Homicidios | Seguridad | 36 | 5 | 50 | 9 (2025-T3) | 38 (2023-T3) | Inverso |
| Hurtos | Seguridad | 260 | 200 | 450 | 259 (2023-T4) | 434 (2023-T1) | Inverso |
| Siniestralidad vial (sin fallecidos) | Movilidad | 57 | 28 | 75 | 44 (2024-T2) | 65 (2023-T3) | Inverso |
| Accidentes con lesionados | Movilidad | 53 | 20 | 65 | 42 (2024-T2) | 56 (2023-T3) | Inverso |
| Muertes en vía | Movilidad | 6 | 1 | 10 | 2 (2024-T1) | 6 (varios) | Inverso |
| VIF | Cohesión | 105* | 60 | 200 | 88 (2023-T4) | 189 (2025-T3) | Inverso |
| Riñas / conflictividad | Cohesión | 127 | 20 | 160 | 38 (2023-T4) | 144 (2025-T3) | Inverso |

*VIF: el score se calcula con el valor trimestral (refs [60,200]); el display muestra el total anual para legibilidad.

**Criterios de calibración para serie real:**
- ref_min: aspiracional (mejor resultado razonable) o ligeramente por debajo del mínimo observado
- ref_max: ligeramente por encima del máximo observado, dando margen para empeoramientos

### 4.2 Indicadores con serie anual por diseño (3 cortes anuales)

La frecuencia anual es inherente a la fuente (año lectivo, corte institucional). Tres cortes anuales son suficientes para observar tendencia general.

| Indicador | Dim. | Valor 2025 | ref_min | ref_max | Obs. min | Obs. max | Tipo |
|-----------|------|-----------|---------|---------|----------|----------|------|
| Matrícula escolar | Educación | 50,336 | 40,000 | 58,000 | 50,336 (2025) | 53,746 (2023) | Positivo |
| Deserción escolar | Educación | 4.3% | 1.0 | 10.0 | 4.3% (2025) | 5.3% (2024) | Inverso |
| Repitencia escolar | Educación | 8.4% | 1.0 | 15.0 | 8.4% (2025) | 9.4% (2023) | Inverso |
| Estudiantes/docente | Educación | 27.1 | 18 | 40 | 26.7 (2024) | 28.3 (2023) | Inverso |

### 4.3 Indicadores con un solo punto de datos o dato manual

Estos concentran la evidencia más débil. Los valores de referencia dependen de juicio experto, rangos conceptuales o supuestos de diseño.

| Indicador | Dim. | Valor | ref_min | ref_max | Sustento |
|-----------|------|-------|---------|---------|----------|
| NDVI cobertura vegetal | Entorno U. | 0.20 | 0.15 | 0.65 | Un solo TIF (2025). ref_max aspiracional para zona urbana densa |
| Área verde neta | Entorno U. | 1,699,769 m² | 500,000 | 3,000,000 | Un solo TIF. ref_max ~25% del polígono |
| Déficit AHDI | Entorno U. | 46.4% | 10 | 100 | Escala conceptual 0-100, no anclada a observación histórica |
| Concentración vulnerabilidad | Cohesión | 54.1 p/1K | 30 | 160 | Un solo corte (2025). Refs son rangos sectoriales |
| Cobertura deportiva | Educación | 3,877 reg. | 1,000 | 7,000 | Dato proxy oficial de 25 escenarios deportivos |

### 4.4 Resumen del peso metodológico

| Estado | Indicadores | Peso acumulado ITT |
|--------|------------|-------------------|
| Serie real (12 trimestres) | 7 | ~35% |
| Serie anual por diseño (3 cortes) | 4 | ~11% |
| Dato débil (juicio experto / único dato) | 6 | ~54% |

**Implicación para la lectura del ITT:**
- Los movimientos del ITT explicados por los 7 indicadores de serie real (35% de peso) son los más confiables.
- Los 4 indicadores de educación (11%) son estables por diseño y se actualizan anualmente.
- Los 6 indicadores de dato débil (54%) son los que más se beneficiarán de mejora continua de fuentes.

---

## 5. Ejemplo de cálculo completo — Pulmón de Oriente

### 5.1 Seguridad (30%)

| Indicador | Valor | ref_min | ref_max | score_raw | Inverso | Score |
|-----------|-------|---------|---------|-----------|---------|-------|
| Homicidios | 36 | 5 | 50 | 68.9 | Sí | 31.1 |
| Hurtos | 260 | 200 | 450 | 24.0 | Sí | 76.0 |

**Score Seguridad = (31.1 + 76.0) / 2 = 53.6**

### 5.2 Movilidad (25%)

| Indicador | Valor | ref_min | ref_max | score_raw | Inverso | Score |
|-----------|-------|---------|---------|-----------|---------|-------|
| Siniestralidad vial | 63 | 30 | 80 | 66.0 | Sí | 34.0 |
| Accidentes lesionados | 53 | 20 | 65 | 73.3 | Sí | 26.7 |
| Muertes en vía | 6 | 1 | 10 | 55.6 | Sí | 44.4 |

**Score Movilidad = (34.0 + 26.7 + 44.4) / 3 = 35.0**

Nota: En versión anterior se incluía Velocidad del corredor (score 74.0, positivo) pero fue retirada del modelo v7 por ser dato único sin serie histórica que inflaba la dimensión.

### 5.3 Entorno Urbano (20%)

| Indicador | Valor | ref_min | ref_max | score_raw | Inverso | Score |
|-----------|-------|---------|---------|-----------|---------|-------|
| NDVI | 0.20 | 0.15 | 0.65 | 10.0 | No | 10.0 |
| Área verde neta | 1,699,769 m² | 500,000 | 3,000,000 | 48.0 | No | 48.0 |
| Déficit AHDI | 46.4% | 10 | 100 | 40.4 | Sí | 59.6 |

**Score Entorno Urbano = (10.0 + 48.0 + 59.6) / 3 = 39.2**

### 5.4 Educación y Desarrollo (13%)

| Indicador | Valor | ref_min | ref_max | score_raw | Inverso | Score |
|-----------|-------|---------|---------|-----------|---------|-------|
| Matrícula | 50,336 | 40,000 | 58,000 | 57.4 | No | 57.4 |
| Deserción | 4.3% | 1.0 | 10.0 | 36.7 | Sí | 63.3 |
| Repitencia | 8.4% | 1.0 | 15.0 | 52.9 | Sí | 47.1 |
| Estudiantes/docente | 27.1 | 18 | 40 | 41.4 | Sí | 58.6 |
| Cobertura deportiva | 4,200 | 1,000 | 7,000 | 53.3 | No | 53.3 |

**Score Educación = (57.4 + 63.3 + 47.1 + 58.6 + 53.3) / 5 = 55.9**

### 5.5 Cohesión Social (12%)

| Indicador | Valor | ref_min | ref_max | score_raw | Inverso | Score |
|-----------|-------|---------|---------|-----------|---------|-------|
| VIF | 105 | 60 | 200 | 32.1 | Sí | 67.9 |
| Riñas | 127 | 20 | 160 | 76.4 | Sí | 23.6 |
| Vulnerabilidad | 54.1 p/1K | 30 | 160 | 18.5 | Sí | 81.5 |

**Score Cohesión = (67.9 + 23.6 + 81.5) / 3 = 57.7**

### 5.6 Consolidado ITT

| Dimensión | Score | Peso | Contribución |
|-----------|-------|------|-------------|
| Seguridad | 53.6 | 30% | 16.1 pts |
| Movilidad | 35.0 | 25% | 8.8 pts |
| Entorno Urbano | 39.2 | 20% | 7.8 pts |
| Educación y Des. | 55.9 | 13% | 7.3 pts |
| Cohesión Social | 57.7 | 12% | 6.9 pts |
| **ITT Global** | **46.9** | **100%** | **Nivel 2 · Consolidación** |

---

## 6. Cómo calibrar ref_min / ref_max para una zona nueva

### 6.1 Principios generales

1. **ref_min** = umbral aspiracional (mejor resultado razonable) o el mínimo observado con margen inferior
2. **ref_max** = peor resultado tolerable o el máximo observado con margen superior
3. Los refs deben ser **fijos y documentados** — no calculados dinámicamente de los datos
4. El rango [ref_min, ref_max] debe ser lo suficientemente amplio para capturar variación real pero no tan amplio que todos los scores queden en un rango estrecho

### 6.2 Escenarios por tipo de zona

#### Zona grande (corredor vial, múltiples comunas, >100K hab)

Usar los refs de Pulmón de Oriente directamente o con ajuste menor. Los volúmenes de datos son comparables.

```
Homicidios:     ref_min=5,   ref_max=50
Hurtos:         ref_min=200, ref_max=450
Siniestralidad: ref_min=28,  ref_max=75
```

#### Zona mediana (barrio grande, corredor corto, 10K-50K hab)

Escalar los refs proporcionalmente al tamaño poblacional o usar juicio experto para el contexto local.

```
Homicidios:     ref_min=1,   ref_max=15
Hurtos:         ref_min=30,  ref_max=150
Siniestralidad: ref_min=5,   ref_max=30
```

#### Zona pequeña (barrio individual, <10K hab)

Definir refs específicos basados en el rango razonable para el tamaño del territorio.

```
Homicidios:     ref_min=0,   ref_max=5
Hurtos:         ref_min=10,  ref_max=60
Siniestralidad: ref_min=1,   ref_max=15
```

### 6.3 Reglas prácticas de calibración

| Regla | Descripción |
|-------|-------------|
| No usar min-max relativo | Nunca calcular ref_min/ref_max a partir de los propios datos de la zona. Esto infla scores con muestras pequeñas |
| Documentar siempre | Cada ref_min/ref_max debe tener una justificación escrita (serie histórica, benchmark, juicio experto) |
| Validar con expertos locales | Los refs propuestos deben ser revisados por quien conoce el territorio |
| Sensibilidad | Probar el ITT con +/-20% en refs para evaluar cuánto cambia el resultado |
| Mantener consistencia | Si se comparan múltiples zonas, usar la misma estructura de refs (escalada por tamaño si es necesario) |

### 6.4 Errores comunes a evitar

| Error | Consecuencia | Corrección |
|-------|-------------|-----------|
| Usar min-max relativo de la muestra | Scores de 0 o 100 con muestras pequeñas, ITT inflado | Usar refs fijos |
| ref_min = ref_max | División por cero | Asegurar que siempre ref_max > ref_min |
| Refs de zona grande en zona pequeña | Todo sale score ~100 porque los conteos son naturalmente bajos | Escalar refs por población/área |
| No invertir indicadores negativos | Más homicidios = mejor score (absurdo) | Verificar flag inverso por indicador |
| Hardcodear dimensiones enteras sin documentar | ITT no refleja realidad y no se sabe por qué | Marcar explícitamente qué es referente provisional y de dónde viene |

---

## 7. Manejo de dimensiones sin datos propios

Cuando no se tienen datos reales para una dimensión completa:

1. Usar el **score de referencia de Pulmón de Oriente** como valor provisional constante
2. Documentar explícitamente que es un valor referente, no calculado
3. Indicar la fuente y el corte temporal del valor
4. Reemplazar en cuanto se tengan datos reales del territorio

### Valores referentes actuales (Pulmón de Oriente)

| Dimensión | Score referente | Fuente |
|-----------|----------------|--------|
| Entorno Urbano | 39.2 | ITT Pulmón de Oriente T4-2025 |
| Educación y Desarrollo | 54.9 | ITT Pulmón de Oriente T4-2025 |
| Vulnerabilidad activa (indicador Cohesión) | 54.1 | Sec. Bienestar Social / Caracterización Sub PyE 2025 C13-C14 |

---

## 8. Estructura de datos de entrada

### Archivos GeoJSON esperados por indicador

| Indicador | Campos mínimos | CRS esperado | Frecuencia |
|-----------|---------------|-------------|-----------|
| Homicidios | FECHA_HECH, X, Y | EPSG:4326 | Evento individual |
| Hurtos | FECHA_HECH, X, Y, TIPO_HURTO | EPSG:4326 | Evento individual |
| Siniestros | Fecha, X, Y, Tipo_Confi | EPSG:4326 o EPSG:3115 | Evento individual |
| VIF | FECHA_HECH, X, Y | EPSG:4326 | Evento individual |
| Riñas (Comparendos) | fecha_hech, lat, lon, agrupado="RIÑAS" | EPSG:4326 | Evento individual |

### Polígono de la zona

- Puede ser un polígono único (barrio) o múltiples tramos (corredor vial con buffers)
- CRS: EPSG:3115 (MAGNA-SIRGAS Colombia Oeste) o EPSG:9377 (Origen Nacional)
- Campos: identificador de tramo/zona, geometría

---

## 9. Tratamiento de datos nulos y ausentes

Los datos ausentes se manejan en dos niveles:

1. **Exclusión espacial:** Los registros que caen fuera del polígono definido son excluidos del análisis (típicamente <4%). Corresponden a eventos en zonas limítrofes.

2. **Ceros legítimos:** Los períodos donde no se registró ningún evento reciben valor cero, lo que refleja la ausencia real del fenómeno.

En ningún caso se inventan o estiman datos faltantes. No se realiza imputación estadística.

---

## 10. Implementación en Python (estructura del notebook)

### Función de normalización con refs fijos

```python
def score_ref(valor, ref_min, ref_max, inverso):
    """Normaliza un valor con umbrales fijos ref_min/ref_max."""
    if ref_max == ref_min:
        return 100.0
    raw = np.clip((valor - ref_min) / (ref_max - ref_min) * 100, 0, 100)
    return 100 - raw if inverso else raw
```

### Definición de refs en el notebook (editables)

```python
REFS = {
    #                  ref_min  ref_max  inverso  descripcion
    'homicidios':     (0,       5,       True,    'Homicidios anuales'),
    'hurtos':         (10,      60,      True,    'Hurtos anuales'),
    'siniestralidad': (1,       15,      True,    'Siniestros viales'),
    'lesionados':     (1,       12,      True,    'Accidentes con lesionados'),
    'mortales':       (0,       3,       True,    'Accidentes mortales'),
    'vif':            (1,       15,      True,    'VIF anual'),
    'rinas':          (0,       10,      True,    'Riñas anual'),
}
```

### Cálculo del ITT

```python
# Normalizar
for ind, (rmin, rmax, inv, desc) in REFS.items():
    base[f'score_{ind}'] = base[ind].apply(lambda v: score_ref(v, rmin, rmax, inv))

# Scores por dimensión
base['score_seguridad'] = (base['score_homicidios'] + base['score_hurtos']) / 2
base['score_movilidad'] = (base['score_siniestralidad'] + base['score_lesionados'] + base['score_mortales']) / 3
base['score_cohesion']  = (base['score_vif'] + base['score_rinas'] + REF_VULNERABILIDAD) / 3
base['score_entorno_u'] = REF_ENTORNO_U      # referente provisional
base['score_educ_des']  = REF_EDUC_DES        # referente provisional

# ITT
base['ITT'] = (
    0.30 * base['score_seguridad'] +
    0.25 * base['score_movilidad'] +
    0.20 * base['score_entorno_u'] +
    0.13 * base['score_educ_des'] +
    0.12 * base['score_cohesion']
)
```

---

## 11. Flujo para replicar en una zona nueva

### Paso 1 — Definir el polígono
Generar el polígono de la zona (barrio, corredor vial con buffers, etc.) en QGIS o ArcGIS. Exportar como GeoJSON.

### Paso 2 — Inventariar datos disponibles
Listar qué indicadores tienen datos reales con fecha y coordenadas. Los que no, marcarlos como referentes provisionales.

### Paso 3 — Calibrar ref_min / ref_max
Usar la tabla de la sección 6 como guía. Escalar según tamaño de zona. Documentar cada decisión.

### Paso 4 — Configurar el notebook
Copiar la plantilla del notebook, ajustar rutas, ANIOS, PESOS, REFS y valores referentes en la Celda 3.

### Paso 5 — Ejecutar y validar
Correr el notebook completo. Verificar que los scores e ITT sean razonables. Si algún indicador da score extremo (0 o 100), revisar los refs.

### Paso 6 — Iterar
Cuando lleguen datos reales para dimensiones referentes, reemplazar los valores fijos por scores calculados y re-ejecutar.

---

## 12. Observaciones metodológicas finales

- Las referencias mínimas y máximas son determinantes en la sensibilidad del score. Cambios en estos límites modifican directamente la posición relativa de cada indicador.
- El índice final es comparable entre dimensiones porque todos los indicadores fueron llevados a una escala homogénea de 0 a 100 antes de la agregación ponderada.
- Las dimensiones con menor puntaje deben interpretarse como frentes prioritarios de intervención, especialmente cuando además concentran pesos altos dentro del índice global.
- El ITT es un índice de seguimiento territorial operativo, no un modelo econométrico de precisión. Los indicadores de dato débil no invalidan el índice; lo contextualizan.
- La lectura correcta jerarquiza los movimientos explicados por indicadores con serie real, reconoce la estabilidad estructural de los indicadores anuales por diseño, y señala las oportunidades de mejora continua en los indicadores de dato débil.

---

## 13. Glosario

| Término | Definición |
|---------|-----------|
| ITT | Índice de Transformación Territorial |
| Score | Valor normalizado 0-100 de un indicador o dimensión |
| ref_min | Umbral inferior de normalización (mejor resultado razonable) |
| ref_max | Umbral superior de normalización (peor resultado tolerable) |
| clamp | Función que acota un valor al rango [0, 100] |
| Indicador inverso | Indicador donde menor valor = mejor resultado (homicidios, hurtos) |
| Indicador positivo | Indicador donde mayor valor = mejor resultado (matrícula, área verde) |
| Referente provisional | Score fijo tomado de otra zona calculada, usado mientras no hay datos propios |
| Serie real | Indicador con 12 trimestres de datos históricos comparables |
| Dato débil | Indicador con un solo corte, dato manual o supuesto de diseño |
| Spatial join | Operación GIS que asigna cada punto al polígono que lo contiene |
| CRS | Sistema de Referencia de Coordenadas (EPSG) |
| Buffer | Zona de influencia alrededor de un eje vial |
| MAGNA-SIRGAS | Marco Geocéntrico Nacional de Referencia de Colombia |
