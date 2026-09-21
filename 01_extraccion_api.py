# Nombres y apellidos: Chinte Ponce, Joseph Alexander
# Codigo de matricula: 2024200494M
# Tema: N.11 - Concentracion y competencia en la banca multiple peruana: indice HHI y C4
# Fecha de extraccion: (19 de setiembre)

"""
Este script consume la API REST publica del BCRP (BCRPData) para descargar,
por cada uno de los 15 bancos de la banca multiple peruana, cuatro variables
mensuales publicadas por el propio BCRP en el cuadro "Indicadores de las
empresas bancarias" (cn-016):

  1. participacion_creditos  -> cuota de mercado en creditos (%), base del HHI y el C4
  2. crecimiento_creditos    -> tasa de crecimiento mensual de colocaciones (%)
  3. utilidad_acumulada      -> utilidad acumulada del banco (millones de S/)
  4. palanca_global          -> apalancamiento (activos / patrimonio efectivo)

Fuente: Banco Central de Reserva del Peru. (2026). BCRPData - Indicadores de
las empresas bancarias [Base de datos]. Recuperado de
https://estadisticas.bcrp.gob.pe/estadisticas/series/cuadros/notasemanalmensual/cn-016

Formato de la API confirmado en la guia oficial:
https://estadisticas.bcrp.gob.pe/estadisticas/series/documentos/bcrpdataapi.pdf
  https://estadisticas.bcrp.gob.pe/estadisticas/series/api/[codigos]/[formato]/[inicio]/[fin]/[idioma]
  - Maximo 10 codigos por consulta, separados por guion.
  - El periodo mensual se escribe como AAAA-M (ej. 2016-1 para enero de 2016).
"""

import requests
import pandas as pd
import time
import json
import os
from datetime import datetime

# ----------------------------------------------------------------------
# PARAMETROS DE LA EXTRACCION (congelados, numeral 2.4.5 de la consigna:
# no se usan fechas dinamicas tipo "hoy", quedan fijas como constantes)
# ----------------------------------------------------------------------
FECHA_INICIO = "2016-1"    # ajusta si tu panel necesita mas historia
FECHA_CORTE = "2025-12"    # ~120 meses junto con FECHA_INICIO, como exige tu ficha

CARPETA_CRUDOS = "/content/drive/MyDrive/proyecto_hhi_2024200494M/datos_crudos"
CARPETA_LOGS = "/content/drive/MyDrive/proyecto_hhi_2024200494M"
os.makedirs(CARPETA_CRUDOS, exist_ok=True)

# ----------------------------------------------------------------------
# DICCIONARIO DE SERIES: banco -> codigo BCRP, por variable
# Codigos tomados directamente del listado oficial del cuadro cn-016
# ----------------------------------------------------------------------
SERIES = {
    "participacion_creditos": {
        "Credito": "PN07693EM", "Interbank": "PN07694EM", "Citibank": "PN07695EM",
        "Scotiabank": "PN07696EM", "Continental": "PN07697EM", "Comercio": "PN07698EM",
        "Financiero": "PN07699EM", "BanBif": "PN07700EM", "MiBanco": "PN07701EM",
        "GNB": "PN07702EM", "Falabella": "PN07703EM", "Santander": "PN07704EM",
        "Ripley": "PN07705EM", "Azteca": "PN07706EM", "ICBC": "PN07709EM",
        "Total": "PN07710EM",
    },
    "crecimiento_creditos": {
        "Credito": "PN07711EM", "Interbank": "PN07712EM", "Citibank": "PN07713EM",
        "Scotiabank": "PN07714EM", "Continental": "PN07715EM", "Comercio": "PN07716EM",
        "Financiero": "PN07717EM", "BanBif": "PN07718EM", "MiBanco": "PN07719EM",
        "GNB": "PN07720EM", "Falabella": "PN07721EM", "Santander": "PN07722EM",
        "Ripley": "PN07723EM", "Azteca": "PN07724EM", "ICBC": "PN07727EM",
        "Total": "PN07728EM",
    },
    "utilidad_acumulada": {
        "Credito": "PN07765EM", "Interbank": "PN07766EM", "Citibank": "PN07767EM",
        "Scotiabank": "PN07768EM", "Continental": "PN07769EM", "Comercio": "PN07770EM",
        "Financiero": "PN07771EM", "BanBif": "PN07772EM", "MiBanco": "PN07773EM",
        "GNB": "PN07774EM", "Falabella": "PN07775EM", "Santander": "PN07776EM",
        "Ripley": "PN07777EM", "Azteca": "PN07778EM", "ICBC": "PN07781EM",
        "Total": "PN07782EM",
    },
    "palanca_global": {
        "Credito": "PN07783EM", "Interbank": "PN07784EM", "Citibank": "PN07785EM",
        "Scotiabank": "PN07786EM", "Continental": "PN07787EM", "Comercio": "PN07788EM",
        "Financiero": "PN07789EM", "BanBif": "PN07790EM", "MiBanco": "PN07791EM",
        "GNB": "PN07792EM", "Falabella": "PN07793EM", "Santander": "PN07794EM",
        "Ripley": "PN07795EM", "Azteca": "PN07796EM", "ICBC": "PN07799EM",
        "Total": "PN07800EM",
    },
    # Tasas del sistema (agregado, no por banco): permiten calcular el spread
    # que pide el objetivo de investigacion de este tema (concentracion vs. spread).
    # Fuente: BCRPData, "Tasas de interes activas y pasivas promedio de las
    # empresas bancarias en MN (terminos efectivos anuales)".
    "tasas_sistema": {
        "TAMN": "PN07807NM",
        "TIPMN": "PN07816NM",
    },
}

