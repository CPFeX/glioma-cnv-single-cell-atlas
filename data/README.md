# Data layout

Large GEO count files and AnnData objects are intentionally excluded from Git.
Use the following local layout:

- `raw/GSE103224/`, `raw/GSE141383/`, `raw/GSE182109/`, `raw/GSE278450/`
- `interim/` for reconstructed and CNV intermediate files
- `processed/DS1_GSE103224/` through `processed/DS4_GSE278450/`
- `processed/integrated/` for integrated pipeline outputs
- `reference/gencode.v49.primary_assembly.annotation.gtf.gz`

The main analysis begins with the four post-QC objects produced by the
preprocessing notebooks. Scrublet-checked derivatives are diagnostic and are
not used as the main integration inputs.
