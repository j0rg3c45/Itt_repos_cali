# Contexto para agente - Proyecto ITT

Este agente apoya consulta, interpretacion y explicacion del **Indice de Transformacion Territorial (ITT)** dentro del repositorio `itt-transformacion-territorial`.

## Objetivo del proyecto

Calcular el ITT para zonas de intervencion urbana en Cali y comparar resultados entre zonas.

## Zonas del repo

- ITT Roosevelt.
- Avenida Ciudad de Cali.
- Barrio Obrero.

## Estado actual

- `01_itt_roosevelt.ipynb`: implementado con estructura homologada a Barrio Obrero y `ref_min/ref_max` fijos. Periodo 2023-2025.
- `02_itt_avenida_ciudad_de_cali.ipynb`: implementado y actualizado — `ref_min/ref_max` fijos, 3 ZIPs, heatmaps por tramo con orden geografico norte→sur, paleta Okabe-Ito. Periodo 2023-2026 T1.
- `03_itt_barrio_obrero.ipynb`: implementado y actualizado — DATIC 2023-2026 T1, datos directamente en carpetas por dimension (sin ZIP), paleta Okabe-Ito, heatmaps cividis, graficas trimestrales linea+relleno, NaN enmascarado para 2026 Q2-Q4.
- `04_itt_pulmon_oriente_2026.ipynb`: salida parcial de seguimiento.
- `05_comparativo_itt_zonas.ipynb`: plantilla comparativa.

## Regla metodologica para agentes

La referencia metodologica vigente del proyecto esta en:

- `agent/knowledge_base/Guia_ITT_Metodologia_Notebook.md`

Los agentes deben asumir como correcto:

- Uso de `ref_min/ref_max` fijos.
- Referentes provisionales para dimensiones sin datos propios.
- Necesidad de escalar refs segun tamano de zona.

Los agentes no deben asumir como vigente:

- Min-max relativo como metodo recomendado general.

## Uso esperado por el agente

El agente debe diferenciar entre:

- Metodologia vigente.
- Implementacion ya migrada.
- Implementacion pendiente de migrar.
- Datos presentes en el repo.
- Datos esperados pero no versionados.

## Seguimiento reciente

- Roosevelt ya dispone de datos fuente en `data/itt_roosevelt/`.
- Se revisaron errores de consistencia por `ano` y `año`; la convencion vigente en Roosevelt es `año`.
- Barrio Obrero migrado de ZIP a estructura de carpetas por dimension — archivos DATIC actualizados a 2023-2026 T1.
- Paleta Okabe-Ito y heatmaps cividis aplicados en notebooks 02 y 03.
- Graficas trimestrales cambiadas de barras agrupadas a linea+relleno con NaN para periodos sin datos.
- `data/referencia/` contiene ademas `Caracterizacion Personas Sub PyE (2025).xlsx` (24.087 registros, Secretaria de Bienestar Social) y `Caracterizacion R.A. 2026 corte may-6.xlsx`. Indicador contextual derivado: concentracion de vulnerabilidad activa = 54.1 por 1.000 hab — solo contexto, no implementado en ITT aun.
- `03_itt_barrio_obrero.ipynb` ya usa experimentalmente `BD_DEFICIT_HABITACIONAL_COM_CORREG_2024 (1).xlsx` para recalcular `Entorno Urbano` con `Comuna 9` como proxy territorial.
- Ese insumo de `Entorno Urbano` es un corte anual `2024`; la visualizacion recomendada es un `heatmap` de componentes del deficit cualitativo.
