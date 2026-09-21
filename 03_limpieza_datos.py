# Nombres y apellidos: Chinte Ponce, Joseph Alexander
# Codigo de matricula: 2024200494M
# Tema: N.11 - Concentracion y competencia en la banca multiple peruana: indice HHI y C4
# Fecha de extraccion: (19 de setiembre)

"""
Limpia y une los archivos JSON crudos descargados por 01_extraccion_api.py
(BCRPData, cuadro "Indicadores de las empresas bancarias") y construye:

  1. Un panel Entidad x Fecha con 4 variables sustantivas por banco:
     participacion_creditos, crecimiento_creditos, utilidad_acumulada, palanca_global
  2. El indice de Herfindahl-Hirschman (HHI) del mercado de creditos, por mes
  3. La razon de concentracion de los 4 bancos mas grandes (C4), por mes

Estructura real del JSON del BCRP (confirmada por inspeccion directa):
  data["config"]["series"] -> lista de {"name": "... - <Banco>", "dec": "1"}
  data["periods"]          -> lista de {"name": "Ene.2016", "values": ["33.7", ...]}
  El orden de 'values' coincide con el orden de 'series'.

Entrada:  /content/datos_crudos/*.json
Salida:   /content/datos_procesados_2024200494M.csv
"""

import json
import os
import re
import glob
import hashlib
import pandas as pd
from datetime import datetime

CARPETA_CRUDOS = "/content/drive/MyDrive/proyecto_hhi_2024200494M/datos_crudos"
SALIDA_CSV = "/content/drive/MyDrive/proyecto_hhi_2024200494M/datos_procesados_2024200494M.csv"

MESES = {
    "Ene": 1, "Feb": 2, "Mar": 3, "Abr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Ago": 8, "Set": 9, "Sep": 9, "Oct": 10, "Nov": 11, "Dic": 12,
}


def parsear_fecha(nombre_periodo):
    """Convierte 'Ene.2016' en una fecha (primer dia del mes)."""
    mes_abrev, anio = nombre_periodo.split(".")
    return pd.Timestamp(year=int(anio), month=MESES[mes_abrev], day=1)


def extraer_banco(nombre_serie):
    """
    El nombre completo de la serie termina en ' - <Banco>', pero la variable
    'Utilidad acumulada' agrega ademas la unidad, ej. 'Interbank (millones S/)'.
    Por eso, despues de tomar el ultimo segmento, se quita cualquier parentesis
    final para que el nombre del banco sea igual en las 4 variables.
    """
    banco = nombre_serie.split(" - ")[-1].strip()
    banco = re.sub(r"\s*\([^)]*\)\s*$", "", banco).strip()
    return banco


def a_flotante(valor):
    """Convierte a float; si el BCRP marca el dato como no disponible, deja NaN."""
    try:
        return float(valor)
    except (TypeError, ValueError):
        return float("nan")


def cargar_variable(nombre_variable):
    """Une los lotes de una variable en un DataFrame largo: fecha, entidad, valor."""
    rutas = sorted(glob.glob(os.path.join(CARPETA_CRUDOS, f"{nombre_variable}_lote*.json")))
    if not rutas:
        raise FileNotFoundError(f"No se encontraron archivos crudos para '{nombre_variable}'")

    filas = []
    for ruta in rutas:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        bancos = [extraer_banco(s["name"]) for s in data["config"]["series"]]
        for periodo in data["periods"]:
            fecha = parsear_fecha(periodo["name"])
            for banco, valor in zip(bancos, periodo["values"]):
                filas.append({"fecha": fecha, "entidad": banco, nombre_variable: a_flotante(valor)})
    return pd.DataFrame(filas)


