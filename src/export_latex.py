"""Genera un archivo de macros LaTeX a partir de los resultados persistidos.

Esto garantiza la regla de oro del reporte: NINGÚN número se teclea a mano en
los ``.tex``; todos provienen de ``results/selected_solutions.json`` y
``results/metrics.json``. El archivo generado se incluye con \\input en
``LaTeX/main.tex`` y se consume vía ``\\num{}`` (siunitx).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
LATEX_DIR = ROOT / "LaTeX"


def _macro(nombre: str, valor) -> str:
    """Define una macro LaTeX sin argumentos."""
    return f"\\newcommand{{\\{nombre}}}{{{valor}}}\n"


def generar(results_dir: Path = RESULTS_DIR, latex_dir: Path = LATEX_DIR) -> Path:
    """Lee los JSON de results/ y escribe LaTeX/valores_generados.tex."""
    with open(results_dir / "selected_solutions.json", encoding="utf-8") as fh:
        sol = json.load(fh)
    with open(results_dir / "metrics.json", encoding="utf-8") as fh:
        met = json.load(fh)

    pp, pl = sol["post_ponderada"], sol["post_lexico"]
    ap, al = sol["apriori_pond"], sol["apriori_lex"]
    ext = met["extremos"]

    # Diferencias absolutas para el análisis de la suma ponderada.
    diff_costo = abs(ap["f1_costo"] - pp["f1_costo"])
    diff_tiempo = abs(ap["f2_tiempo"] - pp["f2_tiempo"])

    latex_dir.mkdir(parents=True, exist_ok=True)
    out = latex_dir / "valores_generados.tex"

    lineas = [
        "% === ARCHIVO GENERADO AUTOMÁTICAMENTE por src/export_latex.py ===\n",
        "% No editar a mano. Regenerar con: python -m src.main\n\n",
        _macro("PostPondCosto", pp["f1_costo"]),
        _macro("PostPondTiempo", pp["f2_tiempo"]),
        _macro("PostLexCosto", pl["f1_costo"]),
        _macro("PostLexTiempo", pl["f2_tiempo"]),
        _macro("AprioriPondCosto", ap["f1_costo"]),
        _macro("AprioriPondTiempo", ap["f2_tiempo"]),
        _macro("AprioriPondVarUno", ap["x"][0]),
        _macro("AprioriPondVarDos", ap["x"][1]),
        _macro("AprioriLexCosto", al["f1_costo"]),
        _macro("AprioriLexTiempo", al["f2_tiempo"]),
        _macro("AprioriLexVarUno", al["x"][0]),
        _macro("AprioriLexVarDos", al["x"][1]),
        _macro("DiffPondCosto", round(diff_costo, 4)),
        _macro("DiffPondTiempo", round(diff_tiempo, 4)),
        _macro("MetHipervolumen", met["hipervolumen"]),
        _macro("MetSpacing", met["spacing"]),
        _macro("MetNSol", met["n_soluciones_frente"]),
        _macro("MetMinFuno", ext["min_f1"]),
        _macro("MetMaxFuno", ext["max_f1"]),
        _macro("MetMinFdos", ext["min_f2"]),
        _macro("MetMaxFdos", ext["max_f2"]),
        _macro("MetSeed", met["seed"]),
    ]
    out.write_text("".join(lineas), encoding="utf-8")
    return out


if __name__ == "__main__":
    ruta = generar()
    print(f"✔ Macros LaTeX generadas en: {ruta}")