BASE_URL = "https://estadisticas.bcrp.gob.pe/estadisticas/series/api"
USER_AGENT = "UNCP-FinanzasI-055D-2024200494M/1.0 (uso academico, contacto: e_2024200494M@uncp.edu.pe)"


def dividir_en_lotes(codigos, tam=10):
    """La API del BCRP acepta como maximo 10 codigos de serie por consulta."""
    for i in range(0, len(codigos), tam):
        yield codigos[i:i + tam]


def consultar_bcrp(codigos):
    """Consume la API REST del BCRP y devuelve el JSON crudo, con manejo de errores."""
    ruta = "-".join(codigos)
    url = f"{BASE_URL}/{ruta}/json/{FECHA_INICIO}/{FECHA_CORTE}/esp"
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json(), resp.status_code
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Fallo la consulta para {ruta}: {e}")
        return None, None


def procesar_variable(nombre_variable, dic_series, log_lineas):
    """Descarga todas las series de una variable (por banco) y las guarda crudas, sin editar."""
    codigos = list(dic_series.values())
    jsons_de_la_variable = []

    for idx, lote in enumerate(dividir_en_lotes(codigos, 10)):
        data, status = consultar_bcrp(lote)
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if data is None:
            log_lineas.append(f"{marca_tiempo} | {nombre_variable} lote {idx} | ERROR | 0 filas")
            continue

        ruta_json = os.path.join(CARPETA_CRUDOS, f"{nombre_variable}_lote{idx}.json")
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        n_periodos = len(data.get("periods", []))
        jsons_de_la_variable.append(data)
        log_lineas.append(
            f"{marca_tiempo} | {nombre_variable} lote {idx} | HTTP {status} | {n_periodos} periodos | {len(lote)} series"
        )
        print(f"[OK] {nombre_variable} (lote {idx}): HTTP {status}, {n_periodos} periodos, {len(lote)} series")
        time.sleep(1)  # pausa entre solicitudes, buena practica de extraccion

    return jsons_de_la_variable


def main():
    log_lineas = [f"=== Extraccion BCRPData iniciada: {datetime.now()} ==="]
    log_lineas.append(f"Ventana congelada: FECHA_INICIO={FECHA_INICIO}  FECHA_CORTE={FECHA_CORTE}")
    print(log_lineas[0])
    print(log_lineas[1])

    for nombre_variable, dic_series in SERIES.items():
        print(f"\n--- Descargando variable: {nombre_variable} ---")
        procesar_variable(nombre_variable, dic_series, log_lineas)

    log_lineas.append(f"=== Extraccion finalizada: {datetime.now()} ===")
    print("\n" + log_lineas[-1])

    with open(os.path.join(CARPETA_LOGS, "log_ejecucion.txt"), "a", encoding="utf-8") as f:
        f.write("\n".join(log_lineas) + "\n\n")

    print("\nListo. Revisa la carpeta /datos_crudos: debe tener 8 archivos .json")
    print("(2 lotes x 4 variables). El siguiente paso es 03_limpieza_datos.py.")


if __name__ == "__main__":
    main()
