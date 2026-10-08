# Protocolo de Conexión a AWS — Proyecto CaliTrack / ITT

Guía de acceso a los recursos AWS del proyecto (datalake S3, pipeline de datos).
Autenticación por **IAM Identity Center (SSO)** — no se usan llaves estáticas.

> Seguridad: este documento describe perfiles y procedimiento, no credenciales.
> Las sesiones SSO son temporales y se renuevan con `aws sso login`. No se deben
> commitear llaves de acceso ni tokens al repositorio.

> **REGLA DE AUTORIZACIÓN:** la conexión a AWS y cualquier comando contra la nube
> (`aws sso login`, `aws s3 ...`, `aws sts ...`, lecturas/escrituras al datalake, etc.)
> **solo se ejecutan cuando el usuario lo autorice explícitamente** en el momento.
> Ningún agente ni automatización debe conectarse a AWS por iniciativa propia, aunque
> haya una sesión SSO activa. Siempre pedir confirmación antes de correr un comando AWS.

## 1. Datos de acceso

| Parámetro | Valor |
|---|---|
| Portal SSO | https://d-906780cf79.awsapps.com/start |
| Usuario | gobiernodedatos.jorgecas@gmail.com |
| Región | us-east-1 |
| Autenticación | IAM Identity Center (SSO), sin llaves estáticas |

## 2. Perfiles configurados (`~/.aws/config`)

| Perfil | Cuenta | Rol SSO | Para qué |
|---|---|---|---|
| `default` | 802479323033 | PS-aca-quick-kiro-access | Acceso rápido (solo S3) |
| `calitrack` | 285757764705 | PS-CaliTrack | Pipeline de datos (sin API Gateway) |
| `calitrack-aca` | 285757764705 | PS-ACA-CaliTrack | Pipeline + API Gateway |

## 3. Recursos conocidos

| Recurso | ARN / Identificador | Cuenta | Perfil con acceso |
|---|---|---|---|
| Datalake ITT (S3) | `arn:aws:s3:::aca-prod-calitrack-itt-datalake` | 285757764705 | `calitrack` / `calitrack-aca` |

> El perfil `default` (cuenta 802479323033) **no** tiene permiso de `s3:ListBucket`
> sobre el datalake — da `AccessDenied`. Para el datalake usar `calitrack` o `calitrack-aca`.

### Estructura del datalake (capas por zona S3)

```
s3://aca-prod-calitrack-itt-datalake/
├── raw/          datos originales de ingesta (NO modificar)
├── curated/      datos limpios y procesados
├── analytics/    salidas para tableros
├── reference/    datos de referencia / catálogos
└── pruebas/      sandbox / pruebas
```

Ejemplo de contenido en `pruebas/itt_Ciudad_Paraiso/` (verificado 2026-10-08):
dimensiones 1-6 (incluye `6_Dimension_Educacion/` con matrícula, indicadores y
estudiantes-por-docente 2026, e `Infraestructura/`), más NDVI y censo arbóreo.
Nota: el datalake tiene datos de Educación que localmente estaban "fuera de alcance".

## 4. Procedimiento de conexión

```bash
# 1) Iniciar sesión SSO del perfil que corresponda (abre el navegador)
aws sso login --profile calitrack-aca

# 2) Verificar identidad (debe mostrar la cuenta 285757764705 y el rol PS-ACA-CaliTrack)
aws sts get-caller-identity --profile calitrack-aca

# 3) Listar el datalake
aws s3 ls s3://aca-prod-calitrack-itt-datalake/ --profile calitrack-aca

# 4) (opcional) fijar el perfil para toda la sesión de terminal
#    PowerShell:  $env:AWS_PROFILE = "calitrack-aca"
#    bash:        export AWS_PROFILE=calitrack-aca
```

## 5. Elección de perfil según la tarea

- **Explorar / leer el datalake S3** → `calitrack` o `calitrack-aca`.
- **Trabajar con el pipeline + API Gateway** → `calitrack-aca`.
- **Acceso rápido genérico a S3 (otra cuenta)** → `default`.

## 6. Diagnóstico de errores comunes

| Síntoma | Causa probable | Acción |
|---|---|---|
| `AccessDenied` en `s3:ListBucket` | Perfil/rol equivocado (p.ej. `default` sobre el datalake) | Usar `--profile calitrack-aca` |
| `Token has expired` / `SSO session expired` | Sesión SSO vencida | `aws sso login --profile <perfil>` |
| `The config profile could not be found` | Perfil no configurado en esa máquina | Revisar `aws configure list-profiles` |

## 7. Notas

- Las sesiones SSO caducan; si un comando falla por token, re-ejecutar `aws sso login`.
- La región por defecto del proyecto es `us-east-1`.
- No versionar `~/.aws/credentials` ni ningún token temporal en el repositorio.

