"""Construye notebooks/01_analisis_multicriterio.ipynb con nbformat.

Genera el notebook de forma reproducible (en vez de teclear JSON a mano) y se
ejecuta después con nbconvert para poblar las salidas. Importa la lógica desde
src/ sin duplicarla.
"""

from pathlib import Path

import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []


def md(text: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text: str) -> None:
    cells.append(nbf.v4.new_code_cell(text))


md(
    "# Análisis Comparativo de Estrategias de Decisión Multicriterio\n"
    "## A Priori (GA) vs. A Posteriori (NSGA-II)\n\n"
    "**MIAAD — Optimización Inteligente · UACJ**  \n"
    "Javier Augusto Rebull Saucedo (263483)\n\n"
    "Este notebook importa la lógica desde `src/` (sin duplicarla), muestra las "
    "cuatro soluciones, la gráfica comparativa y responde las cuatro preguntas "
    "del enunciado. Semilla fija (`seed=1`) para reproducibilidad."
)

code(
    "import sys, os, json\n"
    "from pathlib import Path\n"
    "# Permitir importar el paquete src/ desde la raíz del repo\n"
    "ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n"
    "sys.path.insert(0, str(ROOT))\n"
    "import pandas as pd\n"
    "from src import aposteriori, apriori, visualization\n"
    "print('Raíz del proyecto:', ROOT)"
)

md(
    "## 1. Ejecución de ambas estrategias\n"
    "Resolvemos el frente de Pareto con NSGA-II y aplicamos las post-selecciones "
    "(A Posteriori), y resolvemos el GA mono-objetivo con preferencias inyectadas "
    "(A Priori)."
)

code(
    "post = aposteriori.ejecutar(seed=1)\n"
    "apri = apriori.ejecutar(seed=1)\n"
    "print(f'Frente de Pareto: {len(post.F_pareto)} soluciones no dominadas')"
)

md("## 2. Las cuatro soluciones seleccionadas")

code(
    "tabla = pd.DataFrame([\n"
    "    ['A Posteriori', 'Suma Ponderada', *post.solucion_post_ponderada],\n"
    "    ['A Posteriori', 'Lexicográfica', *post.solucion_post_lexicografica],\n"
    "    ['A Priori', 'GA Ponderado', *apri.ponderada],\n"
    "    ['A Priori', 'GA Lexicográfico', *apri.lexicografica],\n"
    "], columns=['Enfoque', 'Criterio', 'f1 (Costo)', 'f2 (Tiempo)'])\n"
    "tabla = tabla.round(2)\n"
    "tabla"
)

md(
    "## 3. Visualización conjunta\n"
    "Frente de Pareto (NSGA-II) y las cuatro decisiones. Las soluciones "
    "*ponderadas* caen en el codo del frente; las *lexicográficas* en el extremo "
    "de menor tiempo."
)

code(
    "import matplotlib.pyplot as plt\n"
    "from src import theme\n"
    "fig, ax = plt.subplots(figsize=(10, 6))\n"
    "F = post.F_pareto\n"
    "ax.scatter(F[:,0], F[:,1], s=30, facecolors='none', edgecolors=theme.COLORS['pareto'], label=theme.LABELS['pareto'])\n"
    "ax.scatter(*post.solucion_post_ponderada, marker='*', s=220, color=theme.COLORS['post_ponderada'], edgecolors='k', label=theme.LABELS['post_ponderada'])\n"
    "ax.scatter(*post.solucion_post_lexicografica, marker='s', s=130, color=theme.COLORS['post_lexico'], edgecolors='k', label=theme.LABELS['post_lexico'])\n"
    "ax.scatter(*apri.ponderada, marker='X', s=180, color=theme.COLORS['apriori_pond'], edgecolors='k', label=theme.LABELS['apriori_pond'])\n"
    "ax.scatter(*apri.lexicografica, marker='P', s=180, color=theme.COLORS['apriori_lex'], edgecolors='k', label=theme.LABELS['apriori_lex'])\n"
    "ax.set_title('Comparativa de Estrategias de Decisión Multicriterio')\n"
    "ax.set_xlabel('f1: Costo Operativo (Minimizar)'); ax.set_ylabel('f2: Tiempo de Entrega (Minimizar)')\n"
    "ax.grid(True, linestyle='--', alpha=0.6); ax.legend(loc='best')\n"
    "plt.show()"
)

md(
    "## 4. Respuestas a las cuatro preguntas del enunciado\n\n"
    "- [x] **P1 — Gráfica con leyenda visible:** mostrada arriba.\n"
    "- [x] **P2 — Suma ponderada (a priori vs a posteriori):** las soluciones "
    "son muy cercanas (diferencia de pocas unidades). Coinciden porque el frente "
    "es **convexo**: cualquier minimización de la combinación lineal converge al "
    "mismo punto. Difieren levemente por el escalamiento manual ($f_1/200$, "
    "$f_2/50$) frente a la normalización por extremos del frente.\n"
    "- [x] **P3 — Lexicográfica:** al minimizar sólo $f_2$ la solución va a "
    "$(5,5)$, donde $f_1$ alcanza su **máximo** (200). Coincide con el extremo de "
    "menor tiempo del frente NSGA-II.\n"
    "- [x] **P4 — Conclusión profesional:** usar NSGA-II en decisiones "
    "estratégicas únicas con múltiples *stakeholders* y sin pesos consensuados; "
    "usar A Priori en decisiones operativas recurrentes con pesos estables."
)

code(
    "# Verificación numérica (FASE 5): el frente toca los extremos teóricos\n"
    "assert abs(F[:,0].min() - 0)   < 1e-2, 'min f1 debe ser ~0'\n"
    "assert abs(F[:,1].min() - 0)   < 1e-2, 'min f2 debe ser ~0'\n"
    "assert abs(apri.lexicografica[0] - 200) < 1.0, 'lex A Priori f1 debe ser ~200'\n"
    "print('✔ Validación numérica superada: extremos y lexicográfica correctos.')"
)

nb["cells"] = cells
nb["metadata"]["kernelspec"] = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}

out = Path(__file__).resolve().parent / "01_analisis_multicriterio.ipynb"
nbf.write(nb, out)
print(f"✔ Notebook escrito en: {out}")
