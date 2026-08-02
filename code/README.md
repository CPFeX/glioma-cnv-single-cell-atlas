# Analysis code

The executable workflow is divided into two ordered sections.

## `00_preprocessing/`

Dataset-specific reconstruction, quality control, and Scrublet diagnostics for:

- DS1 — GSE103224
- DS2 — GSE141383
- DS3 — GSE182109
- DS4 — GSE278450

Each dataset directory contains:

```text
00a_*_build_raw_anndata.ipynb
00b_*_quality_control.ipynb
00c_*_doublet_diagnostic.ipynb
```

Run each notebook from a fresh kernel, top to bottom. The primary integration inputs are the `postQC.h5ad` outputs from the `00b` notebooks. The `00c` outputs are diagnostic derivatives and are not substituted for the main integration inputs.

See [`00_preprocessing/README.md`](00_preprocessing/README.md) for dataset-level dimensions and input formats.

## `01_main_analysis/`

Thirty-one notebooks implementing:

1. gene harmonization and four-dataset merge;
2. metadata standardization;
3. 8,000-HVG selection;
4. scVI integration and Leiden clustering;
5. marker-based annotation;
6. infercnvpy and CopyKAT CNV inference;
7. CNV consensus and final cellular compartments;
8. differential abundance;
9. malignant-state definition;
10. pseudobulk differential expression;
11. curated enrichment and g:Profiler validation;
12. global and condition-specific LIANA;
13. Squidpy transcriptomic support;
14. exploratory CellRank analysis.

Run notebooks in numeric filename order. The exact sequence and special requirements are documented in [`../docs/main_pipeline_run_order.tsv`](../docs/main_pipeline_run_order.tsv) and [`01_main_analysis/README.md`](01_main_analysis/README.md).

## Path handling

Notebooks locate the repository root automatically. The root may also be set explicitly:

```bash
export GLIOMA_PROJECT_ROOT="/path/to/glioma-cnv-single-cell-atlas"
```

Windows PowerShell:

```powershell
$env:GLIOMA_PROJECT_ROOT="C:\path\to\glioma-cnv-single-cell-atlas"
```

## Execution policy

- Start each notebook with a fresh kernel.
- Execute all cells in order.
- Do not continue after a failed assertion.
- Preserve the generated audit summaries and run logs locally.
- Do not commit large data objects or generated outputs.
