# DS4/GSE278450 preprocessing notebooks

## Execution order

1. `00a_ds4_build_raw_anndata.ipynb`
2. `00b_ds4_quality_control.ipynb`
3. `00c_ds4_doublet_diagnostic.ipynb`

## Expected dimensions

| Stage | Cells | Genes |
|---|---:|---:|
| Merged raw-count object | 91,336 | 36,116 |
| After primary cell QC | 88,246 | 36,116 |
| Final post-QC object | 88,094 | 24,584 |
| Scrublet diagnostic output | 88,094 | 24,584 |

## RAW input format

Place the 22 files ending in `_RawData.tsv.gz` in:

`data/raw/GSE278450/`

Normalized files are not read. The first table column is treated as the gene
index and the remaining columns as cells.

## QC thresholds

- genes: >500 and <5,000
- total counts: >1,000 and <30,000
- mitochondrial fraction: <8%
- final total-count ceiling: 24,000
- final gene filter: detected in at least 10 cells

## Doublet screening

The historical whole-dataset Scrublet run predicted 310 doublets and 87,784
singlets. Doublet calls were stored as diagnostic metadata; no cells were
removed from the main DS4 analysis.

Large count tables and h5ad files should not be committed to GitHub.
