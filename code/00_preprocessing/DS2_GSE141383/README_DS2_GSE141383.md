# DS2/GSE141383 preprocessing notebooks — corrected raw-count build

## Execution order

1. `00a_ds2_build_raw_anndata.ipynb`
2. `00b_ds2_quality_control.ipynb`
3. `00c_ds2_doublet_diagnostic.ipynb`

## Expected files in `data/raw/GSE141383/`

- `GSM4202144_PJ052.counts.txt.gz`
- `GSM4202145_PJ053.counts.txt.gz`
- `GSM4202146_PW016-703.counts.txt.gz`
- `GSM4202147_PW017-703.counts.txt.gz`
- `GSM4202148_PW032-706.counts.txt.gz`
- `GSM4202149_PW032-710.counts.txt.gz`
- `GSM5975476_PW035-710.counts.txt.gz`
- `GSM5975477_PDC001.counts.txt.gz`
- `GSM5975478_PW039-705.counts.txt.gz`

## Expected shapes

| Stage | Cells | Features/genes |
|---|---:|---:|
| Merged raw-count object | 29,415 | 60,725 |
| After primary cell QC | 21,500 | 60,725 |
| Final post-QC object | 21,391 | 25,835 |
| Post-Scrublet diagnostic | 21,391 | 25,835 |

## Build behavior

The 00a notebook reads the nine compressed count tables directly. It validates
their headers, cell barcodes, integer counts, gene identifiers, gene symbols,
feature sets, sample names, and final dimensions. Cell identifiers are formed
as `<sample_id>:<original_barcode>` to prevent collisions while retaining the
original barcode in `adata.obs["cell_barcode"]`.

The tables are read in gene-row chunks and converted to sparse matrices to
reduce peak memory use.

## Doublet analysis

The original Scrublet run was performed after QC on the complete DS2 object.
It predicted one doublet, but no cells were removed. The Scrublet-checked file
is therefore a diagnostic derivative rather than the principal analysis input.

Large count tables and h5ad files should not be committed to GitHub.
