# Diccionario de datos — Matrícula Sector Oficial 2024

Documento convertido a formato Markdown a partir del archivo Excel `22IF014_ acceso_permanencia_matricula_2024_0.xlsx`.

## 1. Información general

- **Título original:** DICCIONARIO DE DATOS -- Matrícula Sector Oficial 2024--
- **Dependencia:** Oficina Asesora de Planeación
- **Id. tabla:** —
- **Nombre de la tabla:** Anexo 6A depurado 30_04_2024
- **Contenido de la tabla:** Contiene la información de la matrícula del sector oficial para el año 2024. La fuente de información es el Anexo 6A del SIMAT con fecha de corte 30 de abril de 2024. Se realiza cruce con el directorio único de establecimientos con fecha de corte 31 de marzo de 2024. Para las informaciòn de víctimas del conflicto armado se solicita la identficación en el Registro Unico de Victimas - RUV con corte 31 de marzo de 2024
- **Número de variables documentadas:** 124

---

## 2. Pautas de diligenciamiento

| Campo | Descripción | Ejemplo de diligenciamiento |
| --- | --- | --- |
| Id. tabla | Identificación única y abreviada con la que se identifica la tabla que contiene los datos | CAP_01 |
| Nombre de la tabla | Nombre completo de la tabla que contiene los datos | Capítulo 1. EDID |
| Contenido de la tabla | Describa de formal general el contenido de la información o los datos que reposan en la tabla | Contiene información del capítulo 1 Diligenciamiento de funcionarios de la encuesta EDID |
| Llave Primaria | En este campo diligencie si la variable a documentar hace parte de la llave primaria.<br>- En caso afirmativo, diligencie con las letras "PK"<br>- En caso negativo, diligencie con "NO"<br><br>*PK= Primary Key | PK |
| Llave Foránea | En este campo diligencie si la variable a documentar hace parte de un campo o variable llave, de una tabla de referencia | Si la variable fuese un código de municipio y este a su vez es un identificador de una tabla de referencia llamada DIVIPOLA, se debería diligencia que "SI" porque corresponde a una llave foránea |
| Campo obligatorio | En este campo diligencie si la variable tiene la condición de ser obligatoria, es decir, que no puede estar en "nulo":<br>- Si el campo es obligatorio, diligencie "SI"<br>- Si el campo no es obligatorio, diligencie "NO" | NO |
| Clasificación del campo | En este campo diligencie si la variable tiene la condición de ser divulgado a una dependencia o entidad que no sea la administradora de la tabla<br>- Si el campo es de carácter "Reservado"<br>- Si el campo es de caracter "Confidencial"<br>- Si el campo es de carácter "Público" | Reservado |
| Id. de la variable | Identificación única y abreviada con la que se identifica la variable. El Id no debe contener espacios en blancos y se sugiere que no empiece con un número | P045_C1 |
| Descipción de la variable | Es la descripción textual de la variable. | Ha promovido la intervención de la ciudadanía en los asuntos públicos. |
| Tipo de datos | Determine el tipo de datos de la variable<br><br>Las Variables Numéricas: son aquellas en las cuales se almacenan valores numéricos, es decir, almacenan caracteres numéricos del 0 al 9, signos (+ y -) y punto decimal.<br><br>Las variables tipo carácter: esta formada por caracteres alfanuméricos (letras, números y caracteres especiales), pero se debe entender que aunque solo contenga números, tales números no son considerados como valor numérico sino como cualquier tipo de carácter.<br>Estas variables generalmente se definen para almacenar letras y caracteres especiales, por eso es importante que estén documentadas con la longitud que se requiere para su almacenamiento. Existen<br><br>Las Variables Fecha son utilizadas para almacenar fechas. Las fechas deben ser ingresadas en formato ISO y pueden incluir una fecha completa (AAAA - MM - DD), año y mes (AAAA - MM) o sólo año (AAAA). | Carácter (por ejemplo para identificar el departamento de Atlántico cuya identificación de variable es 05, el tipo de datos se debe especificar como carácter, porque si se determinaran como tipo número seria 5 y representaría una inconsistencia |
| Longitud | Es el máximo número de caracteres que pueden ser incluidos en una variable. Tenga en cuenta en las variables numéricas pacificar si contiene decimales | * Para una variable numérica con decimales se debe especificar así:<br>p(10,2)<br>Es decir, 10 enteros 2 decimales<br><br>* Para una varible carácter simplemnete la longitud de dominio, asi:<br>50 |
| Dominios (Categorías, valores) | Defina los dominios o valores válidos para esta variable | * Para dominios simples se documenta como el siguiente ejemplo:<br>1= Hombre<br>2= Mujer<br><br>* Para dominios complejos documente los valores sobre rangos<br>De 1 a 99999999999999<br>Feche desde xxxx hasta xxxx<br><br>* Para dominios basados en listas o tablas de referencia, documente<br>como el siguiente ejemplo<br>Este valor corresponde a un código válido de la DIVIPOLA<br>Este valor corresponde a un código válido de la CPC |
| Regla de validación (en lenguaje natural) | Describir la o las reglas específicas de validación del campo.<br>Enumere claramente cada regla que se debe aplicar a la Variable | Si país = 170 = Colombiano y edad es < que 18, entonces tipo documento no puede ser cedula(1), Cedula militar(4) o NIT (3). |

---

## 3. Diccionario de variables

| Id. de la variable | Descripción de la variable | Tipo de datos | Longitud | Llave primaria | Llave foránea | Campo obligatorio | Clasificación del campo | Dominios / categorías / valores | Regla de validación |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ANO_INF | Año de la información | Numérico | 4 | NO | NO | SI | Público | Valor 2024 | — |
| MUN_CODIGO | Municipio o Distrito | Cadena | 3 | NO | NO | SI | Público | 001' | — |
| NUMERO_LOCALIDAD | Número de la localidad | Numérico | 2 | NO | SI | SI | Público | Valores de 1 a 20 | Información del directorio con fecha de corte 31-03-2024 |
| NOMBRE_LOCALIDAD | Localidad | Numérico | 2 | NO | NO | SI | Público | 1 Usaquén<br>2 Chapinero<br>3 Santa Fe<br>4 San Cristóbal<br>5 Usme<br>6 Tunjuelito<br>7 Bosa<br>8 Kennedy<br>9 Fontibón<br>10 Engativá<br>11 Suba<br>12 Barrios Unidos<br>13 Teusaquillo<br>14 Los Mártires<br>15 Antonio Nariño<br>16 Puente Aranda<br>17 La Candelaria<br>18 Rafael Uribe Uribe<br>19 Ciudad Bolívar<br>20 Sumapaz | Información del directorio con fecha de corte 31-03-2024 |
| CODIGO_DANE | Código DANE del establecimiento | Numérico | 12 | PK | SI | SI | Público | Número de 12 digitos | — |
| NOMBRE_ESTABLECIMIENTO_EDUCATIVO | Nombre Establecimiento Educativo | Cadena | 67 | NO | NO | SI | Público | — | — |
| DANE_ANTERIOR | Código DANE de la Sede | Numérico | 12 | PK | SI | SI | Público | Número de 12 digitos | — |
| NOMBRE_SEDE_EDUCATIVA | Nombre Sede Educativa | Cadena | 78 | NO | NO | SI | Público | — | — |
| CONS_SEDE | Consecutivo de la sede | Numérico | 14 | NO | NO | SI | Público | Número de 14 digitos | — |
| COD_CLASE | Código clase de colegio | Numérico | 1 | NO | SI | SI | Público | 1<br>2 | — |
| CLASE_COLEGIO | Clase de colegio | Cadena | 40 | NO | NO | SI | Público | 1 Distrital<br>2 Distrital - Administración contratada | — |
| PER_ID | Identificador único del estudiante | Cadena | 8 | PK | NO | SI | Público | — | — |
| TIPO_DOCUMENTO | Código tipo de documento | Numérico | 2 | PK | SI | SI | Reservado | 1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13 | La combinación Tipo, Número y lugar de expedición de Documento debe ser única a nivel nacional. Si el tipo es 1(CC) y 2(TI) debe ser único por número de documento. |
| DESCRIP_TIP_DOC | Tipo de documento | Cadena | 46 | NO | NO | SI | Reservado | 1 Cédula de Ciudadanía<br>2 Tarjeta de Identidad<br>3 Cédula de Extranjería<br>5 Registro Civil de Nacimiento<br>6 Número de Identificación Personal (NIP)<br>7 Número Único de Identificación Personal (NUIP)<br>8 Número de Identificación establecido por la Secretaría de Educación<br>9 Certificado Cabildo 10 Permiso Especial de Permanencia<br>11 Visa<br>12 Tarjeta de movilidad fronteriza<br>13 Permiso de protección temporal | — |
| NRO_DOCUMENTO | Número de documento | Cadena | 17 | PK | NO | SI | Reservado | — | Para los documentos cedula de ciudadania tarjeta de identidad y registro civil el sistema SIMAT realiza las validaciones de formato establecidas por la Registraduría Nacional del Estado Civil, para el permiso especial de permanencia P.E.P las establecidas por migración Colombia.<br><br>No deben existir valores nulos |
| EXP_DEPTO | Código departamento de Expedición del documento | Cadena | 2 | NO | SI | SI | Reservado | — | — |
| DESCRIP_EXP_DEPTO | Nombre departamento de Expedición del documento | Cadena | 24 | NO | NO | NO | Reservado | — | Cruce con DIVIPOLA año 2023, descargada de<br>https://geoportal.dane.gov.co/servicios/descarga-y-metadatos/datos-geoestadisticos/?cod=112 |
| EXP_MUN | Código municipio de Expedición del documento | Cadena | 3 | NO | SI | NO | Reservado | — | — |
| DESCRIP_EXP_MUN | Nombre municipio de Expedición del documento | Cadena | 27 | NO | NO | NO | Reservado | — | — |
| APELLIDO1 | Primer Apellido del estudiante | Cadena | 21 | NO | NO | SI | Reservado | — | Solo se deben aceptar letras del alfabeto, ningún otro tipo de caracter. |
| APELLIDO2 | Segundo Apellido del estudiante | Cadena | 21 | NO | NO | NO | Reservado | — | — |
| NOMBRE1 | Primer Nombre del estudiante | Cadena | 21 | NO | NO | SI | Reservado | — | — |
| NOMBRE2 | Segundo Nombre del estudiante | Cadena | 21 | NO | NO | NO | Reservado | — | — |
| DIRECCION_RESIDENCIA | Dirección del estudiante | Cadena | 100 | NO | NO | SI | Reservado | — | Para ubicaciones de residencia no convencionales se debe anteponer a la direccion la sigla IND (Indicación) |
| TEL | Teléfono del estudiante | Cadena | 43 | NO | NO | NO | Reservado | — | — |
| RES_DEPTO | Código departamento donde reside el estudiante | Cadena | 2 | NO | SI | NO | Reservado | Códigos de departamento según Divipola | — |
| DESCRIP_RES_DEPTO | Nombre departamento donde reside el estudiante | Cadena | 58 | NO | NO | NO | Reservado | — | — |
| RES_MUN | Código municipio donde reside el estudiante | Cadena | 3 | NO | SI | NO | Público | Codigos de municipio según Divipola | La relación departamento y municipio debe estar acorde con la codificación definida por el DANE |
| NOM_RES_MUN | Nombre municipio donde reside el estudiante | Cadena | 28 | NO | NO | NO | Público | — | — |
| ESTRATO | Estrato socioeconómico del estudiante | Numérico | 1 | NO | NO | SI | Público | 0 Sin estrato<br>1 Estrato 1<br>2 Estrato 2<br>3 Estrato 3<br>4 Estrato 4<br>5 Estrato 5<br>6 Estrato 6 | Se realiza una recodificación de los valores 9 a 0 |
| SISBEN | Puntaje Sisbén metodología IV | Cadena | 9 | NO | NO | NO | Público | Grupo A: (desde A1 hasta A5)<br>Grupo B: (desde B1 hasta B7)<br>Grupo C: (desde C1 hasta C18)<br>Grupo D: (desde D1 hasta D21)<br>NO APLICA | — |
| FECHA_NACIMIENTO | Fecha de Nacimiento del estudiante | Fecha | 11 | NO | NO | SI | Reservado | — | La relación departamento y municipio debe estar acorde con la codificación definida por el DANE.<br><br>Solo puede ser vacío si el tipo documento es extranjería |
| NAC_DEPTO | Código departamento de Nacimiento del estudiante | Cadena | 2 | NO | SI | NO | Reservado | Códigos de departamento según Divipola | — |
| DESCRIP_NAC_DEPTO | Nombre departamento de Nacimiento del estudiante | Cadena | 58 | NO | NO | NO | Reservado | — | — |
| NAC_MUN | Código municipio de Nacimiento del estudiante | Cadena | 3 | NO | SI | NO | Reservado | Codigos de municipio según Divipola | La relación departamento y municipio debe estar acorde con la codificación definida por el DANE.<br><br>Solo puede ser vacío si el tipo documento es extranjería |
| DESCRIP_NAC_MUN | Nombre municipio de Nacimiento del estudiante | Cadena | 28 | NO | NO | NO | Reservado | — | — |
| GENERO | Género del estudiante | Cadena | 1 | NO | NO | SI | Público | F Femenino<br>M Masculino | — |
| PROVIENE_SECTOR_PRIV | Proviene de sector privado | Cadena | 1 | NO | NO | NO | Público | S Si<br>N No | — |
| PROVIENE_OTR_MUN | Proviene de otro municipio | Cadena | 1 | NO | NO | NO | Público | S Si<br>N No | — |
| TIPO_DISCAPACIDAD | Código tipo de discapacidad | Numérico | 2 | NO | SI | SI | Público | 1, 2, 3, 4, 7, 8, 10, 11, 12, 13, 14, 15, 17, 18, 19, 99 | A partir del año 2022, el SIMAT modifica la codificaciòn de esta variable, no siendo comparables con los valores que se tenian en vigencias anteriores. |
| DESCRIP_DISCPACIDAD | Tipo de discapacidad | Cadena | 35 | NO | NO | NO | Público | 1 'Discapacidad física'<br>2 'Discapacidad auditiva'<br>3 'Discapacidad visual'<br>4 'Discapacidad sordoceguera'<br>7 'Discapacidad múltiple'<br>8 'Discapacidad intelectual'<br>10 'Discapacidad múltiple'<br>11 'No es discapacidad'<br>12 'Discapacidad auditiva'<br>13 'Discapacidad auditiva'<br>14 'Discapacidad sordoceguera'<br>15 'Discapacidad física'<br>17 'No es discapacidad'<br>18 'Discapacidad mental-psicosocial'<br>19 'No es discapacidad'<br>99 'No aplica' | — |
| CAP_EXC | Código capacidades excepcionales | Numérico | 2 | NO | SI | SI | Público | 1, 2, 3, 4, 5, 6, 7, 9, 10, 11 | A partir del año 2022, el SIMAT modifica la codificaciòn de esta variable, no siendo comparables con los valores que se tenian en vigencias anteriores. |
| DESCRIP_CAP_EXEP | Capacidades excepcionales | Cadena | 69 | NO | NO | SI | Público | 1 'Capacidades Excepcionales'<br>2 'Talento Cientifico'<br>3 'Talento excepcional en ciencias naturales o básicas'<br>4 'Talento excepcional en artes o letras'<br>5 'Talento excepcional en actividad física, ejercicio y deporte'<br>6 'No aplica'<br>7 'Talento excepcional en ciencias sociales o humanas'<br>9 'No Aplica'.<br>10 'Talento excepcional en tecnología'<br>11 'Talento excepcional en liderazgo social y emprendimiento' | — |
| CODIGO_ETNIA | Código Etnia | Numérico | 3 | NO | SI | SI | Público | — | Se homologaron los códigos 998 y 999 al 0 'No Aplica'. |
| DESCRIP_ETNIA | Etnia | Numérico | 54 | NO | NO | SI | Público | 0 'No aplica'<br>1 'Achagua'<br>2 'Amorúa'<br>3 'Andoque'<br>4 'Arhuaco'<br>5 'Awa'<br>6 'Bara'<br>7 'Barasano'<br>8 'Barí'<br>9 'Betoye (Guahibo)'<br>10 'Bora'<br>11 'Kawiyarí (Cabiyari)'<br>12 'Karapana (Carapana)'<br>13 'Karijona (Carijona)'<br>14 'Chimilas'<br>15 'Chiricoa'<br>16 'Cocama'<br>17 'Coconuco'<br>18 'Kofán'<br>19 'Pijaos (Coyaimas - Natagaimas)'<br>20 'Cubeo'<br>21 'Cuiva (Cuiba - Kuiba)'<br>22 'Curripaco'<br>23 'Desano'<br>24 'Tamas (Dujos de Paniquita)'<br>25 'Embera'<br>26 'Embera Katío'<br>27 'Embera Chami'<br>28 'Eperara Siapidara'<br>29 'Guambiano (autodenominación Nam Misak)'<br>30 'Guanaca'<br>31 'Guayabero (autodenominación JIW)'<br>33 'Hitnú'<br>34 'Inga'<br>35 'Camenstsa (Kamsa o Kamentsa)'<br>36 'Kogui'<br>37 'Coreguaje'<br>38 'Letuama'<br>39 'Macaguaje'<br>40 'Nukak Makú (se incluyen Humhu, Juhup, Jujupda, Kakua)'<br>41 'Makuna'<br>42 'Masiware (Masiguare - Maiben)'<br>43 'Matapí'<br>44 'Miraña'<br>45 'Muinane'<br>46 'Muisca'<br>47 'Nonuya'<br>48 'Ocaina'<br>49 'Paéz (autodenominación Nasa)'<br>50 'Pastos'<br>51 'Piapoco'<br>52 'Piaroa'<br>53 'Piratapuyo'<br>54 'Pisamira'<br>55 'Puinave'<br>56 'Sáliva (Saliba)'<br>57 'Sikuani (Sicuani)'<br>58 'Siona'<br>59 'Siriano'<br>60 'Tsiripu (Tshiripo)'<br>61 'Taiwano'<br>62 'Tanimuka'<br>63 'Tariano'<br>64 'Tatuyo'<br>65 'Tikuna'<br>66 'Totoró'<br>67 'Tukano'<br>68 'Cuna (Tule)'<br>69 'Tuyuka'<br>70 'U´wa'<br>71 'Guanano (Wanano)'<br>72 'Wayuu'<br>73 'Uitotos (Huitoto - Witoto)'<br>74 'Wiwa'<br>75 'Waunana (Wounaan)'<br>76 'Yagua'<br>77 'Yanacona'<br>78 'Yauna'<br>79 'Yucuna'<br>80 'Yuko (Yukpa)'<br>81 'Yurí'<br>82 'Yuruti (Tapuya)'<br>83 'Zenú (Senu)'<br>84 'Quillacingas'<br>90 'Mura'<br>94 'Polindaras'<br>95 'Raizal'<br>96 'Kankuamo'<br>97 'Afrodescendiente'<br>98 'Palanquero'<br>99 'Mokana'<br>100 'Ambalo'<br>101 'Kichwa'<br>102 'Baniva'<br>103 'Guariquema'<br>104 'Jurumi (Urtumi)'<br>105 'Kizgo (Quisgo)'<br>106 'Macahua(N)'<br>107 'Murui (Murui - Wito)'<br>108 'Wipiwi'<br>109 'Yamalero'<br>110 'Yari'<br>111 'Yaruro'<br>112 'Mapayerry'<br>200 'Negritudes'<br>400 'Rom' | — |
| RES | Resguardo | Cadena | 4 | NO | NO | NO | Público | — | — |
| INS_FAMILIAR | Institución bienestar de origen | Cadena | 80 | NO | NO | NO | Público | — | — |
| TIPO_JORNADA | Código jornada | Numérico | 1 | NO | SI | SI | Público | 1 a 6 | — |
| DESCRIP_JORNADA | Jornada | Cadena | 13 | NO | NO | SI | Público | 1 Completa<br>2 Mañana<br>3 Tarde<br>4 Nocturna<br>5 Fin de semana<br>6 Única | — |
| CARACTER | Código carácter | Numérico | 1 | NO | SI | NO | Público | 0, 1, 2 | — |
| DESCRIP_CARACTER | Carácter | Numérico | 1 | NO | NO | NO | Público | 0 No aplica<br>1 Académico<br>2 Técnico | — |
| ESPECIALIDAD | Código especialidad | Cadena | 2 | NO | SI | NO | Público | 00, 05, 06, 07, 08, 09, 10, 16 | — |
| DESCRIP_ESPECIALIDAD | Especialidad | Cadena | 2 | NO | NO | NO | Público | 00 No aplica<br>01<br>05 Académico<br>06 Industrial<br>07 Otro<br>08 Comercial<br>09 Pedagógico<br>10 Agropecuario<br>16 Promoción Social | — |
| COD_GRADO | Código Grado | Numérico | 2 | NO | SI | SI | Público | -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 21, 22, 23, 24, 25, 26, 41, 42, 43, 44, 45, 99 | De acuerdo con el INSTRUCTIVO NUEVAS FUNCIONALIDADES SIMAT VERSIÓN 7.0.8.28, se modifica el registro de estudiantes que hacen parte del programa de formación complementaria que ofrecen las instituciones normalistas, en los sistemas de información dispuestos para el reporte de matrícula (SINEB y SIMAT). A partir de la vigencia 2023, quedan inhabilitados los grados doce (12) y trece (13) y esta matrícula debe reportarse en nuevos grados que pueden tomarse como semestres, de acuerdo con la necesidad que presente cada establecimiento educativo.<br><br>Cambia la denominación del grado 99 de "Aceleración del Aprendizaje" por "Aceleración primeras letras" |
| NOM_GRADO | Grado | Numérico | 2 | NO | NO | SI | Público | "-2 Pre-Jardín<br>-1 Jardín<br>0 Transición<br>1 Primero<br>2 Segundo<br>3 Tercero<br>4 Cuarto<br>5 Quinto<br>6 Sexto<br>7 Séptimo<br>8 Octavo<br>9 Noveno<br>10 Décimo<br>11 Once<br>21 Ciclo 1<br>22 Ciclo 2<br>23 Ciclo 3<br>24 Ciclo 4<br>25 Ciclo 5<br>26 Ciclo 6<br>41 INTR - Semestre introductorio<br>42 PFC 1 - Programa de formación complementaria 1<br>43 PFC 2 - Programa de formación complementaria 2<br>44 PFC 3 - Programa de formación complementaria 3<br>45 PFC 4 - Programa de formación complementaria 4<br>99 Aceleración del aprendizaje" | De acuerdo con el INSTRUCTIVO NUEVAS FUNCIONALIDADES SIMAT VERSIÓN 7.0.8.28, se modifica el registro de estudiantes que hacen parte del programa de formación complementaria que ofrecen las instituciones normalistas, en los sistemas de información dispuestos para el reporte de matrícula (SINEB y SIMAT). A partir de la vigencia 2023, quedan inhabilitados los grados doce (12) y trece (13) y esta matrícula debe reportarse en nuevos grados que pueden tomarse como semestres, de acuerdo con la necesidad que presente cada establecimiento educativo. |
| GRUPO | Grupo del estudiante | Cadena | 6 | NO | NO | SI | Público | — | — |
| METODOLOGIA | Código metodología | Numérico | 2 | NO | SI | SI | Público | 1, 9, 10, 11 | — |
| DESCRIP_METODOLOGIA | Metodología | Cadena | 45 | NO | NO | SI | Público | 1 'Educación Tradicional'<br>9 'Aceleración del aprendizaje'<br>10 'Programa para jóvenes en extraedad y adultos'<br>11 'Preescolar escolarizado | — |
| MATRICULA_CONTRATADA | Estudiantes en colegios de matrícula contratada | Cadena | 1 | NO | NO | NO | Público | S Si<br>N No | — |
| REPITENTE | Estudiantes Repitentes | Cadena | 1 | NO | NO | NO | Público | S Si<br>N No | — |
| NUEVO | Estudiantes Nuevos en la Institución | Cadena | 1 | NO | NO | NO | Público | S Si<br>N No | — |
| FUENT_RECUR | Código fuente de recursos | Numérico | 1 | NO | NO | NO | Público | 1, 2, 3, 4, 5 | — |
| FUENT_RECUR | Fuente de recursos | Cadena | 48 | NO | NO | NO | Público | 1 SGP<br>2 FNR<br>3 Recursos adicionales presupuesto nacional MEN<br>4 Otros Recursos de la Nación<br>5 Recursos Propios | — |
| ZON_ALU | Código zona residencia del estudiante | Numérico | 1 | NO | NO | NO | Público | 1, 2 | — |
| DESCRIP_ZONA_ALUMNO | Zona residencia del estudiante | Cadena | 6 | NO | NO | NO | Público | 1 Urbana<br>2 Rural | — |
| CAB_FAMILIA | Estudiante Madre Cabeza de Familia | Cadena | 1 | NO | NO | NO | Público | S Si<br>N No | — |
| BEN_MAD_FLIA | Beneficiario Hijos dependientes de Madre Cabeza de Familia | Cadena | 1 | NO | NO | NO | Público | S Si<br>N No | — |
| BEN_VET_FP | Beneficiario Veteranos de la Fuerza Pública | Cadena | 1 | NO | NO | NO | Público | S Si<br>N No | — |
| BEN_HER_NAC | Beneficiario Héroes de la Nación | Cadena | 1 | NO | NO | NO | Público | S Si<br>N No | — |
| CODIGO_INTERNADO | Internado | Numérico | 1 | NO | NO | NO | Público | 1 = Internado<br>2 = Semi-internado<br>3 = Ninguno | — |
| CODIGO_VALORACION_1 | Valoración desempeño I | Numérico | 1 | NO | NO | NO | Público | 1 Superior<br>2 Alto<br>3 Básico<br>4 Bajo | — |
| NUM_CONVENIO | Número del convenio | Cadena | 21 | NO | NO | NO | Público | — | — |
| APOYO_ACADEMICO_ESPECIAL | Código apoyo académico especial | Cadena | 2 | NO | SI | NO | Público | 01, 02, 03, 04, 05 | Nueva variable desde el año 2022<br>Su actualización es progresiva por lo que presenta campos sin sin informaciòn |
| DESCRIP_APOYO_ACADEMICO | Apoyo académico especial | Cadena | 41 | NO | NO | NO | Público | 01 No Aplica<br>02 Aula hospitalaria<br>03 Atención domiciliaria<br>04 Atención en institución de apoyo<br>05 Atención en el establecimiento educativo | Nueva variable desde el año 2022<br>Su actualización es progresiva por lo que presenta campos sin sin informaciòn |
| SRPA | Código sistema responsabilidad penal | Cadena | 2 | NO | SI | NO | Público | 01, 02, 03 | Nueva variable desde el año 2022<br>Su actualización es progresiva por lo que presenta campos sin sin informaciòn |
| DESCRIP_SRPA | Sistema responsabilidad penal | Cadena | 26 | NO | NO | NO | Público | 01 No Aplica<br>02 Privado de la libertad<br>03 No privado de la libertad | Nueva variable desde el año 2022<br>Su actualización es progresiva por lo que presenta campos sin sin informaciòn |
| TRASTORNOS_ESPECIFICOS | Código trastornos específicos en el aprendizaje escolar y el comportamiento | Numérico | 1 | NO | SI | NO | Público | 1 Trastornos específicos de aprendizaje escolar<br>2 Trastorno por déficit de atención con/sin hiperactividad<br>3 Trastornos específicos de aprendizaje escolar y por déficit de atención<br>9 No Aplica | Nueva variable desde el año 2022<br>Su actualización es progresiva por lo que presenta campos sin sin informaciòn |
| DESCRIP_TRASTORNOS | Trastornos específicos en el aprendizaje escolar y el comportamiento | Cadena | 1 | NO | NO | NO | Público | 1 Trastornos específicos de aprendizaje escolar<br>2 Trastorno por déficit de atención con/sin hiperactividad<br>3 Trastornos específicos de aprendizaje escolar y por déficit de atención<br>9 No Aplica | Nueva variable desde el año 2022<br>Su actualización es progresiva por lo que presenta campos sin sin informaciòn |
| PAIS_ORIGEN | Código país de origen del estudiante | Cadena | 3 | NO | SI | NO | Público | — | La actualización de este campo es progresiva. Los registros sin información son codificados con el código 996 - NO ESPECIFICADO |
| NOMBRE_PAIS | País de origen del estudiante | Cadena | 30 | NO | NO | NO | Público | — | — |
| TIPO_NACIONALIDAD | Código nacionalidad del estudiante | Numérico | 1 | NO | NO | NO | Público | 0, 1 | A partir del año 2023 se modifica la forma de construcción de esta variable tomando unicamente como fuente de información la variable PAIS_ORIGEN |
| DESCRIP_TIPO_NACIONALIDAD | Nacionalidad del estudiante | Cadena | 10 | NO | NO | NO | Público | 0 Colombiano<br>1 Extranjero | A partir del año 2023 se modifica la forma de construcción de esta variable tomando unicamente como fuente de información la variable PAIS_ORIGEN |
| EDAD | Edad del estudiante | Numérico | 2 | NO | NO | SI | Público | Valores mayores a cero | Calculada a 30 de junio de año de vigencia |
| RANGO_EDAD | Código rango de edad | Numérico | 1 | NO | NO | SI | Público | 1, 2,3, 4, 5, 6, 7, 8 | Construida a partir de la EDAD |
| DESCRIP_RANGO_EDAD | Rango de edad | Cadena | 15 | NO | NO | SI | Público | 1 3 a 5 años<br>2 6 a 13 años<br>3 14 a 17 años<br>4 18 a 19 años<br>5 20 a 25 años<br>6 26 a 28 años<br>7 29 a 59 años<br>8 60 años o más | — |
| NIVEL | Código nivel educativo | Numérico | 1 | NO | NO | SI | Público | 1, 2, 3, 4 | Variable construida a partir de COD_GRADO |
| DESCRIP_NIVEL | Nivel Educativo | Cadena | 11 | NO | NO | SI | Público | 1 Preescolar<br>2 Primaria<br>3 Secundaria<br>4 Media | — |
| NIVEL_B | Código Nivel Educativo B | Numérico | 1 | NO | NO | SI | Público | 1, 2, 3, 4, 5, 6 | Variable construida a partir de COD_GRADO |
| DESCRIP_NIVEL_B | Nivel Educativo | Cadena | 30 | NO | NO | SI | Público | 1 Preescolar<br>2 Primaria<br>3 Secundaria<br>4 Media<br>5 Aceleración<br>6 Educación Adultos | — |
| ETNIA_RECODIFICADA | Código grupo étnico | Numérico | 1 | NO | NO | SI | Público | 0, 1, 2, 3, 4, 5, 6 | — |
| DESCRIP_ETNIA_RECODIFICADA | Grupo étnico | Cadena | 18 | NO | NO | SI | Público | 0 No aplica<br>1 Indígenas<br>2 Negritudes<br>3 Rom<br>4 Raizales.<br>5 Afrodescendientes<br>6 Palenqueros | — |
| DIR_CONSECUTIVO | Consecutivo sede | Numérico | 2 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_ORDENDESEDE | Orden sede | Cadena | 1 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_SECTOR | Sector del colegio según Directorio | Numérico | 1 | NO | NO | SI | Público | Oficial<br>No oficial | Información del directorio con fecha de corte 31-03-2024 |
| DIR_ESTADO | Estado de la sede | Cadena | 17 | NO | NO | SI | Público | Antiguo Activo<br>Nuevo Activo<br>Inactivo | Información del directorio con fecha de corte 31-03-2024 |
| DIR_ZONA | Zona sede | Cadena | 18 | NO | NO | SI | Público | EXPANSION<br>RURAL<br>RURAL Y EXPANSION<br>URBANA<br>URBANA Y EXPANSION<br>URBANA Y RURAL | Información del directorio con fecha de corte 31-03-2024 |
| DIR_DIRECCIONGEO | Dirección de la sede | Cadena | 58 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_BARRIOGEO | Barrio donde esta ubicada la sede | Cadena | 44 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_TELEFONO | Teléfono de la sede | Cadena | 62 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_CORREOELECTRONICO | Correo eléctronico de la institución | Cadena | 209 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_WEB | Página Web de la institución | Cadena | 222 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_CODIGOPOSTAL | Código postal de la instición | Cadena | 18 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_CALENDARIO | Calendario de la institución | Cadena | 6 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_GENERO | Género de la institución | Cadena | 9 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_CARAC_MEDIA | Carácter para la media ofrecido por la institución | Cadena | 17 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_ESP_MEDIA | Especialidad para la media ofrecido por la institución | Cadena | 35 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_ENFASIS_MEDIA | Énfasis para el carácter académico de la media | Cadena | 105 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_RECTOR | Nombre de la persona a cargo de la dirección del colegio | Cadena | 53 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_CARGO | Cargo de la persona a cargo de la dirección del colegio | Cadena | 14 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_CHIP | Chip de la Sede | Cadena | 11 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_CPF | Código plantas físicas | Numérico | 6 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_ESTRATO_GEO | Estrato georeferenciado de la Sede | Cadena | 11 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_No_UPZ | Número UPZ de la sede | Cadena | 12 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_NOMBRE_UPZ | Nombre UPZ de la sede | Cadena | 26 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_SECTOR_CENSAL | Sector censal | Cadena | 18 | NO | NO | NO | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_CODIGO_UPL | Número UPL de la sede | Numérico | 20 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_NOMBREUPL | Nombre UPL de la sede | Numérico | 20 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_COORDENADALONGITUDX | Coordenada Longitud de la sede | Numérico | 20 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DIR_COORDENADALATITUDY | Coordenada Latitud de la sede | Numérico | 20 | NO | NO | SI | Público | — | Información del directorio con fecha de corte 31-03-2024 |
| DISCAPACIDAD_AGRUPADA | Con discapacidad | Numérico | 1 | NO | NO | SI | Público | 1 Con alguna discapacidad<br>2 Sin discapacidad | — |
| CAPACIDAD_AGRUPADA | Capacidades excepcionales | Numérico | 1 | NO | NO | SI | Público | 1 Con alguna capacidad excepcional<br>2 Sin capacidad excepcional | — |
| COD_RUV_VICTIMA | Código población victima del conflicto armado (resultado cruce RUV) | Numérico | 1 | NO | SI | NO | Reservado | 1, 2 | Resultado cruce con base de RUV con fecha de corte 1/08/2024 |
| DESCRIP_RUV_VICTIMA | Población victima del conflicto armado (resultado cruce RUV) | Cadena | 23 | NO | NO | NO | Reservado | 1 Víctima del conflicto<br>2 No Aplica | Resultado cruce con base de RUV con fecha de corte 1/08/2024 |
| DESCRIP_RUV_HECHO | Hecho victimizante | Cadena | 99 | NO | NO | NO | Reservado | Acto terrorista / Atentados / Combates / Enfrentamientos / Hostigamientos<br>Acto terrorista / Atentados / Combates / Enfrentamientos / Hostigamientos y otros<br>Amenaza<br>Amenaza y otros<br>Confinamiento<br>Delitos contra la libertad y la integridad sexual en desarrollo del conflicto armado<br>Desaparición forzada<br>Desplazamiento forzado<br>Desplazamiento Forzado y otros<br>Eventos Masivos<br>Homicidio<br>Minas Antipersonal, Munición sin Explotar y Artefacto Explosivo improvisado<br>Perdida de Bienes Muebles o Inmuebles<br>Reclutamiento ilegal de menores<br>Vinculación de Niños Niñas y Adolescentes a Actividades Relacionadas con grupos armados | Resultado cruce con base de RUV con fecha de corte 1/08/2024 |

---

## 4. Fuente

- Archivo fuente: `22IF014_ acceso_permanencia_matricula_2024_0.xlsx`.
- Hojas procesadas: `Pautas de diligenciamiento` y `Diccionario de datos`.