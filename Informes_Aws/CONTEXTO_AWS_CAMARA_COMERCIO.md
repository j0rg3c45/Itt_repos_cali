# Contexto AWS - Geocodificacion Camara de Comercio (ITT)

**Proyecto:** CaliTrack / ITT - Alcaldia de Santiago de Cali
**Equipo:** Gobierno de Datos (CDO)
**Fecha:** 2026-10-09
**Autor de la ejecucion:** gobiernodedatos.jorgecas@gmail.com

---

## 1. Objetivo

Geocodificar masivamente las direcciones de los establecimientos del Registro
Mercantil (Camara de Comercio de Cali) para poder ubicarlos en el mapa, usando
la API oficial de geocodificacion de la Alcaldia. El resultado alimenta el
analisis microterritorial de unidades productivas.

---

## 2. Conexion a AWS

### 2.1 Acceso
- **Metodo:** IAM Identity Center (SSO). No se usan llaves estaticas.
- **Portal SSO:** https://d-906780cf79.awsapps.com/start
- **Usuario:** gobiernodedatos.jorgecas@gmail.com
- **Region:** us-east-1 (toda la operacion).

### 2.2 Perfiles CLI (~/.aws/config)
| Perfil | Cuenta | Rol SSO | Uso |
|---|---|---|---|
| `default` | 802479323033 | PS-aca-quick-kiro-access | Solo S3 |
| `calitrack` | 285757764705 | PS-CaliTrack | Pipeline de datos (sin API Gateway) |
| `calitrack-aca` | 285757764705 | PS-ACA-CaliTrack | **Perfil de trabajo actual** (+ API Gateway) |

- Los tres perfiles comparten la sesion SSO `my-sso`: un solo `aws sso login` activa todos.
- **Perfil de trabajo:** `calitrack-aca` (rol AWSReservedSSO_PS-ACA-CaliTrack_fd49340229c58266).
- Renovacion de sesion cuando el token expira:
  `aws sso login --profile calitrack-aca`

### 2.3 Permisos relevantes del rol PS-ACA-CaliTrack
- Habilitado: S3, Lambda, Athena, Glue, QuickSight, Step Functions, CloudWatch Logs,
  EventBridge (events/scheduler), EC2/RDS/IAM (solo lectura), API Gateway v1 y v2.
- Denegado: CloudFront.
- **NO tiene** `iam:PutRolePolicy` (no puede crear/editar roles ni politicas IAM).

---

## 3. Reglas de operacion (OBLIGATORIAS)

1. **Kiro (el agente) NUNCA borra nada en AWS.** Ningun `delete`, `rm`, vaciado de
   buckets, `delete-function`, `delete-rule`, etc. Si hace falta borrar, el agente
   prepara el comando y **el usuario lo ejecuta**. Sobrescribir con `put` si esta
   permitido; borrar no.
2. **Zonas protegidas en S3 (nunca tocar):** `raw/blend_instantdb/` y `externo/`.
3. **No se crean ni editan roles/politicas IAM.** Solo se usan roles ya existentes.
4. **Nomenclatura:** prefijo `aca-prod-...` y tag obligatorio `Proyecto: CaliTrack`.
5. **Region unica:** us-east-1.

---

## 4. Fuente de datos

- **Bucket:** `aca-prod-calitrack-itt-datalake` (distinto al de sismo).
- **Archivo:** `raw/camara_de_comercio/20260929-Reporte General Registro Mercantil.csv`
  - Tamano: ~291 MB, ~561.000 filas.
  - Separador: `;` | Encoding: latin-1 | Formato Excel sucio (valores como `="valor "`).
- **Columna de direccion a geocodificar:** `direccion_12` (direccion del establecimiento).
- **Columna de ciudad:** `nombre_11`.
- **Filtro aplicado:** solo Cali (`nombre_11 == "CALI"`), ~90% de los registros.
- **Direcciones unicas geocodificables (Cali):** 103.030.

### Columnas conservadas en la salida
`id_0`, `numeroInscrito_1` (matricula), `nombre_2` (estado del registro),
`codigo_10` (persona natural/sociedad), `razonsocial`, `identificacion_8` (NIT),
`nombre_20` (nombre comercial), `codigo_14` (CIIU), `nombre_11` (ciudad),
`direccion_12`, `comunaid_13`, mas las columnas de geocodificacion
(`direccion_normalizada`, `dir_estandarizada`, `latitud`, `longitud`, `barrio_geo`,
`comuna_geo`, `estrato_geo`, `georef_exacto`, `estado_geo`, `estado_geocodificacion`).

---

## 5. Lambda: aca-prod-geocodificador-camara-comercio-itt

- **Codigo:** `aws_lambda/geocodificador_camara_comercio_itt/lambda_function.py`
  (repositorio del proyecto apt_zonas).
- **Base:** replica del geocodificador del RUD (`aca-prod-geocodificador-rud`),
  adaptado a Camara de Comercio, con el normalizador de direcciones de
  `aca-prod-normalizacion-direcciones-sismo` integrado.

### Configuracion
| Parametro | Valor |
|---|---|
| Runtime | python3.14 |
| Memoria | 8192 MB (por el CSV de 291 MB) |
| Timeout | 900 s |
| Almacenamiento efimero | 2048 MB |
| Layer | AWSSDKPandas-Python314:11 |
| Rol de ejecucion | aca-prod-damnificados-bronze-lambda-role (S3FullAccess + salida a internet) |
| Tag | Proyecto=CaliTrack |

