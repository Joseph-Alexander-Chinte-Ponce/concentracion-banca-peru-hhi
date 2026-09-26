# Nombres y apellidos: Chinte Ponce, Joseph Alexander
# Codigo de matricula: 2024200494M
# Tema: N.11 - Concentracion y competencia en la banca multiple peruana: indice HHI y C4
# Fecha de extraccion: (19 de setiembre)

"""
Genera, a partir de datos_procesados_2024200494M.csv, las tablas y figuras
para la seccion de Resultados del articulo:

  Tabla 1  -> ranking de bancos por cuota de mercado promedio en creditos
  Tabla 2  -> matriz de correlaciones entre HHI, C4, spread, TAMN y TIPMN
  Figura 1 -> evolucion mensual del HHI y del C4 (2016-2025)
  Figura 2 -> relacion entre concentracion (HHI) y spread del sistema

Entrada:  <proyecto>/datos_procesados/datos_procesados_2024200494M.csv
Salidas:  <proyecto>/salidas/  (tablas .csv y figuras .png)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

CODIGO_MATRICULA = "2024200494M"

# Rutas relativas a la raiz del proyecto (numeral 2.4.4 de la consigna).
# Este script vive en <proyecto>/codigo/, por eso BASE_DIR sube un nivel.
BASE_DIR = Path(__file__).resolve().parent.parent
ENTRADA_CSV = BASE_DIR / "datos_procesados" / f"datos_procesados_{CODIGO_MATRICULA}.csv"
CARPETA_SALIDAS = BASE_DIR / "salidas"
CARPETA_SALIDAS.mkdir(parents=True, exist_ok=True)


def cargar_panel():
    df = pd.read_csv(ENTRADA_CSV, parse_dates=["fecha"])
    return df


def tabla1_ranking_bancos(panel):
    """Ranking de bancos por cuota de mercado promedio en creditos, 2016-2025."""
    ranking = (
        panel.groupby("entidad")["participacion_creditos"]
        .mean()
        .sort_values(ascending=False)
        .round(2)
        .reset_index()
        .rename(columns={"participacion_creditos": "cuota_promedio_pct"})
    )
    ranking.insert(0, "posicion", range(1, len(ranking) + 1))
    ruta = CARPETA_SALIDAS / "tabla1_ranking_bancos.csv"
    ranking.to_csv(ruta, index=False, encoding="utf-8")
    print(f"[Tabla 1] guardada en {ruta}")
    print(ranking.to_string(index=False))
    return ranking


def tabla2_correlaciones(panel):
    """Matriz de correlaciones entre las variables de mercado (una fila por mes)."""
    mercado = panel.drop_duplicates(subset="fecha")[
        ["hhi_mercado", "c4_mercado", "spread_sistema", "tamn_sistema", "tipmn_sistema"]
    ]
    corr = mercado.corr(method="pearson").round(3)
    ruta = CARPETA_SALIDAS / "tabla2_correlaciones.csv"
    corr.to_csv(ruta, encoding="utf-8")
    print(f"\n[Tabla 2] guardada en {ruta}")
    print(corr.to_string())
    return corr


def figura1_evolucion_hhi_c4(panel):
    """Evolucion mensual del HHI y del C4 (una observacion por mes)."""
    serie = panel.drop_duplicates(subset="fecha").sort_values("fecha")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    ax1.plot(serie["fecha"], serie["hhi_mercado"], color="#1f77b4")
    ax1.set_ylabel("HHI")
    ax1.set_title("Evolucion del indice HHI en el mercado de creditos (2016-2025)")
    ax1.axhline(1500, color="gray", linestyle="--", linewidth=0.8)
    ax1.axhline(2500, color="gray", linestyle="--", linewidth=0.8)

    ax2.plot(serie["fecha"], serie["c4_mercado"], color="#d62728")
    ax2.set_ylabel("C4 (%)")
    ax2.set_xlabel("Fecha")
    ax2.set_title("Evolucion del C4 (cuota de los 4 bancos mas grandes)")

    fig.tight_layout()
    ruta = CARPETA_SALIDAS / "figura1_evolucion_hhi_c4.png"
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    print(f"\n[Figura 1] guardada en {ruta}")


def figura2_hhi_vs_spread(panel):
    """Dispersion entre concentracion (HHI) y spread del sistema, con linea de tendencia."""
    serie = panel.drop_duplicates(subset="fecha").dropna(subset=["hhi_mercado", "spread_sistema"])

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(serie["hhi_mercado"], serie["spread_sistema"], alpha=0.6, color="#2ca02c")

    coef = serie["hhi_mercado"].corr(serie["spread_sistema"])
    pendiente, intercepto = np.polyfit(serie["hhi_mercado"], serie["spread_sistema"], 1)
    x_linea = np.array([serie["hhi_mercado"].min(), serie["hhi_mercado"].max()])
    ax.plot(x_linea, pendiente * x_linea + intercepto, color="black", linewidth=1)

    ax.set_xlabel("HHI (concentracion)")
    ax.set_ylabel("Spread del sistema (TAMN - TIPMN, p.p.)")
    ax.set_title(f"Concentracion vs. spread (correlacion de Pearson = {coef:.3f})")
    fig.tight_layout()

    ruta = CARPETA_SALIDAS / "figura2_hhi_vs_spread.png"
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    print(f"\n[Figura 2] guardada en {ruta}")
    print(f"Correlacion de Pearson entre HHI y spread: {coef:.3f}")


def main():
    panel = cargar_panel()
    print(f"Panel cargado: {len(panel)} filas, {panel['entidad'].nunique()} bancos, "
          f"{panel['fecha'].nunique()} meses\n")

    tabla1_ranking_bancos(panel)
    tabla2_correlaciones(panel)
    figura1_evolucion_hhi_c4(panel)
    figura2_hhi_vs_spread(panel)

    print(f"\nListo. Revisa la carpeta {CARPETA_SALIDAS}: deben existir 2 tablas .csv y 2 figuras .png")


if __name__ == "__main__":
    main()
