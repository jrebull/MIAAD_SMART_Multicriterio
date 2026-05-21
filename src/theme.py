"""Paleta institucional UACJ — fuente única de verdad para colores y tipografía.

Centralizar el tema garantiza coherencia visual entre las figuras de
matplotlib, el dashboard de Streamlit y la portada del reporte LaTeX.
"""

from __future__ import annotations

# --- Paleta institucional UACJ ---------------------------------------------
UACJ_AZUL = "#003CA6"
UACJ_AMARILLO = "#FFD600"
UACJ_GRIS = "#555559"
UACJ_NEGRO = "#231F20"
UACJ_ORO = "#C8962E"

# Fondo crema del enunciado original (Actividad.html, body background).
FONDO_CREMA = "#FDFFE2"

# --- Asignación semántica para esta práctica -------------------------------
COLORS = {
    "pareto": UACJ_AZUL,        # Frente NSGA-II
    "post_ponderada": UACJ_ORO,        # Estrella oro
    "post_lexico": UACJ_AMARILLO,   # Cuadrado amarillo
    "apriori_pond": "#C81E1E",        # Rojo de contraste
    "apriori_lex": UACJ_NEGRO,       # Negro
}

# Etiquetas legibles para leyendas y tablas (orden de presentación estable).
LABELS = {
    "pareto": "Frente de Pareto (NSGA-II)",
    "post_ponderada": "A Posteriori: Suma Ponderada",
    "post_lexico": "A Posteriori: Lexicográfica",
    "apriori_pond": "A Priori: GA Ponderado",
    "apriori_lex": "A Priori: GA Lexicográfico",
}


def apply_matplotlib_theme() -> None:
    """Aplica la tipografía serif (Palatino) para casar con el LaTeX.

    Se invoca explícitamente desde los módulos de visualización para evitar
    efectos colaterales al importar el tema (p. ej. desde Streamlit).
    """
    import matplotlib as mpl

    mpl.rcParams["font.family"] = "serif"
    mpl.rcParams["font.serif"] = ["Palatino", "Palatino Linotype", "DejaVu Serif"]
    mpl.rcParams["axes.labelsize"] = 12
    mpl.rcParams["axes.titlesize"] = 14
    mpl.rcParams["legend.fontsize"] = 10
    mpl.rcParams["figure.facecolor"] = "white"
    mpl.rcParams["savefig.facecolor"] = "white"


# Compatibilidad: aplicar el tema al importar, como sugiere el SuperPrompt.
apply_matplotlib_theme()
