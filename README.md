# Análisis de Estrategias de Decisión Multicriterio · A Priori vs. A Posteriori

Práctica de laboratorio de **Optimización Inteligente** (MIAAD — UACJ). Compara
dos filosofías de decisión multicriterio sobre un problema bi-objetivo de
ruteo (Costo vs. Tiempo):

- **A Posteriori** — NSGA-II aproxima todo el frente de Pareto y luego el
  decisor elige (suma ponderada normalizada o criterio lexicográfico).
- **A Priori** — el decisor inyecta sus preferencias *antes* de optimizar y se
  resuelve un GA mono-objetivo (suma ponderada con escalamiento manual o
  lexicográfico directo).

**Alumno:** Javier Augusto Rebull Saucedo (263483) · **Profesor:** Mtro. Raúl
Gibrán Porras Alaniz.

## Problema

$$\min\ f_1(\mathbf{x}) = 4x_1^2 + 4x_2^2 \qquad \min\ f_2(\mathbf{x}) = (x_1-5)^2 + (x_2-5)^2, \qquad \mathbf{x}\in[0,5]^2$$

## Estructura

```
src/                 Código fuente (problema, estrategias, visualización, pipeline)
notebooks/           Notebook explicativo (01_analisis_multicriterio.ipynb)
results/             Salidas reproducibles (pareto_front.csv, *.json)
Figures/             Scatter plot principal (png + pdf) y zoom
LaTeX/               Fuente del reporte académico
output/              Reporte_Multicriterio_Rebull.pdf  ← entregable final
streamlit_app.py     Dashboard interactivo
```

## Reproducir

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 1) Pipeline: genera results/, Figures/ y LaTeX/valores_generados.tex
python -m src.main

# 2) Reporte PDF (requiere LaTeX con siunitx, mathpazo, titlesec, babel-spanish)
bash LaTeX/compilar.sh        # deja el PDF en output/

# 3) Dashboard interactivo (opcional)
streamlit run streamlit_app.py
```

Todo es determinista: `seed=1` en ambos algoritmos. **Ningún número del reporte
se teclea a mano**: `src/export_latex.py` genera las macros LaTeX a partir de
`results/*.json`.

## Resultados clave

| Enfoque | Criterio | f₁ (Costo) | f₂ (Tiempo) |
|---|---|---:|---:|
| A Posteriori | Suma Ponderada | 20.18 | 23.32 |
| A Posteriori | Lexicográfica | 200.00 | 0.00 |
| A Priori | GA Ponderado | 18.00 | 24.50 |
| A Priori | GA Lexicográfico | 200.00 | 0.00 |

Las soluciones ponderadas coinciden casi exactamente (frente convexo); la
lexicográfica sacrifica todo el costo (f₁ = 200) por minimizar el tiempo.

## Despliegue web (Streamlit Community Cloud)

El dashboard es autocontenido (recalcula el frente; no depende de `results/`),
por lo que se despliega directo desde este repo público:

1. Entra a **https://share.streamlit.io** e inicia sesión con GitHub.
2. **New app** → repo `jrebull/MIAAD_SMART_Multicriterio`, branch `main`,
   main file `streamlit_app.py`, Python **3.12**.
3. **Deploy**. La primera build instala dependencias (incluye `pymoo`); tarda
   unos minutos. La app queda en una URL `https://<nombre>.streamlit.app`.

Atajo con el formulario pre-llenado:
`https://share.streamlit.io/deploy?repository=jrebull/MIAAD_SMART_Multicriterio&branch=main&mainModule=streamlit_app.py`

El tema institucional UACJ se aplica vía `.streamlit/config.toml`.
