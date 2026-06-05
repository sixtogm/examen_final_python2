# ── Uso de IA ───────────────────────────────────────────────
# Herramienta : GitHub Copilot
# Prompt usado: "pruebas para clasificar genes y encontrar extremos en deseq_utils"
# Qué generó  : la estructura de las funciones de prueba
# Qué modifiqué: apropié las pruebas para los datos de DESeq2 y añadí casos de borde
# ────────────────────────────────────────────────────────────

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from deseq_utils import classify_gene, find_extremes, read_gff, read_tsv


def test_classify_upregulated():
    """Un gen con padj=0.01 y lfc=3.5 debe ser upregulated."""
    assert classify_gene(3.5, 0.01, padj_thr=0.05, lfc_thr=1.0) == 'upregulated'


def test_classify_downregulated():
    """Un gen con padj=0.01 y lfc=-2.0 debe ser downregulated."""
    assert classify_gene(-2.0, 0.01, padj_thr=0.05, lfc_thr=1.0) == 'downregulated'


def test_classify_no_change_by_padj():
    """Un gen con padj=0.8 aunque tenga lfc alto debe ser no_change."""
    assert classify_gene(4.0, 0.8, padj_thr=0.05, lfc_thr=1.0) == 'no_change'


def test_classify_no_change_by_lfc():
    """Un gen significativo pero con lfc=0.3 debe ser no_change."""
    assert classify_gene(0.3, 0.01, padj_thr=0.05, lfc_thr=1.0) == 'no_change'


def test_find_extremes_returns_correct_keys():
    """find_extremes debe retornar dict con las claves most_induced, most_repressed y most_significant."""
    genes = [
        {'gene_id': 'A', 'log2FoldChange': 5.0, 'padj': 0.01},
        {'gene_id': 'B', 'log2FoldChange': -3.0, 'padj': 0.02},
        {'gene_id': 'C', 'log2FoldChange': 1.5, 'padj': 0.001},
    ]
    extremes = find_extremes(genes)

    assert set(extremes.keys()) == {'most_induced', 'most_repressed', 'most_significant'}
    assert extremes['most_induced']['gene_id'] == 'A'
    assert extremes['most_repressed']['gene_id'] == 'B'
    assert extremes['most_significant']['gene_id'] == 'C'


def test_read_gff_ignores_comments_and_parses_description(tmp_path):
    """read_gff debe parsear correctamente Name y description."""
    content = '##gff-version 3\n# comment line\nchr1\tEnsembl\tgene\t1\t100\t.\t+\t.\tID=ENSG00000000001_TEST;Name=TEST;description=Test gene description;gene_type=protein_coding\n'
    path = tmp_path / 'test.gff'
    path.write_text(content, encoding='utf-8')

    annotations = read_gff(str(path))
    assert annotations['TEST'] == 'Test gene description'


def test_read_tsv_raises_file_not_found():
    """read_tsv debe levantar FileNotFoundError si el archivo no existe."""
    with pytest.raises(FileNotFoundError):
        read_tsv('no_existe.tsv')