---

# Protocolo de Creación y Nomenclatura de Recursos AWS — CaliTrack

> **Recordatorio de autorización:** crear, modificar o etiquetar recursos en AWS son
> acciones que **solo se ejecutan con autorización explícita del usuario** (igual que la
> conexión). El agente propone el comando y espera confirmación antes de correrlo.
> Crear recursos en la nube es una acción de alto impacto: siempre confirmar primero.

## 8. Regla de nombres

Todo recurso se nombra con esta estructura:

```
aca-prod-<dominio>-<funcion>[-<detalle>]
```

| Componente | Valor | Significado |
|---|---|---|
| `aca` | fijo | Alcaldía de Cali |
| `prod` | fijo | Entorno productivo |
| `<dominio>` | ej. `sismo`, `calitrack` | Área o proyecto |
| `<funcion>` | ej. `calidad-datos`, `cruce-subsidios` | Qué hace el recurso |
| `[-<detalle>]` | opcional | Precisión extra (`-to-curated`, `-rud`) |

Reglas de forma:
- Solo **minúsculas, números y guiones** (`-`). Nada de espacios, tildes ni mayúsculas.
- **Sin emojis** (política del proyecto).
- Descriptivo pero corto: el nombre debe decir qué hace sin abrir el recurso.

Ejemplos reales del proyecto:
- `aca-prod-sismo-calidad-datos-to-curated`
- `aca-prod-sismo-cruce-subsidios-rud`
- `aca-prod-instantdb-to-s3`
- `aca-prod-openpyxl-layer`

## 9. Etiqueta obligatoria

Todo recurso creado lleva este tag (lo exige la política de permisos para EC2, RDS,
Logs, CloudWatch):

```
Proyecto = CaliTrack
```

## 10. Checklist antes de crear cualquier recurso

1. **Autorización explícita del usuario** para la creación concreta.
2. **Perfil correcto:** `--profile calitrack-aca` (el que tiene API Gateway) o `calitrack`.
3. **Región:** `us-east-1` siempre.
4. **Sesión SSO activa:** si expiró, `aws sso login --profile calitrack-aca`.
5. **Nombre** según el patrón `aca-prod-...`.
6. **Tag** `Proyecto=CaliTrack`.
7. **Permiso disponible:** confirmar que el rol activo tiene acceso al servicio.
8. **Verificar tras crear:** `get`/`list` para confirmar que quedó bien y con su tag.

## 11. Parámetros estándar por tipo de recurso

**Lambda:**

| Parámetro | Valor estándar |
|---|---|
| Runtime | `python3.14` |
| Layers | `AWSSDKPandas-Python314:11` + `aca-prod-openpyxl-layer:1` |
| Rol de ejecución | `aca-prod-damnificados-bronze-lambda-role` (lee `raw/`, escribe `curated/`) |
| Memoria / Timeout | según carga (ej. 1024 MB / 300 s cruces; 2048 MB / 900 s calidad) |
| Tag | `Proyecto=CaliTrack` |

**S3 — rutas de salida en el datalake:**

```
raw/        -> datos originales (NO modificar)
curated/    -> datos limpios y procesados
externo/    -> entregables a terceros (zona protegida)
analytics/  -> salidas para tableros
```

Siempre con subcarpeta por fecha: `curated/<fuente>/<YYYY-MM-DD>/` (idempotencia por fecha).

## 12. Ejemplos de creación

Crear una Lambda siguiendo el protocolo (PowerShell):

```powershell
aws lambda create-function `
  --function-name aca-prod-sismo-api-subsidios `
  --runtime python3.14 `
  --role arn:aws:iam::285757764705:role/aca-prod-damnificados-bronze-lambda-role `
  --handler lambda_function.lambda_handler `
  --timeout 60 --memory-size 512 `
  --tags Proyecto=CaliTrack `
  --zip-file fileb://function.zip `
  --profile calitrack-aca --region us-east-1
```

Etiquetar un recurso ya creado (ej. una API):

```powershell
aws apigatewayv2 tag-resource `
  --resource-arn <ARN-de-la-api> `
  --tags Proyecto=CaliTrack `
  --profile calitrack-aca --region us-east-1
```

## 13. Reglas de oro

- **No tocar** `raw/` ni las zonas protegidas `raw/blend_instantdb/` y `externo/`.
- **No crear ni editar roles IAM** (sin permiso); usar los roles existentes.
- **Prefijo + tag siempre:** sin ellos, el recurso no cumple la gobernanza del proyecto.
- **Idempotencia por fecha:** las salidas van a subcarpeta del día, sin sobrescribir corridas previas.
- **Verificar tras crear:** confirmar con un `get`/`list` que el recurso quedó bien y con su tag.
