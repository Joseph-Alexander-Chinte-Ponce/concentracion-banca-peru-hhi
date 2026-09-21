# Diccionario de variables

**Tema N.º 11:** Concentración y competencia en la banca múltiple peruana: índice HHI y C4
**Estudiante:** Chinte Ponce, Joseph Alexander — Código 2024200494M
**Archivo descrito:** `datos_procesados_2024200494M.csv`

| Variable | Definición | Unidad | Frecuencia | Fuente exacta | Endpoint / URL |
|---|---|---|---|---|---|
| `fecha` | Primer día del mes al que corresponde la observación | Fecha (AAAA-MM-DD) | Mensual | — (derivada del periodo del BCRP) | — |
| `entidad` | Banco de la banca múltiple peruana | Texto (15 categorías) | — | BCRP, cuadro cn-016 | https://estadisticas.bcrp.gob.pe/estadisticas/series/cuadros/notasemanalmensual/cn-016 |
| `participacion_creditos` | Cuota de mercado del banco en el saldo de colocaciones (créditos) del sistema | % | Mensual | BCRP, "Indicadores de las empresas bancarias – Colocaciones – Participación (%)" | Series PN07693EM a PN07710EM (una por banco) |
| `crecimiento_creditos` | Tasa de crecimiento mensual de las colocaciones del banco | % mensual | Mensual | BCRP, "Indicadores de las empresas bancarias – Colocaciones – Tasa de crecimiento (%)" | Series PN07711EM a PN07728EM |
| `utilidad_acumulada` | Utilidad acumulada en el año del banco | Millones de S/ | Mensual | BCRP, "Indicadores de las empresas bancarias – Utilidad acumulada" | Series PN07765EM a PN07782EM |
| `palanca_global` | Apalancamiento del banco (activos / patrimonio efectivo) | Veces | Mensual | BCRP, "Indicadores de las empresas bancarias – Palanca global" | Series PN07783EM a PN07800EM |
| `hhi_mercado` | Índice de Herfindahl-Hirschman del mercado de créditos: suma de las cuotas de mercado (participacion_creditos) al cuadrado, de los 15 bancos, en ese mes | Índice (0–10 000) | Mensual (dato de mercado, igual para los 15 bancos en un mismo mes) | Cálculo propio a partir de `participacion_creditos` | — |
| `c4_mercado` | Razón de concentración de los 4 bancos más grandes: suma de las 4 cuotas de mercado más altas del mes | % | Mensual (dato de mercado) | Cálculo propio a partir de `participacion_creditos` | — |
| `tamn_sistema` | Tasa Activa Promedio del sistema en Moneda Nacional | % anual (términos efectivos) | Mensual (dato de mercado) | BCRP, "Tasas de interés activas y pasivas promedio de las empresas bancarias en MN" | Serie PN07807NM |
| `tipmn_sistema` | Tasa Pasiva Promedio del sistema en Moneda Nacional | % anual (términos efectivos) | Mensual (dato de mercado) | BCRP, ídem anterior | Serie PN07816NM |
| `spread_sistema` | Diferencia entre la tasa activa y la tasa pasiva del sistema (tamn_sistema − tipmn_sistema) | Puntos porcentuales | Mensual (dato de mercado) | Cálculo propio | — |

**Ventana de extracción:** enero de 2016 a diciembre de 2025 (120 meses), congelada como constantes `FECHA_INICIO` y `FECHA_CORTE` en `01_extraccion_api.py`.

**Fecha de corte de la extracción:** (completar con la fecha real en que corriste el script por última vez).

**Nota sobre `hhi_mercado`, `c4_mercado`, `tamn_sistema`, `tipmn_sistema` y `spread_sistema`:** son variables de mercado (una por mes), no específicas de cada banco. Por eso su valor se repite en las 15 filas de un mismo mes dentro del panel — es el mismo indicador aplicándose a todo el sistema, no un error de los datos.
