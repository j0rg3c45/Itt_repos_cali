# Índice de Transformación Territorial

## Documento Maestro de Definición y Metodología

**Versión:** 1.0 · Mayo 2026  
**Elaborado por:** Equipo de Gobierno de Datos — Alcaldía Distrito Santiago de Cali  
**Territorios:** Pulmón de Oriente · Av. Roosevelt · Av. Ciudad de Cali · Barrio Obrero  

---

## Propósito de este documento

Este documento recoge la definición completa del **Índice de Transformación Territorial (ITT) de Cali Inteligente**: su objetivo, arquitectura metodológica, dimensiones, indicadores, fuentes de datos, territorios de aplicación y herramientas técnicas.

Sirve como referencia maestra para el equipo de Gobierno de Datos, para los organismos que alimentan el índice y como punto de entrada para cualquier colaboración externa, incluyendo academia, organismos internacionales y otros municipios.

---

## Tabla de contenido

1. [Objetivo y contexto](#1-objetivo-y-contexto)  
2. [Fórmula y escala del ITT](#2-fórmula-y-escala-del-itt)  
3. [Dimensiones e indicadores](#3-dimensiones-e-indicadores)  
4. [Territorios de aplicación](#4-territorios-de-aplicación)  
5. [Diseño de evaluación de impacto](#5-diseño-de-evaluación-de-impacto)  
6. [Fuentes de datos, herramientas y acceso](#6-fuentes-de-datos-herramientas-y-acceso)  

---

# 1. Objetivo y contexto

El **ITT** es el instrumento de medición de impacto de las intervenciones estratégicas del Distrito de Santiago de Cali en territorios priorizados.

Su pregunta central es:

> Cuando terminan las obras, ¿cómo sabemos si hubo transformación real en el territorio?

El índice responde esa pregunta produciendo un número entre **0 y 100** que sintetiza el estado del territorio en cinco dimensiones, próximamente seis:

- Seguridad.
- Movilidad.
- Entorno urbano.
- Educación y desarrollo.
- Cohesión social.
- Actividad económica, en proceso de definición y validación.

El ITT no es un reporte estático. Es un sistema de monitoreo permanente que opera sobre el **datalake distrital**, dentro del ecosistema **CalIA**, y produce resultados comparables entre territorios y en el tiempo.

---

## 1.1 Principios de diseño

| Principio | Descripción |
|---|---|
| Legibilidad | Escala 0–100 que cualquier tomador de decisión entiende sin contexto técnico adicional. |
| Comparabilidad temporal | Los indicadores tienen serie histórica mínima 2023–2025, lo que permite observar la tendencia antes de la intervención y medir el cambio posterior. |
| Comparabilidad territorial | El mismo modelo se aplica a todos los polígonos priorizados, permitiendo comparación entre territorios. |
| Atribuibilidad | Diseño de territorio espejo, es decir, zona de comparación sin intervención, para demostrar que las mejoras son producto de la obra y no de tendencias externas. |
| Sostenibilidad técnica | Los indicadores se calculan desde el datalake, no desde solicitudes manuales a secretarías. |

---

## 1.2 Respaldo metodológico internacional

| Referencia | Aporte al ITT | Aplicación |
|---|---|---|
| OCDE/JRC — *Handbook on Constructing Composite Indicators* — Nardo et al., 2008 | Normalización min-max, agregación lineal ponderada y diez pasos para índices compuestos de política pública. | Método estándar del ITT. |
| Reino Unido — *English Index of Multiple Deprivation* — IMD, 1999–hoy | Índice compuesto de 37 indicadores en siete dominios territoriales a escala de vecindario, con 25 años de uso en política pública. | Mismo modelo dimensional. |
| Banco Mundial / BID — *La evaluación de impacto en la práctica* — Gertler et al., 2017 | Cadena Output → Outcome → Impact, diferencias en diferencias y diseño de territorio de control o espejo. | Cadena causal del ITT. |
| *International Journal of Health Geographics* — Urban Liveability Index, Melbourne, Higgs et al., 2019 | Índice compuesto espacial para decisión de política pública y criterio explícito de comunicabilidad a tomadores de decisión. | Comunicabilidad como criterio de diseño. |

---

# 2. Fórmula y escala del ITT

## 2.1 Fórmula

El ITT se calcula como una agregación lineal ponderada de los scores de cada dimensión, todos normalizados en escala **0–100** mediante normalización **min-max**.

```text
ITT = 0,27 × I_Seg
    + 0,22 × I_Mov
    + 0,17 × I_Ent
    + 0,10 × I_EyD
    + 0,09 × I_Coh
    + 0,15 × I_Eco
```

Donde cada dimensión se normaliza con la fórmula:

```text
Score = (valor – mín_histórico) / (máx_histórico – mín_histórico) × 100
```

Para indicadores negativos, donde menor es mejor, como homicidios, la fórmula se invierte:

```text
Score = (máx – valor) / (máx – mín) × 100
```

El peso de la dimensión de **Actividad Económica** está pendiente de definición tras la validación metodológica con ICESI. Los pesos de las demás dimensiones se ajustarán proporcionalmente.

---

## 2.2 Escala de madurez

| Nivel | Nombre | Rango ITT | Descripción |
|---:|---|---|---|
| 1 | Activación | 0 – 40 | El espacio se usa más, pero los indicadores estructurales aún no se han movido. |
| 2 | Consolidación | 41 – 60 | Bajan los incidentes y sube la afluencia al espacio público de forma simultánea y sostenida. |
| 3 | Transformación | 61 – 80 | Mejora la actividad económica y la comunidad reconoce el esfuerzo de la administración. |
| 4 | Escala | 81 – 100 | La intervención genera condiciones para sostenerse y replicarse en otros territorios. |

---

# 3. Dimensiones e indicadores

Cada dimensión contiene un conjunto de indicadores normalizados individualmente y luego agregados en el score de la dimensión.

## Nota metodológica sobre el número de dimensiones del ITT

El ITT está diseñado deliberadamente con un número acotado de dimensiones, entre cinco y seis, y un máximo de tres a cuatro indicadores por dimensión. Esta decisión responde a principios metodológicos consolidados en la literatura internacional sobre índices compuestos de política pública.

Los índices compuestos más robustos y citados a nivel internacional son deliberadamente parsimoniosos. El Índice de Desarrollo Humano del PNUD opera con tres dimensiones; el Índice de Prosperidad Urbana de ONU-Hábitat con seis; y el *English Index of Multiple Deprivation* del Reino Unido, con 25 años de uso en política pública, tiene siete dominios bien delimitados.

En todos los casos, la parsimonia no limita la utilidad del índice, sino que garantiza su legibilidad e interpretabilidad por parte de tomadores de decisión no especializados.

Desde el punto de vista técnico, cada dimensión adicional diluye la varianza explicada del índice y dificulta la atribución de cambios a causas específicas. Con seis dimensiones bien definidas es posible identificar qué aspecto de la vida urbana mejoró o empeoró y relacionarlo con la intervención evaluada. Con diez o más dimensiones esa capacidad analítica se pierde.

El ITT no es un inventario exhaustivo de la condición del territorio. Para ese propósito existe el **Sistema Integrado de Información Estadística Distrital — SIIED**, con sus cuatro dominios y más de 200 indicadores.

El ITT responde a una pregunta específica:

> ¿Qué cambia en el territorio como consecuencia de una intervención urbana?

Sus dimensiones deben responder a esa pregunta y solo a esa. Agregar dimensiones adicionales solo es metodológicamente justificable si se puede demostrar que la intervención evaluada afecta un aspecto de la vida urbana que ninguna de las dimensiones existentes captura.

Lo que sí es metodológicamente válido y deseable es revisar periódicamente la ubicación de los indicadores dentro de las dimensiones existentes, garantizando coherencia conceptual entre el indicador y la dimensión que habita. Esa revisión no amplía la estructura del índice: la fortalece.

---

## 3.1 Dimensión Seguridad y Convivencia

**Peso:** 0,27  
**Fuente:** Observatorio de Seguridad y Justicia del Valle del Cauca  

Mide la condición de un territorio donde la reducción de hechos delictivos y la disminución de infracciones de convivencia reflejan una mayor confianza colectiva entre los habitantes y entre la comunidad y la institucionalidad.

Un territorio más seguro no solo registra menos violencia grave, sino que muestra menor conflictividad cotidiana en el espacio público, condición necesaria para que las personas se apropien del entorno y lo habiten activamente.

| Indicador | Tipo | Fuente | Metodología | Estado |
|---|---|---|---|---|
| Homicidios en el área | Negativo | Observatorio de Seguridad y Justicia / SIEDCO | Conteo trimestral de homicidios georreferenciados dentro del polígono. | Inversa: `(máx – valor) / (máx – mín) × 100` |
| Hurtos a personas en el área | Negativo | Observatorio de Seguridad y Justicia / SIEDCO | Conteo trimestral de hurtos georreferenciados. Modalidad principal: atraco. | Inversa: `(máx – valor) / (máx – mín) × 100` |
| Infracciones de convivencia | Negativo | Observatorio de Seguridad y Justicia / Comparendos Policía Nacional | Conteo trimestral de comparendos por armas no convencionales, desacato a la autoridad e infracciones al Código Nacional de Policía georreferenciados en el polígono. | Inversa: `(máx – valor) / (máx – mín) × 100` |

---

## 3.2 Dimensión Movilidad y Accesibilidad

**Peso:** 0,22  
**Fuente:** Secretaría de Movilidad / SIMUR  

Mide las condiciones de desplazamiento en el territorio en sus dos dimensiones: la seguridad vial vehicular y la accesibilidad peatonal.

Una intervención urbana que mejora la infraestructura debe traducirse en menos siniestros, menos lesionados, cero muertes en vía y un entorno más caminable para los habitantes. Esta dimensión captura tanto el efecto sobre el tráfico como sobre la movilidad activa y cotidiana de las personas a pie.

| Indicador | Tipo | Fuente | Metodología | Estado |
|---|---|---|---|---|
| Siniestralidad vial | Negativo | Secretaría de Movilidad | Conteo trimestral de accidentes de tránsito en el polígono. | Inversa |
| Accidentes con lesionados | Negativo | Secretaría de Movilidad | Conteo trimestral de accidentes con heridos en el polígono. | Inversa |
| Muertes en vía | Negativo | Secretaría de Movilidad | Conteo trimestral de muertes en accidentes viales en el polígono. | Inversa |
| Caminabilidad peatonal | Positivo | Av. Roosevelt y otros corredores / OpenStreetMap / OSMnx | Índice compuesto: densidad de intersecciones, longitud de red peatonal, longitud promedio de segmento y densidad de calle en km/km². | En revisión para inclusión |

---

## 3.3 Dimensión Entorno Urbano

**Peso:** 0,17  
**Fuentes:** Copernicus/Sentinel-2 · OpenStreetMap/OSMnx · Secretaría de Vivienda, solo Pulmón de Oriente  

Mide la calidad del entorno físico habitable del territorio: la presencia de cobertura vegetal, la disponibilidad de espacio verde, las condiciones de la vivienda y la infraestructura para la movilidad peatonal.

Una intervención que transforma el entorno urbano debe mejorar la relación entre el espacio construido y el espacio natural, reducir el déficit habitacional y hacer el territorio más caminable y accesible para sus habitantes.

| Indicador | Tipo | Fuente | Metodología | Estado |
|---|---|---|---|---|
| NDVI / Cobertura vegetal | Positivo | Todos | Copernicus/Sentinel-2 · TIF procesado. Índice de vegetación calculado sobre el polígono completo. Se refinará sobre sub-polígono ambiental. | Incluido |
| Área verde neta — m² | Positivo | Todos | Copernicus/Sentinel-2 · NDVI ≥ 0,20. Derivado del TIF del NDVI: píxeles con NDVI ≥ 0,20 dentro del polígono. | En revisión |
| Déficit habitacional cualitativo | Negativo | Solo Pulmón de Oriente | Secretaría de Vivienda / AHDI 2024–2026. Porcentaje de déficit habitacional por resolver en el territorio. | Incluido |
| Uso activo del espacio público | Positivo | Cámaras DATIC / Conteo peatonal | Conteo trimestral de personas detectadas en cámaras instaladas en el polígono. Mide la apropiación y uso activo del espacio público post-intervención. | Pendiente instalación de cámaras DATIC |

---

## 3.4 Dimensión Educación y Desarrollo

**Peso:** 0,10  
**Fuentes:** Secretaría de Educación / SIMAT · Secretaría de Recreación y Deporte  

Mide el acceso y la calidad de las oportunidades de formación y desarrollo humano disponibles en el territorio. Incluye tanto la cobertura y eficiencia del sistema educativo formal como la participación en actividades deportivas y recreativas organizadas.

Una intervención que mejora el entorno debe favorecer la permanencia escolar, reducir la deserción y ampliar las opciones de desarrollo para la población, especialmente niños, niñas y jóvenes.

| Indicador | Tipo | Fuente | Metodología | Estado |
|---|---|---|---|---|
| Matrícula escolar | Positivo | Secretaría de Educación / SIMAT | Estudiantes matriculados en sedes dentro del área de influencia del polígono. | Incluido |
| Deserción escolar | Negativo | Secretaría de Educación / SIMAT | Tasa de deserción por sede escolar en el área. | Incluido |
| Repitencia escolar | Negativo | Secretaría de Educación / SIMAT | Tasa de repitencia por sede en el área. | Incluido |
| Estudiantes por docente | Contextual | Secretaría de Educación | Ratio de estudiantes por docente en sedes del área. | En revisión |
| Cobertura deportiva activa | Positivo | Secretaría de Recreación y Deporte | Personas registradas activas en escenarios deportivos del área. | En revisión |

**Pendiente para todos los territorios:** indicador de brecha de cobertura escolar, entendido como niños fuera del sistema frente a la media de Cali. Fuente: SIMAT. Solicitado en reunión de gabinete.

---

## 3.5 Dimensión Cohesión Social

**Peso:** 0,09  
**Fuentes:** Observatorio de Seguridad y Justicia · Secretaría de Bienestar Social  

Mide la fortaleza del tejido social del territorio: la capacidad de la comunidad para sostener relaciones de convivencia, proteger a sus miembros más vulnerables y resistir dinámicas de desintegración.

Un territorio con alta cohesión social registra menos violencia al interior de los hogares, menos conflictividad entre vecinos, menor presencia de conductas de exclusión social en el espacio público y menor concentración de personas en situación de vulnerabilidad activa.

Esta dimensión captura lo que una obra no produce directamente, pero que su ausencia puede deteriorar o su presencia puede fortalecer.

| Indicador | Tipo | Fuente | Metodología | Estado |
|---|---|---|---|---|
| Violencia intrafamiliar — VIF | Negativo | Observatorio de Seguridad y Justicia / SIEDCO | Casos anuales de VIF georreferenciados en el área. | Calculado |
| Riñas / conflictividad | Negativo | Observatorio de Seguridad y Justicia / Comparendos | Conteo trimestral de comparendos por riñas en el área. | Calculado |
| Concentración de vulnerabilidad activa | Negativo | Secretaría de Bienestar Social / Sub PyE 2025 | Personas en situación de vulnerabilidad activa por 1.000 habitantes en el área. | Proxy · Pendiente dato propio |
| Consumo de SPA en espacio público | Negativo | Observatorio de Seguridad y Justicia / Comparendos Policía Nacional | Conteo trimestral de comparendos por consumo de sustancias psicoactivas en espacio público georreferenciados en el polígono. Indicador independiente solicitado por el Alcalde. | Pendiente extracción y georreferenciación desde dataset de comparendos |

---

## 3.6 Dimensión Actividad Económica

**Peso:** 0,15  

Esta dimensión fue incorporada por solicitud del Alcalde. Su peso definitivo en la fórmula del ITT está pendiente de validación metodológica con ICESI.

Los indicadores de la fase inicial fueron acordados en reunión del **8 de mayo de 2026** con la Secretaría de Desarrollo Económico.

Mide la vitalidad económica del territorio: la densidad de empresas activas, la generación de empleo local y el volumen de ingresos operacionales.

Una intervención urbana que mejora la infraestructura y la seguridad debe generar condiciones para la apertura de nuevos negocios, la formalización de la actividad económica existente y la creación de empleo.

Esta dimensión captura el efecto multiplicador de la inversión pública sobre la economía del territorio y es la que tiene mayor rezago temporal respecto a la intervención.

| Indicador | Tipo | Fuente | Metodología | Estado |
|---|---|---|---|---|
| Establecimientos económicos activos | Positivo | Cámara de Comercio de Cali | Conteo de matrículas vigentes con dirección dentro del polígono. | Incluido |
| Empleabilidad en el área | Positivo | Cámara de Comercio, empleo declarado. Exploración: GEIH + SAE, Rao & Molina, Censo 2018. | Fase 1: empleados reportados por establecimientos. Fase 2: micro-simulación SAE. | Incluido |
| Ingresos / ventas operacionales | Positivo | Cámara de Comercio de Cali | Promedio de ingresos operacionales declarados por establecimientos en el polígono. | Incluido |
| Cambio de vocación económica — CIIU | Positivo | Cámara de Comercio de Cali | Distribución porcentual de establecimientos por CIIU. Captura cambio de composición del tejido comercial. | Incluido |
| Valor catastral del área | Positivo | Catastro Distrital de Cali | Avalúo promedio ponderado por m² en predios del polígono. | En exploración |
| Licencias de construcción | Positivo | Curaduría Urbana de Cali | Conteo y valor de permisos emitidos en el polígono. Proxy de inversión privada. | En exploración |
| Progresión hacia la formalidad | Positivo | Secretaría de Desarrollo Económico — caracterización en curso | Proporción de vendedores informales con avance en criterios de formalización entre mediciones. | En exploración |
| Fiscalidad activa — facturación | Positivo | Hacienda Distrital / DIAN | Empresas con factura electrónica más volumen facturado. Requiere acuerdo de acceso bajo habeas data. | En exploración |

---

# 4. Territorios de aplicación

## 4.1 Pulmón de Oriente

| Aspecto | Detalle |
|---|---|
| Tipo de intervención | Recuperación de espacio ambiental y espacio público. Intervención de carácter ecológico y social. |
| Área de aplicación | Comunas 13, 14, 15 y 16, oriente de Cali. GeoJSON disponible. |
| Inicio de medición ITT | Línea base 2025. Series disponibles desde 2023. |
| Notas metodológicas | NDVI calculado sobre polígono completo con imagen Sentinel-2. Déficit habitacional incluye datos AHDI 2024–2026. Indicadores de Entorno Urbano y Movilidad muestran tendencia descendente que justifica la intervención. |

---

## 4.2 Av. Roosevelt

| Aspecto | Detalle |
|---|---|
| Tipo de intervención | Mejoramiento de corredor vial: adoquinado, bolardos, cicloruta, enterramiento de cables aéreos y equipamiento urbano. |
| Área de aplicación | Buffer de 100 m a cada lado del eje del corredor. Área resultante: 42,9 ha. Longitud aproximada: 641 m. GeoJSON disponible. |
| Inicio de medición ITT | Línea base al inicio de obras. Series 2023–2025 disponibles para Seguridad, Movilidad y Cohesión Social. |
| Notas metodológicas | El indicador de Déficit habitacional no aplica para este territorio, porque no hay proyectos de vivienda en el corredor. Actividad Económica se calculará con el dataset de Cámara de Comercio una vez georreferenciado. |

---

## 4.3 Barrio Obrero

| Aspecto | Detalle |
|---|---|
| Tipo de intervención | Transformación de espacio público histórico con componente de patrimonio cultural. Incluye parques, la “T” y equipamiento urbano. |
| Área de aplicación | Polígono del área de intervención. GeoJSON disponible. |
| Inicio de medición ITT | Línea base 2025. Series 2023–2025 disponibles para Seguridad y Movilidad. |
| Diferencial metodológico | Incluye una dimensión de Cultura y Patrimonio específica para este territorio, basada en el Plan Especial de Salvaguarda — PES. Sus indicadores capturan la actividad de colectivos de salsa y melómanos en el polígono. |
| Notas metodológicas | Actividad Económica se calculará con el mismo modelo aplicado a Roosevelt, usando el dataset de Cámara de Comercio. |

---

## 4.4 Av. Ciudad de Cali

| Aspecto | Detalle |
|---|---|
| Tipo de intervención | Infraestructura vial con embellecimiento urbano. Intervención distribuida en ocho tramos del corredor. |
| Área de aplicación | Polígono por tramos de intervención. GeoJSON en elaboración. |
| Inicio de medición ITT | Línea base al inicio de obras. Series 2023–2025 disponibles para Seguridad y Movilidad. |
| Notas metodológicas | Indicadores de Entorno Urbano, Educación y Cohesión Social pendientes de fuentes. La normalización de los indicadores de Seguridad y Movilidad está en proceso de homologación con la metodología de los demás territorios. |

---

# 5. Diseño de evaluación de impacto

## 5.1 Cadena causal: Output → Outcome → Impact

| Nivel | Definición |
|---|---|
| Output | Lo ejecutado físicamente: obra construida, equipamiento entregado. |
| Outcome | Cambios inmediatos en la dinámica del territorio por el uso de la obra: afluencia peatonal, reducción de siniestralidad. |
| Impact | Efectos sostenidos en seguridad, ingresos, tejido social y calidad de vida. |

---

## 5.2 Territorio espejo o zona de control

Para atribuir los cambios del ITT a la intervención y no a tendencias externas, como ciclo económico o temporada, cada territorio de intervención requiere un corredor o zona de comparación que no reciba intervención física en el período de medición.

### Parámetros para selección del territorio espejo para Av. Roosevelt

| Parámetro | Criterio |
|---|---|
| Longitud del corredor | Entre 500 y 700 metros. |
| Buffer | 100 m. |
| Área resultante | Entre 38 y 48 hectáreas. |
| Tipología urbana | Uso mixto comercial-residencial comparable a Roosevelt. |
| Intervención física | Sin intervención física planificada en el período 2026–2028. |
| Validación técnica | Densidad de intersecciones entre 400 y 700/km² calculada con el mismo script OSMnx. |

---

## 5.3 Periodicidad de medición

| Dimensión | Periodicidad | Cortes de seguimiento |
|---|---|---|
| Seguridad | Trimestral | T1, T2, T3, T4 por año. |
| Movilidad | Trimestral | T1, T2, T3, T4 por año. |
| Entorno Urbano | Anual / imagen disponible | NDVI según disponibilidad Sentinel-2. Caminabilidad: antes de obra y post-obra. |
| Educación y Desarrollo | Anual | Corte por año lectivo. |
| Cohesión Social | Trimestral | T1, T2, T3, T4 por año. |
| Actividad Económica | Anual / semestral | Línea base 2023–2025. Cortes post-intervención a 6 y 12 meses. |

---

# 6. Fuentes de datos, herramientas y acceso

## 6.1 Fuentes institucionales

| Fuente | Dimensión | Tipo de acceso | Notas |
|---|---|---|---|
| Observatorio de Seguridad y Justicia del Valle del Cauca | Seguridad / Cohesión Social | Institucional | Datos trimestrales georreferenciados por tipo de delito. |
| Secretaría de Movilidad / SIMUR | Movilidad | Institucional | Siniestralidad vial. Posible fuente de conteo peatonal si hay cámaras en el corredor. |
| Copernicus / Sentinel-2 | Entorno Urbano | Libre — descarga directa | NDVI y área verde neta. Procesamiento de imágenes Sentinel-2 gestionado por DATIC. |
| Secretaría de Educación / SIMAT | Educación y Desarrollo | Institucional | Matrícula, deserción, repitencia y ratio docente. |
| Secretaría de Recreación y Deporte | Educación y Desarrollo | Institucional | Cobertura deportiva activa por escenario. |
| Secretaría de Bienestar Social | Cohesión Social | Institucional | Concentración de vulnerabilidad activa — caracterización Sub PyE. |
| Secretaría de Vivienda / AHDI | Entorno Urbano | Institucional | Solo aplica para Pulmón de Oriente. No aplica para Roosevelt. |
| Cámara de Comercio de Cali | Actividad Económica | Acuerdo de intercambio | Dataset 2023–2025 con ID, dirección, CIIU, tamaño, empleo y ventas. |
| Catastro Distrital de Cali | Actividad Económica / Entorno | Datos abiertos — descarga directa | datos.cali.gov.co — Información Histórica de Predios. 763.249 registros 2023. Codificación IGAC. |
| DANE / GEIH + Censo 2018 | Actividad Económica | Libre — descarga directa | Empleabilidad por micro-simulación SAE, Rao & Molina. Fase posterior. |
| IMAE Cali, datos abiertos | Variable de control | Libre — datos.cali.gov.co | Índice Mensual de Actividad Económica. 81 registros. Sirve para aislar tendencias de ciclo económico general frente al efecto de la intervención. |

---

## 6.2 Fuentes abiertas y herramientas técnicas

| Herramienta / Fuente | Uso en el ITT | Acceso | Notas |
|---|---|---|---|
| OpenStreetMap / OSMnx — Python | Índice de caminabilidad peatonal en corredores de intervención. | Libre — sin API Key | Métricas calculadas para Roosevelt en mayo de 2026. Notebook Colab disponible. Decisión de inclusión en el ITT pendiente de validación metodológica. |
| Overture Maps Foundation | Inventario de POIs en el polígono. Exploración de indicador de cambio de vocación económica. | Libre — sin API Key | 474 POIs en Roosevelt, mayo de 2026. Notebook Colab disponible. Indicador en revisión para inclusión en el ITT. |
| Meta Data for Good — Population Density Maps | Población residente en el área de influencia y perfil demográfico. Aplica principalmente a Pulmón de Oriente. | Libre — HDX / AWS | Resolución 30 m. Colombia disponible. Última actualización 2022. Descarga: data.humdata.org. |
| Meta Data for Good — Movement Distribution Maps | Movilidad general de la población a nivel de zona. Variable de contexto. | Libre — HDX | Series mensuales diciembre 2022 – 2025. Granularidad: área administrativa, no corredor específico. |
| Google Maps / Popular Times | Afluencia en puntos específicos del corredor. | No disponible programáticamente | Descartado: dato no expuesto en API oficial. Cualquier extracción sería scraping frágil. |
| SIMUR — cámaras de seguridad | Conteo peatonal y vehicular en el corredor. | Institucional — gestión con Movilidad | Pendiente verificar cobertura en corredor Roosevelt. |

---

## Cierre del documento

Documento elaborado por el **Equipo de Gobierno de Datos · Alcaldía Distrito Santiago de Cali · Mayo 2026**.

**Versión:** 1.0  
**Actualización prevista:** tras validación con ICESI y operación del datalake.