def cargar_tasas_sistema():
    """
    Carga TAMN y TIPMN (tasas del sistema, no por banco) y calcula el spread.
    Se une al panel por 'fecha' unicamente, ya que es un dato de mercado.
    """
    rutas = sorted(glob.glob(os.path.join(CARPETA_CRUDOS, "tasas_sistema_lote*.json")))
    filas = []
    for ruta in rutas:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        etiquetas = [s["name"].split(" - ")[-1].strip() for s in data["config"]["series"]]
        for periodo in data["periods"]:
            fecha = parsear_fecha(periodo["name"])
            fila = {"fecha": fecha}
            for etiqueta, valor in zip(etiquetas, periodo["values"]):
                fila[etiqueta] = a_flotante(valor)
            filas.append(fila)
    df_tasas = pd.DataFrame(filas)
    df_tasas["spread_sistema"] = df_tasas["TAMN"] - df_tasas["TIPMN"]
    return df_tasas.rename(columns={"TAMN": "tamn_sistema", "TIPMN": "tipmn_sistema"})


def main():
    print(f"Iniciando limpieza: {datetime.now()}")

    variables = ["participacion_creditos", "crecimiento_creditos", "utilidad_acumulada", "palanca_global"]
    df = None
    for var in variables:
        df_var = cargar_variable(var)
        print(f"  {var}: {len(df_var)} filas cargadas")
        df = df_var if df is None else df.merge(df_var, on=["fecha", "entidad"], how="outer")

    entidades_unicas = sorted(df["entidad"].unique())
    print(f"\nEntidades detectadas ({len(entidades_unicas)}): {entidades_unicas}")
    print("(deben ser 16: los 15 bancos + la fila de control 'Empresas Bancarias')")

    # 'Empresas Bancarias' es la fila de control del BCRP (el sistema completo = 100%)
    chequeo = df[df["entidad"] == "Empresas Bancarias"]
    prom_total = chequeo["participacion_creditos"].mean()
    print(f"\nChequeo de consistencia: promedio de 'Empresas Bancarias' = {prom_total:.2f} (debe ser ~100.0)")
    if abs(prom_total - 100) > 1:
        print("ADVERTENCIA: el total no cuadra cerca de 100. Revisar antes de continuar.")

    # El panel de bancos individuales excluye esa fila de control
    panel = df[df["entidad"] != "Empresas Bancarias"].copy()
    panel = panel.sort_values(["fecha", "entidad"]).reset_index(drop=True)

    # --- HHI y C4 del mercado de creditos, por mes (variables de mercado, no de banco) ---
    panel["hhi_mercado"] = panel.groupby("fecha")["participacion_creditos"].transform(
        lambda cuotas: (cuotas ** 2).sum()
    )
    panel["c4_mercado"] = panel.groupby("fecha")["participacion_creditos"].transform(
        lambda cuotas: cuotas.sort_values(ascending=False).head(4).sum()
    )

    # --- Spread del sistema (TAMN - TIPMN), variable de mercado unida por fecha ---
    df_tasas = cargar_tasas_sistema()
    panel = panel.merge(df_tasas, on="fecha", how="left")

    panel.to_csv(SALIDA_CSV, index=False, encoding="utf-8")
    print(f"\nPanel final guardado en: {SALIDA_CSV}")
    print(f"Filas: {len(panel)}  |  Bancos: {panel['entidad'].nunique()}  |  Meses: {panel['fecha'].nunique()}")
    print(f"Columnas: {list(panel.columns)}")

    ultimo_mes = panel["fecha"].max()
    print(f"\nHHI, C4 y spread del ultimo mes disponible ({ultimo_mes.strftime('%b-%Y')}):")
    print(panel[panel["fecha"] == ultimo_mes][
        ["hhi_mercado", "c4_mercado", "tamn_sistema", "tipmn_sistema", "spread_sistema"]
    ].head(1).to_string(index=False))

    # --- Hash SHA-256 del archivo entregado (numeral 2.4.5 de la consigna) ---
    with open(SALIDA_CSV, "rb") as f:
        hash_sha256 = hashlib.sha256(f.read()).hexdigest()
    print(f"\nHash SHA-256 del archivo procesado (cópialo a tu README.md tal cual):")
    print(hash_sha256)


if __name__ == "__main__":
    main()
