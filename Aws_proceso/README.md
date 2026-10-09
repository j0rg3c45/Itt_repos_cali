# Aws_proceso — Trabajo del ITT en AWS

Carpeta que agrupa **todo lo que construyamos del ITT sobre AWS**: scripts del pipeline
de datos (medallón Bronze/Silver/Gold), funciones Lambda, la capa API, configuración de
infraestructura y utilidades para el datalake.

> **Regla de autorización:** ninguna conexión ni comando contra AWS (conectar, leer el
> datalake, crear/editar/etiquetar recursos) se ejecuta sin **autorización explícita del
> usuario** en el momento. Ver `docs/07_conexion_aws_calitrack.md`.

## Contexto de referencia

Antes de trabajar aquí, leer:
- `agent/context/arquitectura_aws_proceso_data.md` — arquitectura objetivo (medallón + API).
- `docs/07_conexion_aws_calitrack.md` — conexión SSO, perfiles, nomenclatura de recursos.
- `docs/08_estructura_aws_proceso_data_itt.md` — hoja de ruta del proceso de datos.

## Datos de la cuenta (CaliTrack / datalake ITT)

| Dato | Valor |
|---|---|
| Cuenta | `285757764705` |
| Rol SSO | `PS-ACA-CaliTrack` |
| Perfil CLI | `calitrack-aca` |
| Región | `us-east-1` |
| Datalake | `s3://aca-prod-calitrack-itt-datalake/` |

## Estructura de la carpeta

```
Aws_proceso/
├── README.md              # este archivo
├── pipeline/              # scripts del pipeline medallón (bronze/silver/gold)
├── lambdas/               # código de funciones Lambda (una subcarpeta por función)
├── api/                   # capa API (contrato de endpoints, handlers)
├── infra/                 # plantillas/config de infraestructura (IaC, policies de ejemplo)
└── notebooks_exploracion/ # notebooks de exploración del datalake (lectura)
```

## Convenciones

- **Nomenclatura de recursos AWS:** `aca-prod-calitrack-<funcion>[-<detalle>]`
  (minúsculas y guiones, sin tildes ni emojis). Tag obligatorio `Proyecto=CaliTrack`.
- **Capas S3:** `raw/` (crudo, no tocar) → `curated/` (limpio) → `analytics/` (consumo).
  Salidas idempotentes por fecha: `curated/<fuente>/<YYYY-MM-DD>/`.
- **No** modificar `raw/` ni zonas protegidas (`raw/blend_instantdb/`, `externo/`).
- **No** crear ni editar roles IAM; usar los existentes.
- No versionar credenciales ni tokens; el acceso es por SSO.

## Estado

Carpeta recién creada. Vacía de implementación por ahora — se irá poblando a medida que
se construya el pipeline y la API, siempre con autorización explícita para cada acción
en la nube.
