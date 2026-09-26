# Concentración y competencia en la banca múltiple peruana: índice HHI y C4

**Nombres y apellidos:** Chinte Ponce, Joseph Alexander
**Código de matrícula:** 2024200494M
**Tema:** N.º 11 del Temario — Concentración y competencia en la banca múltiple peruana: índice HHI y C4
**Curso:** Finanzas I (055D) — UNCP, 2026-II — Unidad I
**Fecha de corte de los datos:** (19 de setiembre)

## Objetivo

Medir la concentración del mercado de créditos de la banca múltiple peruana (HHI y C4) y su
relación con el spread del sistema (TAMN − TIPMN), usando datos oficiales del BCRP extraídos
de forma automatizada.

## Fuentes y endpoints

Vía única (API), tal como exige la Unidad I:

- **BCRPData REST** — Banco Central de Reserva del Perú.
  Cuadro base: "Indicadores de las empresas bancarias" (cn-016).
  https://estadisticas.bcrp.gob.pe/estadisticas/series/cuadros/notasemanalmensual/cn-016
  Formato de la API: https://estadisticas.bcrp.gob.pe/estadisticas/series/api/[códigos]/json/[inicio]/[fin]/esp
  Documentación oficial: https://estadisticas.bcrp.gob.pe/estadisticas/series/documentos/bcrpdataapi.pdf
  Series utilizadas: PN07693EM–PN07710EM (participación de créditos), PN07711EM–PN07728EM
  (crecimiento de créditos), PN07765EM–PN07782EM (utilidad acumulada), PN07783EM–PN07800EM
  (palanca global), PN07807NM (TAMN) y PN07816NM (TIPMN). El detalle completo está en
  `diccionario_variables.md`.

No se usa clave ni token: la API de BCRPData es de acceso público (ver `.env.example`).

## Estructura del proyecto

```
proyecto/
├── codigo/
│   ├── 01_extraccion_api.py
│   ├── 03_limpieza_datos.py
│   └── 04_analisis.py
├── datos_crudos/        (JSON tal como salen de la API, sin editar)
├── datos_procesados/    (datos_procesados_2024200494M.csv)
├── salidas/              (tablas .csv y figuras .png)
├── diccionario_variables.md
├── README.md
├── requirements.txt
├── .env.example
└── log_ejecucion.txt
```

Los tres scripts usan rutas relativas (`pathlib`, `Path(__file__).resolve().parent.parent`): se ejecutan desde `codigo/` y ubican `datos_crudos/`, `datos_procesados/` y `salidas/` un nivel arriba, sin rutas absolutas del computador del estudiante.

## Orden de ejecución

1. `codigo/01_extraccion_api.py` — descarga los datos crudos desde BCRPData y los guarda en `datos_crudos/` (formato JSON, sin editar).
2. `codigo/03_limpieza_datos.py` — limpia, tipifica y une las series en un panel Entidad × Fecha; calcula HHI, C4 y spread; genera `datos_procesados/datos_procesados_2024200494M.csv` y su hash SHA-256.
3. `codigo/04_analisis.py` — genera las tablas y figuras de la sección de Resultados del artículo, guardadas en `salidas/`.

No existe un script `02_scraping_web.py` en esta entrega porque, para la Unidad I, la consigna exige solo una vía de extracción automatizada (preferentemente API), y esta es la vía elegida.

## Versión del lenguaje y de las librerías

Ejecutado en Google Colab.
Python: 3.13.15
Librerías (ver `requirements.txt` para versiones exactas): requests, pandas, numpy, matplotlib, openpyxl.

## Hash SHA-256 del archivo procesado

```
9593be9cc176779823d62b944f1eeb7946b4cfcaca83c270d00d24ca357e9204
```

(Corresponde a `datos_procesados_2024200494M.csv`. Si vuelves a correr la extracción en una fecha distinta, el BCRP puede haber revisado algún dato hacia atrás; en ese caso, actualiza este hash con el que imprima tu última ejecución y dejalo anotado junto con la fecha, según el numeral 2.4.5 de la consigna.)

## Reproducibilidad

Los parámetros `FECHA_INICIO = "2016-1"` y `FECHA_CORTE = "2025-12"` están declarados como
constantes fijas en `codigo/01_extraccion_api.py` (no se usan fechas dinámicas). Los datos crudos
(`datos_crudos/`) se conservan tal como salen de la fuente, sin editar.

## Repositorio

Enlace de GitHub: (https://github.com/Joseph-Alexander-Chinte-Ponce/concentracion-banca-peru-hhi)
