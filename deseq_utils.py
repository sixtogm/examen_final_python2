# ── Uso de IA ───────────────────────────────────────────────
# Herramienta : GitHub Copilot
# Prompt usado: "función para parsear columna attributes de GFF3"
# Qué generó  : la estructura de lectura de archivos TSV y GFF3
# Qué modifiqué: añadí manejo de errores, validación de columnas y skipping de filas inválidas
# ────────────────────────────────────────────────────────────

"""Módulo de utilidades para análisis DESeq2.

Contiene funciones para leer resultados TSV, parsear GFF3, clasificar genes y encontrar extremos.
"""

import csv
import sys
from typing import Dict, List


def read_tsv(filepath: str) -> List[Dict[str, object]]:
    """Leer un archivo TSV de resultados DESeq2 y devolver una lista de genes.

    Parameters
    ----------
    filepath : str
        Ruta al archivo TSV de DESeq2.

    Returns
    -------
    list[dict]
        Lista de diccionarios con los campos convertidos apropiadamente.

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.
    ValueError
        Si falta alguna columna obligatoria o no se pueden convertir valores.
    """
    expected_columns = [
        'gene_id',
        'baseMean',
        'log2FoldChange',
        'lfcSE',
        'stat',
        'pvalue',
        'padj',
    ]

    try:
        with open(filepath, 'r', encoding='utf-8', newline='') as handle:
            reader = csv.DictReader(handle, delimiter='\t')
            if reader.fieldnames is None:
                raise ValueError(f'El archivo {filepath} no contiene un encabezado válido.')

            missing_columns = [col for col in expected_columns if col not in reader.fieldnames]
            if missing_columns:
                raise ValueError(f'Faltan columnas obligatorias en el TSV: {", ".join(missing_columns)}')

            genes = []
            invalid_rows = 0
            for line_number, row in enumerate(reader, start=2):
                if not row or all(v.strip() == '' for v in row.values()):
                    continue

                try:
                    gene_id = str(row['gene_id']).strip()
                    if not gene_id:
                        raise ValueError('gene_id vacío')

                    gene = {
                        'gene_id': gene_id,
                        'baseMean': float(row['baseMean']),
                        'log2FoldChange': float(row['log2FoldChange']),
                        'lfcSE': float(row['lfcSE']),
                        'stat': float(row['stat']),
                        'pvalue': float(row['pvalue']),
                        'padj': float(row['padj']),
                    }
                    genes.append(gene)
                except (ValueError, TypeError) as exc:
                    invalid_rows += 1
                    print(
                        f'Advertencia: fila {line_number} ignorada en {filepath} debido a un valor no válido ({exc}).',
                        file=sys.stderr,
                    )

            if not genes:
                raise ValueError(f'No se cargó ningún gen válido desde {filepath}.')

            if invalid_rows > 0:
                print(
                    f'Se omitieron {invalid_rows} fila(s) inválida(s) de {filepath}.',
                    file=sys.stderr,
                )

            return genes
    except FileNotFoundError as exc:
        raise FileNotFoundError(f'No se encontró el archivo TSV: {filepath}') from exc


def read_gff(filepath: str) -> Dict[str, str]:
    """Leer un archivo GFF3 y devolver un diccionario de anotaciones por gen.

    Parameters
    ----------
    filepath : str
        Ruta al archivo GFF3.

    Returns
    -------
    dict
        Diccionario con clave `gene_id` y valor `description`.

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.
    ValueError
        Si el archivo no contiene datos válidos.
    """
    annotations: Dict[str, str] = {}

    try:
        with open(filepath, 'r', encoding='utf-8') as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip() or line.startswith('#'):
                    continue

                parts = line.rstrip('\n').split('\t')
                if len(parts) < 9:
                    print(
                        f'Advertencia: línea {line_number} en {filepath} no tiene 9 columnas, se omite.',
                        file=sys.stderr,
                    )
                    continue

                attributes_text = parts[8]
                try:
                    attributes = {}
                    for item in attributes_text.split(';'):
                        if '=' not in item:
                            continue
                        key, value = item.split('=', 1)
                        attributes[key.strip()] = value.strip()

                    gene_name = attributes.get('Name')
                    description = attributes.get('description', 'anotación no disponible en GFF')
                    if gene_name:
                        annotations[gene_name] = description
                    else:
                        print(
                            f'Advertencia: línea {line_number} en {filepath} no tiene Name=, se omite.',
                            file=sys.stderr,
                        )
                except Exception as exc:
                    print(
                        f'Advertencia: no se pudo parsear la línea {line_number} en {filepath} ({exc}).',
                        file=sys.stderr,
                    )

        if not annotations:
            raise ValueError(f'No se encontró ninguna anotación válida en {filepath}.')

        return annotations
    except FileNotFoundError as exc:
        raise FileNotFoundError(f'No se encontró el archivo GFF3: {filepath}') from exc


def classify_gene(log2fc: float, padj: float, padj_thr: float, lfc_thr: float) -> str:
    """Clasifica un gen como upregulated, downregulated o no_change.

    Parameters
    ----------
    log2fc : float
        Log2 fold change del gen.
    padj : float
        Valor p ajustado (BH).
    padj_thr : float
        Umbral máximo de padj para considerar significativo.
    lfc_thr : float
        Umbral mínimo de |log2FoldChange| para clasificar.

    Returns
    -------
    str
        Una de: 'upregulated', 'downregulated', 'no_change'.
    """
    if padj < padj_thr and log2fc >= lfc_thr:
        return 'upregulated'
    if padj < padj_thr and log2fc <= -lfc_thr:
        return 'downregulated'
    return 'no_change'


def find_extremes(genes: List[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    """Encontrar los genes extremos entre una lista de genes.

    Parameters
    ----------
    genes : list[dict]
        Lista de genes con campos 'log2FoldChange' y 'padj'.

    Returns
    -------
    dict
        Diccionario con las claves 'most_induced', 'most_repressed' y 'most_significant'.
    """
    if not genes:
        return {}

    most_induced = max(genes, key=lambda gene: gene['log2FoldChange'])
    most_repressed = min(genes, key=lambda gene: gene['log2FoldChange'])
    most_significant = min(genes, key=lambda gene: gene['padj'])

    return {
        'most_induced': most_induced,
        'most_repressed': most_repressed,
        'most_significant': most_significant,
    }
