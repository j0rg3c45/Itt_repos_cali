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