### Variables de entorno
`S3_BUCKET=aca-prod-calitrack-itt-datalake`,
`CSV_KEY=raw/camara_de_comercio/20260929-Reporte General Registro Mercantil.csv`,
`OUTPUT_PREFIX=curated/camara_de_comercio`, `BATCH_SIZE=12000`,
`SOLO_CIUDAD=true`, `CIUDAD_FILTRO=CALI`.

### API de geocodificacion
- Endpoint: `https://geocodificador.ia.cali.gov.co/api`
- Limites: 18.000 registros por archivo, 5 MB por CSV.
- Por eso el trabajo se divide en LOTES de 12.000 direcciones -> 9 lotes
  (8 de 12.000 + 1 de 7.030).

---

## 6. Flujo del proceso (reanudable: START / CHECK / RECOVER)

La API tarda y una Lambda muere a los 15 min; por eso el proceso se separa en fases
que guardan su estado en S3 y pueden retomarse.

### START  (`{"action":"START"}`)
1. Lee el CSV (291 MB) solo con las columnas necesarias.
2. Filtra Cali y normaliza las direcciones (reglas de nomenclatura de Cali).
3. Deduplica y divide en lotes de 12.000.
4. Envia cada lote al API -> recibe un `idProceso` por lote.
5. Guarda los `idProceso` y el estado en S3. Termina sin esperar (status 202).

### CHECK  (`{"action":"CHECK"}`)
1. Recupera el job activo desde S3.
2. Consulta el avance de cada `idProceso`.
3. Si alguno sigue < 100%: guarda avance y termina (202, "sigue procesando").
4. Si TODOS llegan a 100%: descarga resultados, los UNE por direccion normalizada,
   mapea coordenadas sobre todos los registros y publica el resultado (COMPLETED).

### RECOVER  (`{"action":"RECOVER"}`)
Registra `idProceso` de una corrida previa sin volver a enviar (rescate).

### Idempotencia
Compara el ETag del CSV: si el archivo no cambio, reutiliza el resultado y no vuelve
a llamar la API.

---

## 7. Estructura de salida en S3

`curated/camara_de_comercio/{fecha}/`
| Archivo | Contenido |
|---|---|
| `camara_comercio_geocodificado.csv` | SOLO los registros que SI obtuvieron coordenada (entregable principal) |
| `camara_comercio_no_geocodificado.csv` | Los que NO, con el motivo (estado_geocodificacion) |
| `resumen_geocodificacion.json` | Metricas de la corrida |
| `_jobs/` | Control interno del proceso (estado, lotes, direcciones_idesc, _SUCCESS) |

Punteros globales (fuera de la fecha, para localizar el job activo):
`curated/camara_de_comercio/_control/active.json` y `last_success.json`.

---

## 8. Automatizacion del CHECK (EventBridge)

- **Regla:** `aca-prod-cc-itt-check-5min` (EventBridge Rule clasico).
- **Frecuencia:** `rate(5 minutes)`, estado ENABLED.
- **Target:** la Lambda, con input constante `{"action":"CHECK"}`.
- **Permiso:** `lambda:AddPermission` para `events.amazonaws.com` (no requiere rol IAM nuevo).

### Apagado al terminar (decision operativa - Opcion 2)
- El Lambda NO se autoapaga: su rol de ejecucion no tiene `events:DisableRule`, y el
  rol PS-ACA-CaliTrack no tiene `iam:PutRolePolicy` para ampliarlo.
- Al confirmar COMPLETED, el apagado lo realiza el agente/usuario con el perfil
  `calitrack-aca` (es un `disable`, no un `delete`):
  ```
  aws events disable-rule --name aca-prod-cc-itt-check-5min --profile calitrack-aca --region us-east-1
  ```

---

## 9. Validacion y estado

- **Validacion local** de lectura + normalizacion sobre muestra (8.322 registros Cali):
  96% geocodificables. Ejemplos correctos:
  - `CR 108  44   75 AP 3  505` -> `CR 108 # 44 - 75`
  - `CALLE. 43 NRO. 111 - 50 INTERIOR 101...` -> `CL 43 # 111 - 50`
  - `VIA CALI - JAMUNDI KM 12...` -> marcada como NO geocodificable (rural), correcto.
- **Job 2026-10-09:** `20261009T164946-47e596fc`, 9 lotes, 103.030 direcciones unicas.
  Avance observado: 3.6% -> 23.6% -> 47.9% (en progreso).

---

## 10. Comandos operativos de referencia

```powershell
# Renovar sesion SSO
aws sso login --profile calitrack-aca

# START (payload en archivo para evitar problemas de comillas en PowerShell)
aws lambda invoke --function-name aca-prod-geocodificador-camara-comercio-itt `
  --invocation-type RequestResponse --cli-read-timeout 900 `
  --cli-binary-format raw-in-base64-out `
  --payload file://payload_start.json `
  --profile calitrack-aca --region us-east-1 salida.json

# CHECK manual
aws lambda invoke --function-name aca-prod-geocodificador-camara-comercio-itt `
  --invocation-type RequestResponse --cli-read-timeout 900 `
  --cli-binary-format raw-in-base64-out `
  --payload file://payload_check.json `
  --profile calitrack-aca --region us-east-1 salida.json

# Desactivar la regla al terminar (disable, NO delete)
aws events disable-rule --name aca-prod-cc-itt-check-5min `
  --profile calitrack-aca --region us-east-1
```

---

*Documento de contexto tecnico. Equipo de Gobierno de Datos (CDO), Alcaldia de Santiago de Cali.*
