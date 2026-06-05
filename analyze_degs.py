# ── Uso de IA ───────────────────────────────────────────────
# Herramienta : GitHub Copilot
# Prompt usado: "script principal para análisis de genes DE, juntar funciones de utilidades"
# Qué generó  : el flujo principal y el formato de salida
# Qué modifiqué: adapté la lógica de clasificación a los requisitos, añadí manejo de directorio de salida y errores
# ────────────────────────────────────────────────────────────

"""Script principal para analizar genes diferencialmente expresados de DESeq2."""

import argparse
import csv
import os
import sys

from deseq_utils import (
    classify_gene,
    find_extremes,
    read_gff,
    read_tsv,
)

DEFAULT_OUTPUT_DIR = 'results/'


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Analiza genes diferencialmente expresados con DESeq2'
    )
    parser.add_argument(
        '--input', required=True, help='Ruta al archivo TSV de DESeq2'
    )
    parser.add_argument(
        '--gff', required=True, help='Ruta al archivo GFF3 de anotaciones'
    )
    parser.add_argument(
        '--padj-threshold', type=float, default=0.05, help='Umbral de significancia estadística'
    )
    parser.add_argument(
        '--lfc-threshold', type=float, default=1.0, help='Umbral mínimo de cambio en log2FC'
    )
    parser.add_argument(
        '--output-dir', default=DEFAULT_OUTPUT_DIR, help='Directorio para los archivos de salida'
    )
    return parser.parse_args()


def format_float(value: float) -> str:
    return f'{value:.4f}'


def write_tsv(filepath: str, genes: list[dict]) -> None:
    with open(filepath, 'w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter='\t')
        writer.writerow(['gene_id', 'log2FoldChange', 'padj', 'description'])
        for gene in genes:
            writer.writerow([
                gene['gene_id'],
                format_float(gene['log2FoldChange']),
                format_float(gene['padj']),
                gene['description'],
            ])


def write_summary_report(
    filepath: str,
    input_path: str,
    gff_path: str,
    padj_threshold: float,
    lfc_threshold: float,
    total_genes: int,
    annotation_count: int,
    categories: dict,
    extremes: dict,
) -> None:
    lines = [
        'Resumen DESeq2',
        '=====================',
        f'Archivo TSV  : {input_path}',
        f'Archivo GFF  : {gff_path}',
        f'padj_threshold : {padj_threshold}',
        f'lfc_threshold  : {lfc_threshold}',
        f'Genes cargados del TSV : {total_genes}',
        f'Genes cargados del GFF : {annotation_count}',
        '',
        'Clasificación:',
        f'  upregulated  : {len(categories["upregulated"])}',
        f'  downregulated: {len(categories["downregulated"])}',
        f'  no_change    : {len(categories["no_change"])}',
        '',
        'Genes extremos (significativos):',
    ]

    if extremes:
        lines.extend([
            f'  Más inducido  : {extremes["most_induced"]["gene_id"]} '
            f'log2FC = {format_float(extremes["most_induced"]["log2FoldChange"])} '
            f'padj = {format_float(extremes["most_induced"]["padj"])}',
            f'  Más reprimido : {extremes["most_repressed"]["gene_id"]} '
            f'log2FC = {format_float(extremes["most_repressed"]["log2FoldChange"])} '
            f'padj = {format_float(extremes["most_repressed"]["padj"])}',
            f'  Más confiable : {extremes["most_significant"]["gene_id"]} '
            f'padj   = {format_float(extremes["most_significant"]["padj"])}',
        ])
    else:
        lines.append('  No hay genes significativos para calcular extremos.')

    lines.extend(['','Lista de genes diferencialmente expresados:',])

    for category in ['upregulated', 'downregulated']:
        if categories[category]:
            lines.append(f'  {category}:')
            for gene in categories[category]:
                lines.append(
                    f'    {gene["gene_id"]}\tlog2FC={format_float(gene["log2FoldChange"])} '
                    f'padj={format_float(gene["padj"])}\t{gene["description"]}'
                )
            lines.append('')

    with open(filepath, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines).rstrip() + '\n')


def ensure_output_dir(output_dir: str) -> None:
    """Crea el directorio de salida si no existe."""
    os.makedirs(output_dir, exist_ok=True)


def print_console_summary(
    input_path: str,
    gff_path: str,
    padj_threshold: float,
    lfc_threshold: float,
    total_genes: int,
    annotation_count: int,
    categories: dict,
    extremes: dict,
    output_dir: str,
) -> None:
    total = total_genes
    

    print('=================================================')
    print('  Análisis DESeq2: IAV vs Mock')
    print(f'  Archivo: {input_path}')
    print(f'  GFF    : {gff_path}')
    print(f'  padj   : {padj_threshold}   |   |log2FC|: {lfc_threshold}')
    print('=================================================')
    print(f'Genes cargados del TSV  : {total_genes}')
    print(f'Genes cargados del GFF  : {annotation_count}')
    print('')
    print('--- Clasificación ---')
    print(f'  upregulated  : {len(categories["upregulated"]):3d}  ({len(categories["upregulated"])/total*100:4.1f}%)')
    print(f'  downregulated: {len(categories["downregulated"]):3d}  ({len(categories["downregulated"])/total*100:4.1f}%)')
    print(f'  no_change    : {len(categories["no_change"]):3d}  ({len(categories["no_change"])/total*100:4.1f}%)')
    print('')
    print('--- Genes extremos (significativos) ---')

    if extremes:
        print(
            f'  Más inducido  : {extremes["most_induced"]["gene_id"]}   '
            f'log2FC = {format_float(extremes["most_induced"]["log2FoldChange"])}  '
            f'padj = {format_float(extremes["most_induced"]["padj"])}'
        )
        print(
            f'  Más reprimido : {extremes["most_repressed"]["gene_id"]}   '
            f'log2FC = {format_float(extremes["most_repressed"]["log2FoldChange"])}  '
            f'padj = {format_float(extremes["most_repressed"]["padj"])}'
        )
        print(
            f'  Más confiable : {extremes["most_significant"]["gene_id"]}   '
            f'padj   = {format_float(extremes["most_significant"]["padj"])}'
        )
    else:
        print('  No hay genes significativos para calcular extremos.')

    print('')
    print(f'Archivos guardados en: {output_dir}')


def main() -> int:
    args = parse_arguments()
    output_dir = os.path.abspath(args.output_dir)

    try:
        genes = read_tsv(args.input)
        annotations = read_gff(args.gff)
        ensure_output_dir(output_dir)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1

    categories = {'upregulated': [], 'downregulated': [], 'no_change': []}
    for gene in genes:
        gene['description'] = annotations.get(gene['gene_id'], 'sin anotación')
        category = classify_gene(
            gene['log2FoldChange'], gene['padj'], args.padj_threshold, args.lfc_threshold
        )
        categories[category].append(gene)

    significant_genes = categories['upregulated'] + categories['downregulated']
    extremes = find_extremes(significant_genes)

    write_tsv(os.path.join(output_dir, 'upregulated_genes.tsv'), categories['upregulated'])
    write_tsv(os.path.join(output_dir, 'downregulated_genes.tsv'), categories['downregulated'])
    write_summary_report(
        os.path.join(output_dir, 'summary_report.txt'),
        args.input,
        args.gff,
        args.padj_threshold,
        args.lfc_threshold,
        len(genes),
        len(annotations),
        categories,
        extremes,
    )

    print_console_summary(
        args.input,
        args.gff,
        args.padj_threshold,
        args.lfc_threshold,
        len(genes),
        len(annotations),
        categories,
        extremes,
        output_dir,
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
