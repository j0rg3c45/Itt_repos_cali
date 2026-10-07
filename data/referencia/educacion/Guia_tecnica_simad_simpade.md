# Guía técnica: uso de SIMAT y SIMPADE

## Uso de SIMAT (Anexos 5A, 6A) y SIMPADE para el cálculo de indicadores educativos

Esta guía resume las reglas mínimas para reproducir los indicadores de **matrícula, repitencia, deserción, aprobación y cobertura** del municipio de **Santiago de Cali** a partir de los reportes oficiales del **Ministerio de Educación Nacional (MEN)**.

Está pensada como referencia rápida y no reemplaza la documentación técnica del MEN.

- **SIMAT:** Sistema Integrado de Matrícula.
- **SIMPADE:** Sistema de Información para el Monitoreo, Prevención y Análisis de la Deserción Escolar.

---

## 1. Qué contiene cada archivo

- **SIMAT Anexo 6A — matrícula total:** incluye los sectores Oficial, No Oficial y SGP Defensa. Tiene una fila por estudiante matriculado.

- **SIMAT Anexo 5A — matrícula del sector No Oficial únicamente:** corresponde a establecimientos privados. Tiene una fila por estudiante.

- **SIMPADE — registro de desertores:** contiene una fila por estudiante en estado de deserción. Todos los registros del archivo son desertores y contiene registros de los tres sectores mencionados anteriormente.

---

## 2. Variables clave

Los nombres siguen la nomenclatura SIMAT/SIMPADE. Se deben respetar las mayúsculas y los espacios.

| Información | Nombre en SIMAT | Descripción |
|---|---|---|
| Código DANE sede | `DANE_ANTERIOR` | Identifica cada sede física. Llave para cruces. |
| Código DANE institución | `CODIGO_DANE` | Identifica la institución educativa que agrupa una o más sedes. |
| Sector | `SECTOR` | Solo en 6A. Valores: `OFICIAL`, `NO OFICIAL`, `SGP DEFENSA`. |
| Grado | `GRADO` | Numérico. `0` = Transición, `1-5` = Primaria, `6-9` = Secundaria, `10-11` = Media, `99` = Aceleración, `21-26` = Adultos, `12-13` y `41-45` = PFC, `-2` y `-1` = Prejardín/Jardín. |
| Sexo | `GENERO` | `F` = Femenino, `M` = Masculino. |
| Edad | `FECHA_NACIMIENTO` | Calcular edad simple: edad = año de referencia − año de nacimiento. |
| Repitente | `REPITENTE` | Binaria: `S` = repitente, `N` = no repitente. |
| Comuna sede | `COMUNA SEDE` | Solo en 6A. En 5A usar `COMUNA`. Para sedes oficiales se recomienda cruzar con IDESC para mayor precisión en corregimientos. |

---

## 3. Reglas críticas

### 3.1. Cómo construir el universo de matrícula

- **Oficial:** 6A con `SECTOR = OFICIAL`.
- **SGP Defensa:** 6A con `SECTOR = SGP DEFENSA`.
- **No Oficial:** se construye combinando 6A con `SECTOR = NO OFICIAL` más todo el archivo 5A.

En las sedes que aparecen en ambos archivos, los registros corresponden a poblaciones distintas y, por lo tanto, se suman. No se eliminan duplicados a nivel de sede.

---

### 3.2. Base de cálculo para indicadores de eficiencia

Los indicadores de **repitencia** y **deserción** se calculan exclusivamente sobre estudiantes en grados **0 a 11 más 99**, es decir:

- Preescolar transición.
- Básica.
- Media.
- Aceleración del aprendizaje.

Se excluyen del cálculo:

- Prejardín y jardín: grados `-2` y `-1`.
- Programas para adultos: grados `21` a `26`.
- Programas de formación complementaria — PFC: grados `12`, `13` y `41` a `45`.

---

### 3.3. Base de cálculo para cobertura

Las tasas de **cobertura bruta** y **cobertura neta** se calculan únicamente sobre grados **0 a 11**, es decir:

- Transición.
- Primaria.
- Secundaria.
- Media.

No incluyen:

- Aceleración.
- Adultos.
- PFC.
- Prejardín/Jardín.

Esto se debe a que esos programas no tienen una edad teórica definida en el rango oficial de **5 a 16 años** del MEN.

---

### 3.4. Comunas y corregimientos

- **Sector Oficial:** cruzar con IDESC por código DANE de sede, usando `EeCoDanAnt → EEComCor`, para obtener el código real de comuna o corregimiento.

- **No Oficial y SGP Defensa:** usar la columna `COMUNA` del Anexo 5A o `COMUNA SEDE` del 6A para SGP Defensa.

Códigos territoriales:

| Código | Territorio |
|---|---|
| `1-22` | Comunas urbanas |
| `51-65` | Corregimientos rurales |
| `81` | Zona de expansión |

---

### 3.5. Cálculo de edad para cobertura neta

Usar edad simple:

```text
edad = año de referencia − año de FECHA_NACIMIENTO