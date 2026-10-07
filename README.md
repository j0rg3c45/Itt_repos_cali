# ITT - Transformacion Territorial

Repositorio para calcular y comparar el **Indice de Transformacion Territorial (ITT)** en zonas de intervencion urbana de Cali, Colombia.

El proyecto esta organizado para trabajar con:

- Un notebook por zona.
- Un notebook comparativo entre zonas.
- Una carpeta de datos por zona.
- Una carpeta de salidas por zona.
- Documentacion metodologica y operativa.
- Una carpeta `agent/` con contexto y knowledge base para agentes de IA.

## Estado actual

| Notebook | Zona | Estado |
|---|---|---|
| `notebooks/01_itt_roosevelt.ipynb` | ITT Roosevelt | Implementado |
| `notebooks/02_itt_avenida_ciudad_de_cali.ipynb` | Avenida Ciudad de Cali | Implementado |
| `notebooks/03_itt_barrio_obrero.ipynb` | Barrio Obrero | Implementado |
| `notebooks/08_itt_ciudad_paraiso_5dim.ipynb` | Ciudad Paraiso (Comuna 3) | Implementado — Educacion fuera de alcance de este repo |
| `notebooks/04_itt_pulmon_oriente_2026.ipynb` | Pulmon de Oriente 2026 | Parcial |
| `notebooks/05_comparativo_itt_zonas.ipynb` | Comparativo | Plantilla |

Notas de estado:

- `02_itt_avenida_ciudad_de_cali.ipynb` sigue pendiente de migrar de min-max relativo a `ref_min/ref_max` fijos.
- `03_itt_barrio_obrero.ipynb` ya usa `ref_min/ref_max` fijos y es la referencia metodologica vigente dentro del repo.
- En `03_itt_barrio_obrero.ipynb`, `Entorno Urbano` ya puede recalcularse con un proxy basado en `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx` para `Comuna 9`.
- Ese proxy de `Entorno Urbano` es un corte anual `2024`, no una serie mensual o trimestral observada.
- `01_itt_roosevelt.ipynb` ya fue adaptado con la estructura de Barrio Obrero y usa `ref_min/ref_max` fijos.
- `05_comparativo_itt_zonas.ipynb` sigue como base de trabajo y depende de resultados homologos exportados.

## Metodo vigente

El metodo vigente del proyecto usa:

- Cinco dimensiones: Seguridad, Movilidad, Entorno Urbano, Educacion y Desarrollo, Cohesion Social.
- Pesos: 30%, 25%, 20%, 13%, 12%.
- Normalizacion con umbrales fijos `ref_min/ref_max`.
- Scores referentes provisionales cuando una dimension aun no tiene datos propios.

Regla metodologica clave:

- No usar min-max relativo de la muestra para zonas pequenas o con bajo volumen de eventos.

La referencia principal para agentes y decisiones metodologicas esta en:

- `agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md`

## Estructura del proyecto

```text
itt-transformacion-territorial/
|-- README.md
|-- requirements.txt
|
|-- data/
|   |-- itt_roosevelt/
|   |-- itt_avenida_ciudad_de_cali/
|   |-- itt_barrio_obrero/
|   `-- referencia/
|
|-- notebooks/
|   |-- 01_itt_roosevelt.ipynb
|   |-- 02_itt_avenida_ciudad_de_cali.ipynb
|   |-- 03_itt_barrio_obrero.ipynb
|   |-- 04_itt_pulmon_oriente_2026.ipynb
|   `-- 05_comparativo_itt_zonas.ipynb
|
|-- outputs/
|   |-- itt_roosevelt/
|   |-- itt_avenida_ciudad_de_cali/
|   |-- itt_barrio_obrero/
|   `-- consolidado/
|
|-- docs/
|   |-- 01_contexto_proyecto.md
|   |-- 02_metodologia_itt.md
|   |-- 03_fuentes_datos.md
|   `-- 04_manual_ejecucion.md
|
`-- agent/
    |-- context/
    |-- prompts/
    `-- knowledge_base/
```

## Orden sugerido de trabajo

1. Ubicar o cargar los datos de la zona en `data/`.
2. Ejecutar el notebook de la zona correspondiente.
3. Exportar resultados a `outputs/`.
4. Ejecutar el comparativo cuando existan resultados homologos de las zonas.
5. Actualizar `agent/context/` y `agent/knowledge_base/` con metodologia, fuentes y resultados.

## Seguimiento reciente

- Roosevelt ya cuenta con notebook implementado y alineado con la metodologia de `ref_min/ref_max` fijos.
- La data de Roosevelt ya esta disponible en `data/itt_roosevelt/` mediante ZIP y carpeta descomprimida de trabajo.
- Se agregaron Excel de vivienda en `data/referencia/` para evaluar mejoras en `Entorno Urbano`.
- `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx` ya se esta usando en `03_itt_barrio_obrero.ipynb` como proxy experimental de `Entorno Urbano` para `Comuna 9 / Barrio Obrero`.
- El notebook de Barrio Obrero ahora incluye una visualizacion `heatmap` de componentes del deficit cualitativo 2024 para explicar ese proxy.

## Recomendacion operativa

Mantener nombres de carpetas y archivos sin espacios simplifica el trabajo con Python, Git, rutas relativas y Google Colab.
