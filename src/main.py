"""Pipeline end-to-end: ejecuta todo, persiste resultados y figuras.

Ejecutar con:  ``python -m src.main``

Pasos:
  1) Resolver NSGA-II y guardar F_pareto en results/pareto_front.csv
  2) Post-selección ponderada y lexicográfica (A Posteriori)
  3) Resolver GA mono-objetivo ponderado y lexicográfico (A Priori)
  4) Persistir las 4 soluciones en results/selected_solutions.json
  5) Calcular métricas (hipervolumen ref=[200,50], spacing, extremos)
  6) Persistir métricas en results/metrics.json
  7) Generar figuras (scatter principal + zoom)
  8) Imprimir tabla resumen en consola (formato numérico mexicano)

Reproducibilidad: seed=1 en ambos minimize() (FASE 1.6 del SuperPrompt).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from pymoo.indicators.hv import HV

from . import apriori, aposteriori, export_latex, visualization

# --- Rutas del proyecto (relativas a la raíz del repo) ---------------------
ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "Figures"

# Punto de referencia para el hipervolumen (peor caso del dominio observado).
HV_REF_POINT = np.array([200.0, 50.0])

SEED = 1


def _spacing(F: np.ndarray) -> float:
    """Métrica de espaciamiento de Schott (uniformidad del frente).

    Para cada solución se toma la distancia (L1) al vecino más cercano del
    frente; el spacing es la desviación estándar de esas distancias. Un valor
    pequeño indica una distribución uniforme.
    """
    n = len(F)
    if n < 2:
        return 0.0
    dists = np.zeros(n)
    for i in range(n):
        otros = np.delete(F, i, axis=0)
        d = np.abs(otros - F[i]).sum(axis=1)  # distancia L1
        dists[i] = d.min()
    d_mean = dists.mean()
    return float(np.sqrt(np.sum((d_mean - dists) ** 2) / (n - 1)))


def _fmt_mx(valor: float) -> str:
    """Formato numérico mexicano: punto decimal, coma de miles."""
    return f"{valor:,.2f}"


def ejecutar_pipeline(seed: int = SEED) -> dict:
    """Corre todo el análisis y persiste resultados. Devuelve un resumen."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # 1-2) A Posteriori: NSGA-II + post-selección
    print("→ Ejecutando NSGA-II (A Posteriori)...")
    post = aposteriori.ejecutar(seed=seed)

    # Guardar frente de Pareto ordenado por f1 (legibilidad del CSV).
    F = post.F_pareto
    orden = np.argsort(F[:, 0])
    df_front = pd.DataFrame(F[orden], columns=["f1_costo", "f2_tiempo"])
    df_front.to_csv(RESULTS_DIR / "pareto_front.csv", index=False)

    # 3) A Priori: GA mono-objetivo
    print("→ Ejecutando GA mono-objetivo (A Priori)...")
    apri = apriori.ejecutar(seed=seed)

    # 4) Persistir las 4 soluciones
    soluciones = {
        "post_ponderada": {
            "estrategia": "A Posteriori — Suma Ponderada",
            "f1_costo": round(float(post.solucion_post_ponderada[0]), 4),
            "f2_tiempo": round(float(post.solucion_post_ponderada[1]), 4),
            "indice_frente": post.idx_ponderada,
        },
        "post_lexico": {
            "estrategia": "A Posteriori — Lexicográfica (prioridad f2)",
            "f1_costo": round(float(post.solucion_post_lexicografica[0]), 4),
            "f2_tiempo": round(float(post.solucion_post_lexicografica[1]), 4),
            "indice_frente": post.idx_lexicografica,
        },
        "apriori_pond": {
            "estrategia": "A Priori — GA Ponderado",
            "f1_costo": round(float(apri.ponderada[0]), 4),
            "f2_tiempo": round(float(apri.ponderada[1]), 4),
            "x": [round(float(v), 4) for v in apri.x_ponderada],
        },
        "apriori_lex": {
            "estrategia": "A Priori — GA Lexicográfico (sólo f2)",
            "f1_costo": round(float(apri.lexicografica[0]), 4),
            "f2_tiempo": round(float(apri.lexicografica[1]), 4),
            "x": [round(float(v), 4) for v in apri.x_lexicografica],
        },
    }
    with open(RESULTS_DIR / "selected_solutions.json", "w", encoding="utf-8") as fh:
        json.dump(soluciones, fh, ensure_ascii=False, indent=2)

    # 5) Métricas del frente
    hv = HV(ref_point=HV_REF_POINT)
    metrics = {
        "seed": seed,
        "n_soluciones_frente": int(len(F)),
        "hipervolumen": round(float(hv(F)), 4),
        "hv_ref_point": HV_REF_POINT.tolist(),
        "spacing": round(_spacing(F), 4),
        "extremos": {
            "min_f1": round(float(F[:, 0].min()), 4),
            "max_f1": round(float(F[:, 0].max()), 4),
            "min_f2": round(float(F[:, 1].min()), 4),
            "max_f2": round(float(F[:, 1].max()), 4),
        },
        "pesos_ponderada": [0.7, 0.3],
        "parametros": {
            "pop_size": 100, "n_gen": 100,
            "algoritmo_aposteriori": "NSGA-II",
            "algoritmo_apriori": "GA",
        },
    }
    with open(RESULTS_DIR / "metrics.json", "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=2)

    # 7) Figuras
    print("→ Generando figuras...")
    png, pdf = visualization.scatter_estrategias(post, apri, FIGURES_DIR)
    zoom = visualization.scatter_zoom(post, apri, FIGURES_DIR)

    # 8b) Exportar macros LaTeX (numbers → reporte, sin hardcodear)
    macros = export_latex.generar()

    # 8) Tabla resumen en consola
    _imprimir_resumen(soluciones, metrics)
    print(f"\n✔ Resultados en: {RESULTS_DIR}")
    print(f"✔ Figuras: {png.name}, {pdf.name}, {zoom.name}")
    print(f"✔ Macros LaTeX: {macros.relative_to(ROOT)}")

    return {"soluciones": soluciones, "metrics": metrics}


def _imprimir_resumen(soluciones: dict, metrics: dict) -> None:
    """Imprime una tabla resumen legible con formato mexicano."""
    print("\n" + "=" * 64)
    print(" RESUMEN — Estrategias de Decisión Multicriterio")
    print("=" * 64)
    fila = "{:<38} {:>11} {:>11}"
    print(fila.format("Estrategia", "f1 (Costo)", "f2 (Tiempo)"))
    print("-" * 64)
    for s in soluciones.values():
        print(fila.format(s["estrategia"][:38], _fmt_mx(s["f1_costo"]), _fmt_mx(s["f2_tiempo"])))
    print("-" * 64)
    print(f" Hipervolumen (ref {metrics['hv_ref_point']}): {_fmt_mx(metrics['hipervolumen'])}")
    print(f" Spacing (uniformidad):                {_fmt_mx(metrics['spacing'])}")
    ext = metrics["extremos"]
    print(f" Extremos frente — f1∈[{_fmt_mx(ext['min_f1'])}, {_fmt_mx(ext['max_f1'])}]"
          f"  f2∈[{_fmt_mx(ext['min_f2'])}, {_fmt_mx(ext['max_f2'])}]")
    print("=" * 64)


if __name__ == "__main__":
    ejecutar_pipeline()
