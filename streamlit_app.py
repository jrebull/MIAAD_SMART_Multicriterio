"""Dashboard interactivo — Estrategias de Decisión Multicriterio (MIAAD/UACJ).

Ejecutar con:  streamlit run streamlit_app.py

Permite explorar cómo cambia la decisión A Posteriori al mover los pesos
(suma ponderada) y al cambiar la prioridad lexicográfica, todo sobre el mismo
frente de Pareto aproximado por NSGA-II. Reutiliza la lógica de src/.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Hacer importable el paquete src/ sin depender del cwd ni del lanzador.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import aposteriori, apriori, theme

st.set_page_config(page_title="Decisión Multicriterio — UACJ", layout="wide")


@st.cache_data(show_spinner="Calculando frente de Pareto (NSGA-II)…")
def cargar_datos(seed: int = 1):
    """Calcula una sola vez el frente NSGA-II y las soluciones A Priori."""
    post = aposteriori.ejecutar(seed=seed)
    apri = apriori.ejecutar(seed=seed)
    return post.F_pareto, apri.ponderada, apri.lexicografica


def seleccion_ponderada(F: np.ndarray, w1: float) -> int:
    """Re-selecciona sobre el frente con pesos (w1, 1-w1)."""
    pesos = np.array([w1, 1.0 - w1])
    rango = F.max(axis=0) - F.min(axis=0)
    rango = np.where(rango == 0, 1.0, rango)
    F_norm = (F - F.min(axis=0)) / rango
    return int(np.argmin(np.sum(F_norm * pesos, axis=1)))


def seleccion_lexicografica(F: np.ndarray, prioridad: str) -> int:
    """Índice del extremo según la prioridad lexicográfica elegida."""
    col = 1 if prioridad.startswith("f₂") else 0
    return int(np.argsort(F[:, col])[0])


# ------------------------------------------------------------------ UI ------
st.title("Estrategias de Decisión Multicriterio · A Priori vs A Posteriori")
st.caption("MIAAD — Optimización Inteligente · UACJ · Javier Rebull (263483)")

F, apri_pond, apri_lex = cargar_datos()

with st.sidebar:
    st.header("Preferencias del decisor")
    st.subheader("Suma ponderada")
    w1 = st.slider("Peso del Costo (f₁)", 0.0, 1.0, 0.7, 0.05)
    st.write(f"Peso del Tiempo (f₂): **{1 - w1:.2f}**")
    st.divider()
    st.subheader("Criterio lexicográfico")
    prioridad = st.radio(
        "Objetivo prioritario",
        ["f₂ (Tiempo) primero", "f₁ (Costo) primero"],
        index=0,
    )

idx_pond = seleccion_ponderada(F, w1)
idx_lex = seleccion_lexicografica(F, prioridad)
post_pond = F[idx_pond]
post_lex = F[idx_lex]

# --- Métricas -------------------------------------------------------------
st.subheader("Soluciones seleccionadas")
c1, c2, c3, c4 = st.columns(4)
c1.metric("A Posteriori · Ponderada — Costo", f"{post_pond[0]:,.2f}", f"Tiempo {post_pond[1]:,.2f}")
c2.metric("A Posteriori · Lexicográfica — Costo", f"{post_lex[0]:,.2f}", f"Tiempo {post_lex[1]:,.2f}")
c3.metric("A Priori · GA Ponderado — Costo", f"{apri_pond[0]:,.2f}", f"Tiempo {apri_pond[1]:,.2f}")
c4.metric("A Priori · GA Lexicográfico — Costo", f"{apri_lex[0]:,.2f}", f"Tiempo {apri_lex[1]:,.2f}")

# --- Scatter interactivo --------------------------------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=F[:, 0], y=F[:, 1], mode="markers", name="Frente de Pareto (NSGA-II)",
    marker=dict(size=7, color=theme.UACJ_AZUL, symbol="circle-open"),
))
fig.add_trace(go.Scatter(
    x=[post_pond[0]], y=[post_pond[1]], mode="markers", name="A Posteriori: Ponderada",
    marker=dict(size=20, color=theme.UACJ_ORO, symbol="star", line=dict(width=1, color="black")),
))
fig.add_trace(go.Scatter(
    x=[post_lex[0]], y=[post_lex[1]], mode="markers", name="A Posteriori: Lexicográfica",
    marker=dict(size=16, color=theme.UACJ_AMARILLO, symbol="square", line=dict(width=1, color="black")),
))
fig.add_trace(go.Scatter(
    x=[apri_pond[0]], y=[apri_pond[1]], mode="markers", name="A Priori: GA Ponderado",
    marker=dict(size=15, color=theme.COLORS["apriori_pond"], symbol="x", line=dict(width=1, color="black")),
))
fig.add_trace(go.Scatter(
    x=[apri_lex[0]], y=[apri_lex[1]], mode="markers", name="A Priori: GA Lexicográfico",
    marker=dict(size=15, color=theme.UACJ_NEGRO, symbol="cross", line=dict(width=1, color="white")),
))
fig.update_layout(
    title="Comparativa de Estrategias de Decisión Multicriterio",
    xaxis_title="f₁: Costo Operativo (Minimizar)",
    yaxis_title="f₂: Tiempo de Entrega (Minimizar)",
    height=560, legend=dict(bgcolor=theme.FONDO_CREMA),
    plot_bgcolor="white",
)
fig.update_xaxes(showgrid=True, gridcolor="#e8e8e8")
fig.update_yaxes(showgrid=True, gridcolor="#e8e8e8")
st.plotly_chart(fig, width="stretch")

# --- Tabla comparativa ----------------------------------------------------
st.subheader("Tabla comparativa")
tabla = pd.DataFrame([
    ["A Posteriori", "Suma Ponderada", post_pond[0], post_pond[1]],
    ["A Posteriori", "Lexicográfica", post_lex[0], post_lex[1]],
    ["A Priori", "GA Ponderado", apri_pond[0], apri_pond[1]],
    ["A Priori", "GA Lexicográfico", apri_lex[0], apri_lex[1]],
], columns=["Enfoque", "Criterio", "f₁ (Costo)", "f₂ (Tiempo)"])
st.dataframe(tabla.round(2), width="stretch", hide_index=True)

st.info(
    "Mueve el peso del costo: verás que la solución ponderada se desliza por el "
    "frente. Sobre un frente convexo, la elección a priori (GA) y la a posteriori "
    "(sobre el frente) tienden a coincidir."
)
