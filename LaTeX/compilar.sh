#!/usr/bin/env bash
# Compila el reporte LaTeX y deja el PDF final en ../output/.
# Uso: bash compilar.sh   (ejecutar dentro de la carpeta LaTeX/)
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p ../output

# Fecha fija en metadatos → PDF byte-reproducible entre compilaciones.
export SOURCE_DATE_EPOCH=1779321600   # 2026-05-21 UTC
export FORCE_SOURCE_DATE=1

pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex

mv -f main.pdf ../output/Reporte_Multicriterio_Rebull.pdf
echo "✔ PDF generado en ../output/Reporte_Multicriterio_Rebull.pdf"
