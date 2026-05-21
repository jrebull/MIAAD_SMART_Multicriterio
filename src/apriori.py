"""Estrategia A Priori: GA mono-objetivo con preferencias inyectadas antes.

El tomador de decisiones expresa sus preferencias *antes* de optimizar,
colapsando el problema bi-objetivo a uno mono-objetivo:

  A) Suma ponderada directa con escalamiento manual (f1/200, f2/50) y pesos
     (0.7, 0.3).
  B) Lexicográfica directa: se optimiza únicamente el objetivo prioritario
     (Tiempo, f2).

Reproduce fielmente la sección 4 de ``Actividad.html``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.core.problem import ElementwiseProblem
from pymoo.optimize import minimize

from .problem import XL, XU, f1_costo, f2_tiempo

POP_SIZE = 100
N_GEN = 100
SEED = 1

# Escalamiento manual del enunciado (denominadores aproximados a los rangos).
ESCALA_F1 = 200.0
ESCALA_F2 = 50.0
PESOS = (0.7, 0.3)


class WeightedSumProblem(ElementwiseProblem):
    """Suma ponderada directa (A Priori), idéntica al enunciado."""

    def __init__(self) -> None:
        super().__init__(n_var=2, n_obj=1, xl=XL, xu=XU)

    def _evaluate(self, x, out, *args, **kwargs):
        f1 = 4 * x[0] ** 2 + 4 * x[1] ** 2
        f2 = (x[0] - 5) ** 2 + (x[1] - 5) ** 2
        out["F"] = PESOS[0] * (f1 / ESCALA_F1) + PESOS[1] * (f2 / ESCALA_F2)


class LexicographicProblem(ElementwiseProblem):
    """Lexicográfica directa (A Priori): sólo minimiza Tiempo (f2)."""

    def __init__(self) -> None:
        super().__init__(n_var=2, n_obj=1, xl=XL, xu=XU)

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = (x[0] - 5) ** 2 + (x[1] - 5) ** 2


@dataclass
class ResultadoAPriori:
    """Soluciones A Priori evaluadas en los objetivos originales (f1, f2)."""

    ponderada: np.ndarray          # (2,): [f1_pond, f2_pond]
    lexicografica: np.ndarray      # (2,): [f1_lex, f2_lex]
    x_ponderada: np.ndarray        # (2,): vector de decisión
    x_lexicografica: np.ndarray    # (2,): vector de decisión


def _resolver(problema: ElementwiseProblem, seed: int) -> np.ndarray:
    """Resuelve un problema mono-objetivo con GA y devuelve la X óptima."""
    res = minimize(problema, GA(pop_size=POP_SIZE), ("n_gen", N_GEN), seed=seed, verbose=False)
    return np.asarray(res.X)


def ejecutar(seed: int = SEED) -> ResultadoAPriori:
    """Pipeline A Priori completo (ponderada + lexicográfica)."""
    x_pond = _resolver(WeightedSumProblem(), seed)
    x_lex = _resolver(LexicographicProblem(), seed)

    ponderada = np.array([f1_costo(x_pond), f2_tiempo(x_pond)])
    lexicografica = np.array([f1_costo(x_lex), f2_tiempo(x_lex)])

    return ResultadoAPriori(
        ponderada=ponderada,
        lexicografica=lexicografica,
        x_ponderada=x_pond,
        x_lexicografica=x_lex,
    )
