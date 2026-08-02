# DS3/GSE182109 preprocessing notebooks

## Execution order

1. `00a_ds3_build_raw_anndata.ipynb`
2. `00b_ds3_quality_control.ipynb`
3. `00c_ds3_doublet_diagnostic.ipynb`

## Expected dimensions

| Stage | Cells | Genes |
|---|---:|---:|
| Merged raw-count object | 264,951 | 38,224 |
| After primary cell QC | 219,418 | 38,224 |
| Final post-QC object | 218,735 | 30,284 |
| Scrublet diagnostic output | 218,735 | 30,284 |

## RAW input format

Place all 44 complete 10x triplets in:

`data/raw/GSE182109/`

Each prefix requires matching matrix, feature, and barcode files.

## QC thresholds

- genes: >500 and <8,000
- total counts: >1,000 and <60,000
- mitochondrial fraction: <12%
- final total-count ceiling: 45,000
- final gene filter: detected in at least 10 cells

## Doublet screening

The recorded Scrublet analysis was sample-aware and post-QC. Two samples with
fewer than 500 cells were not checked. The historical run called 2,927
doublets, 215,146 singlets, and left 662 cells unchecked.

Predicted doublets were not excluded from the main analysis. This is necessary
because the reported DS3 and integrated-object totals use all 218,735 post-QC
DS3 cells.

Large count matrices and h5ad objects should not be committed to GitHub.
