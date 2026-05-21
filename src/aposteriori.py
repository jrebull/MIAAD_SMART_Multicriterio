"""Estrategia A Posteriori: NSGA-II + post-selección sobre el frente.

Primero se aproxima TODO el frente de Pareto con NSGA-II y, sólo después, el
tomador de decisiones elige sobre el conjunto no dominado mediante:

  A) Suma ponderada normalizada (pesos 0.7 costo / 0.3 tiempo).
  B) Criterio lexicográfico (prioridad 1: tiempo f2; prioridad 2: costo f1).

Reproduce fielmente la sección 3 de ``Actividad.html``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize

from .problem import RoutingProxyProblem

# Parámetros del enunciado.
POP_SIZE = 100
N_GEN = 100
SEED = 1
PESOS = np.array([0.7, 0.3])  # 70% Costo, 30% Tiempo


@dataclass
class ResultadoAPosteriori:
    """Frente de Pareto y las dos soluciones post-seleccionadas."""

    F_pareto: np.ndarray                 # (N, 2): [f1, f2] del frente
    solucion_post_ponderada: np.ndarray  # (2,)
    solucion_post_lexicografica: np.ndarray  # (2,)
    idx_ponderada: int
    idx_lexicografica: int


def resolver_nsga2(seed: int = SEED) -> np.ndarray:
    """Ejecuta NSGA-II y devuelve los valores objetivo del frente (F)."""
    algorithm = NSGA2(pop_size=POP_SIZE)
    res = minimize(
        RoutingProxyProblem(),
        algorithm,
        ("n_gen", N_GEN),
        seed=seed,
        verbose=False,
    )
    return np.asarray(res.F)


def seleccionar_ponderada(F_pareto: np.ndarray, pesos: np.ndarray = PESOS) -> int:
    """Índice de la mejor solución por suma ponderada normalizada del frente."""
    rango = F_pareto.max(axis=0) - F_pareto.min(axis=0)
    # Evita división por cero si un objetivo fuera constante en el frente.
    rango = np.where(rango == 0, 1.0, rango)
    F_norm = (F_pareto - F_pareto.min(axis=0)) / rango
    valores_ponderados = np.sum(F_norm * pesos, axis=1)
    return int(np.argmin(valores_ponderados))


def seleccionar_lexicografica(F_pareto: np.ndarray) -> int:
    """Índice de la solución con menor f2 (prioridad: Tiempo de Entrega)."""
    return int(np.argsort(F_pareto[:, 1])[0])


def ejecutar(seed: int = SEED) -> ResultadoAPosteriori:
    """Pipeline A Posteriori completo."""
    F_pareto = resolver_nsga2(seed=seed)
    idx_pond = seleccionar_ponderada(F_pareto)
    idx_lex = seleccionar_lexicografica(F_pareto)
    return ResultadoAPosteriori(
        F_pareto=F_pareto,
        solucion_post_ponderada=F_pareto[idx_pond],
        solucion_post_lexicografica=F_pareto[idx_lex],
        idx_ponderada=idx_pond,
        idx_lexicografica=idx_lex,
    )
