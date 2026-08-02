# DS1/GSE103224 preprocessing notebooks

Execution order:

1. `00a_ds1_build_raw_anndata.ipynb`
2. `00b_ds1_quality_control.ipynb`
3. `00c_ds1_doublet_diagnostic.ipynb`

## Expected shapes

| Stage | Cells | Genes |
|---|---:|---:|
| Loaded raw-count object | 23,793 | 60,725 |
| Post-QC object | 23,207 | 29,457 |
| Post-Scrublet diagnostic | 23,207 | 29,457 |

The Scrublet notebook reproduces the original post-QC diagnostic. It adds
`doublet_score` and `predicted_doublet` metadata but does not remove predicted
doublets. The original run flagged one cell.

## Default data locations

- RAW matrices: `data/raw/GSE103224/`
- Interim AnnData: `data/interim/DS1_GSE103224/`
- Processed AnnData: `data/processed/DS1_GSE103224/`
- Audit tables and plots: `results/qc/DS1_GSE103224/`

Large data files should not be committed to GitHub.
