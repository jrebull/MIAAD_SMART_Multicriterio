"""Generación del scatter plot principal y del zoom al codo del frente.

Toda la estética (colores, marcadores, tipografía) proviene de ``theme.py``
para mantener una única fuente de verdad visual. Las figuras se exportan en
PNG (300 dpi) y PDF (vectorial) para uso en el reporte LaTeX.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from . import theme
from .aposteriori import ResultadoAPosteriori
from .apriori import ResultadoAPriori

theme.apply_matplotlib_theme()

# Estilos de marcador por estrategia (marker, size).
_MARKERS = {
    "post_ponderada": ("*", 220),
    "post_lexico": ("s", 130),
    "apriori_pond": ("X", 180),
    "apriori_lex": ("P", 180),
}


def _dibujar_puntos(ax, post: ResultadoAPosteriori, apri: ResultadoAPriori) -> None:
    """Dibuja el frente y las 4 soluciones seleccionadas sobre un eje."""
    F = post.F_pareto
    ax.scatter(
        F[:, 0], F[:, 1], s=30, facecolors="none",
        edgecolors=theme.COLORS["pareto"], linewidths=1.1,
        label=theme.LABELS["pareto"], zorder=2,
    )

    puntos = {
        "post_ponderada": post.solucion_post_ponderada,
        "post_lexico": post.solucion_post_lexicografica,
        "apriori_pond": apri.ponderada,
        "apriori_lex": apri.lexicografica,
    }
    for key, p in puntos.items():
        marker, size = _MARKERS[key]
        ax.scatter(
            p[0], p[1], marker=marker, s=size, color=theme.COLORS[key],
            edgecolors=theme.UACJ_NEGRO, linewidths=0.8,
            label=theme.LABELS[key], zorder=3,
        )


def scatter_estrategias(
    post: ResultadoAPosteriori,
    apri: ResultadoAPriori,
    figures_dir: Path,
) -> tuple[Path, Path]:
    """Figura principal del reporte. Devuelve (ruta_png, ruta_pdf)."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))

    _dibujar_puntos(ax, post, apri)

    # Anotaciones de los dos extremos del frente.
    F = post.F_pareto
    idx_min_f1 = int(np.argmin(F[:, 0]))
    idx_min_f2 = int(np.argmin(F[:, 1]))
    ax.annotate(
        "Extremo mín. $f_1$\n(menor costo)",
        xy=(F[idx_min_f1, 0], F[idx_min_f1, 1]),
        xytext=(F[idx_min_f1, 0] + 28, F[idx_min_f1, 1] - 9),
        fontsize=9, color=theme.UACJ_GRIS,
        arrowprops=dict(arrowstyle="->", color=theme.UACJ_GRIS, lw=0.8),
    )
    ax.annotate(
        "Extremo mín. $f_2$\n(menor tiempo)",
        xy=(F[idx_min_f2, 0], F[idx_min_f2, 1]),
        xytext=(F[idx_min_f2, 0] - 70, F[idx_min_f2, 1] + 6),
        fontsize=9, color=theme.UACJ_GRIS,
        arrowprops=dict(arrowstyle="->", color=theme.UACJ_GRIS, lw=0.8),
    )

    ax.set_title("Comparativa de Estrategias de Decisión Multicriterio")
    ax.set_xlabel("f₁: Costo Operativo (Minimizar)")
    ax.set_ylabel("f₂: Tiempo de Entrega (Minimizar)")
    ax.grid(True, linestyle="--", alpha=0.6)

    legend = ax.legend(loc="best", frameon=True, framealpha=0.85)
    legend.get_frame().set_facecolor(theme.FONDO_CREMA)
    legend.get_frame().set_edgecolor(theme.UACJ_GRIS)

    fig.tight_layout()
    png_path = figures_dir / "scatter_estrategias.png"
    pdf_path = figures_dir / "scatter_estrategias.pdf"
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    # metadata sin fecha → PDF reproducible bit-a-bit entre corridas.
    fig.savefig(pdf_path, bbox_inches="tight", metadata={"CreationDate": None})
    plt.close(fig)
    return png_path, pdf_path


def scatter_zoom(
    post: ResultadoAPosteriori,
    apri: ResultadoAPriori,
    figures_dir: Path,
) -> Path:
    """Zoom al codo del frente (zona de las soluciones lexicográficas)."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 6))

    _dibujar_puntos(ax, post, apri)

    # Ventana centrada en el extremo de menor f2 (donde caen las lexicográficas).
    F = post.F_pareto
    f1_lex = post.solucion_post_lexicografica[0]
    x_max = max(f1_lex, apri.lexicografica[0]) * 1.10 + 10
    y_max = max(post.solucion_post_lexicografica[1], apri.lexicografica[1]) + 8
    ax.set_xlim(F[:, 0].min() - 5, x_max)
    ax.set_ylim(-1, y_max)

    ax.set_title("Zoom al codo del frente: análisis lexicográfico")
    ax.set_xlabel("f₁: Costo Operativo (Minimizar)")
    ax.set_ylabel("f₂: Tiempo de Entrega (Minimizar)")
    ax.grid(True, linestyle="--", alpha=0.6)
    legend = ax.legend(loc="best", frameon=True, framealpha=0.85)
    legend.get_frame().set_facecolor(theme.FONDO_CREMA)

    fig.tight_layout()
    zoom_path = figures_dir / "pareto_front_zoom.png"
    fig.savefig(zoom_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return zoom_path
