"""Definición del problema bi-objetivo y de las funciones objetivo originales.

Reproduce fielmente el enunciado de ``Actividad.html`` (sección 2):

    f1 = 4 * x0^2 + 4 * x1^2          (Costo Operativo)
    f2 = (x0 - 5)^2 + (x1 - 5)^2      (Tiempo de Entrega)

con dominio x in [0, 5]^2. No se altera la matemática del enunciado.
"""

from __future__ import annotations

import numpy as np
from pymoo.core.problem import ElementwiseProblem

# Dominio de decisión (idéntico al enunciado).
XL = np.array([0.0, 0.0])
XU = np.array([5.0, 5.0])


def f1_costo(x: np.ndarray) -> float:
    """Costo Operativo: f1 = 4*x0^2 + 4*x1^2."""
    return float(4.0 * x[0] ** 2 + 4.0 * x[1] ** 2)


def f2_tiempo(x: np.ndarray) -> float:
    """Tiempo de Entrega: f2 = (x0-5)^2 + (x1-5)^2."""
    return float((x[0] - 5.0) ** 2 + (x[1] - 5.0) ** 2)


class RoutingProxyProblem(ElementwiseProblem):
    """Proxy continuo Costo (f1) vs Tiempo (f2). Idéntico al enunciado."""

    def __init__(self) -> None:
        super().__init__(n_var=2, n_obj=2, xl=XL, xu=XU)

    def _evaluate(self, x, out, *args, **kwargs):
        out["F"] = [f1_costo(x), f2_tiempo(x)]
