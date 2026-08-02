# Dataset-specific preprocessing

This directory contains the reproducible preprocessing workflows for the four public glioma scRNA-seq datasets.

## Execution pattern

Within each dataset directory, run:

```text
00a — reconstruct the raw-count AnnData object
00b — apply dataset-specific QC and save the post-QC object
00c — run the post-QC Scrublet diagnostic
```

The `00c` notebooks add `doublet_score` and `predicted_doublet` metadata. Predicted doublets were not removed from the primary analysis objects.

## Expected dimensions

| Dataset | RAW/merged object | Final post-QC object | Main integration input |
|---|---:|---:|---|
| DS1/GSE103224 | 23,793 × 60,725 | 23,207 × 29,457 | `GSE103224_postQC.h5ad` |
| DS2/GSE141383 | 29,415 × 60,725 | 21,391 × 25,835 | `GSE141383_postQC.h5ad` |
| DS3/GSE182109 | 264,951 × 38,224 | 218,735 × 30,284 | `GSE182109_postQC.h5ad` |
| DS4/GSE278450 | 91,336 × 36,116 | 88,094 × 24,584 | `GSE278450_postQC.h5ad` |

The four post-QC cell counts sum to **351,427**.

## RAW input formats

### DS1/GSE103224

Eight compressed gene-by-cell count matrices:

```text
GSM*_PJ*.filtered.matrix.txt.gz
```

### DS2/GSE141383

Nine compressed count tables:

```text
*.counts.txt.gz
```

### DS3/GSE182109

Forty-four complete 10x Genomics triplets:

```text
<prefix>_matrix.mtx.gz
<prefix>_features.tsv.gz
<prefix>_barcodes.tsv.gz
```

### DS4/GSE278450

Twenty-two compressed raw-count tables:

```text
*_RawData.tsv.gz
```

Normalized DS4 tables are not used.

## Local data directories

```text
data/raw/GSE103224/
data/raw/GSE141383/
data/raw/GSE182109/
data/raw/GSE278450/

data/interim/
data/processed/DS1_GSE103224/
data/processed/DS2_GSE141383/
data/processed/DS3_GSE182109/
data/processed/DS4_GSE278450/
```

Large input and output files are excluded by `.gitignore`.

## Dataset documentation

Each dataset directory includes a dedicated README and, where needed, provenance notes describing source-specific assumptions and reconstruction decisions.
