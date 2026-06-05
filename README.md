# Examen Final — Análisis de Genes Diferencialmente Expresados

Este proyecto analiza resultados de RNA-seq (DESeq2) de células epiteliales humanas (A549) infectadas con el virus de la influenza A (IAV) versus control (mock). Identifica genes inducidos y reprimidos, los anota funcionalmente con datos de GFF3,
y genera un reporte interpretable.

## Archivos clave

- `analyze_degs.py`: script principal con manejo de argumentos.
- `deseq_utils.py`: funciones reutilizables para leer TSV, GFF3, clasificar genes y encontrar extremos.
- `tests/test_deseq_utils.py`: pruebas unitarias con `pytest`.

## Uso

Desde la raíz del proyecto:

```bash
uv run python analyze_degs.py \
  --input datos/iav_deseq2_results.tsv \
  --gff datos/human_genes.gff \
  --padj-threshold 0.05 \
  --lfc-threshold 1.0 \
  --output-dir results/
```

## Pruebas

```bash
uv run pytest tests/ -v
```

## Notas

Asegúrate de no commitear el directorio `.venv/` y `results/`.
