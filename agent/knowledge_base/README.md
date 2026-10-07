# Knowledge base del agente

Guardar aqui los documentos y resultados que un agente debe consultar para responder con contexto tecnico y metodologico correcto.

## Prioridad de consulta

1. `Guia_ITT_Metodologia_Notebook.md`
2. Resultados exportados por notebooks
3. Fuentes de datos registradas
4. Resumenes ejecutivos por zona
5. Comparativos consolidados

## Contenido recomendado

- Documento metodologico vigente.
- Excels generados por notebooks.
- Resumenes ejecutivos por zona.
- Comparativo consolidado.
- Inventario de fuentes y observaciones de calidad.
- Referencias auxiliares en evaluacion metodologica, como insumos de vivienda para `Entorno Urbano`.

## Regla de consistencia

Si existe diferencia entre un resumen corto de `docs/` y la guia metodologica completa, el agente debe priorizar la guia metodologica completa y luego verificar el estado real de los notebooks.

## Estado de referencia actual

- `03_itt_barrio_obrero.ipynb` sigue siendo la referencia metodologica principal.
- `01_itt_roosevelt.ipynb` ya replica esa estructura con adaptaciones de corredor.
- `02_itt_avenida_ciudad_de_cali.ipynb` sigue siendo la principal deuda de migracion metodologica.
