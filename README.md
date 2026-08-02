# CNV-Informed Single-Cell Integration Across the Glioma Spectrum

Reproducible analysis code for the study:

**CNV-Informed Single-Cell Integration Across the Glioma Spectrum Maps Malignant-State Heterogeneity and Candidate Tumor–Microenvironment Communication Axes**

This repository contains dataset-specific preprocessing notebooks and the cleaned analysis workflow used to integrate four public glioma single-cell RNA-sequencing datasets, define CNV-supported cellular compartments, characterize malignant transcriptional states, perform pseudobulk differential expression and enrichment analyses, and prioritize candidate ligand–receptor communication axes.

## Datasets

| Dataset | GEO accession | Post-QC cells |
|---|---|---:|
| DS1 | GSE103224 | 23,207 |
| DS2 | GSE141383 | 21,391 |
| DS3 | GSE182109 | 218,735 |
| DS4 | GSE278450 | 88,094 |
| **Integrated total** | — | **351,427** |

The raw GEO files and generated AnnData objects are intentionally excluded from Git. See [`data/README.md`](data/README.md) for the expected local directory layout.

## Repository structure

```text
.
├── code/
│   ├── 00_preprocessing/     # RAW reconstruction, dataset-specific QC, Scrublet diagnostics
│   └── 01_main_analysis/     # 31 ordered analysis notebooks
├── config/                   # Example environment-variable configuration
├── data/                     # Local data layout only; large files are ignored
├── docs/                     # Run order, notebook mapping, validation, and cleaning report
├── environment/              # Python requirements and R environment check
├── metadata/                 # Small project metadata files
├── supplementary/            # Submission-related supplementary materials
├── CITATION.cff
├── LICENSE
└── README.md
```

## Reproducibility status

The public notebooks were cleaned for repository release:

- machine-specific absolute paths were removed;
- paths resolve from the repository root or `GLIOMA_PROJECT_ROOT`;
- stored notebook outputs and execution counters were cleared;
- Python code cells were checked for syntax validity;
- input/output contracts and expected object dimensions were added;
- the obsolete Enrichr branch was removed;
- g:Profiler is retained as the online enrichment validation workflow;
- CellRank is explicitly presented as exploratory analysis.

Full end-to-end runtime validation still requires the original GEO-derived data, GENCODE v49, the CopyKAT R environment, and the package versions listed in [`environment/requirements.txt`](environment/requirements.txt).

## Installation

Create and activate a dedicated Python environment, then install the pinned packages:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r environment/requirements.txt
```

Linux or macOS:

```bash
source .venv/bin/activate
pip install -r environment/requirements.txt
```

Register the Jupyter kernel:

```bash
python -m ipykernel install --user \
  --name glioma-cnv-atlas \
  --display-name "Glioma CNV Atlas"
```

Copy the example configuration if environment-variable overrides are needed:

```bash
cp config/example.env .env
```

## Data preparation

Place the downloaded GEO files under:

```text
data/raw/GSE103224/
data/raw/GSE141383/
data/raw/GSE182109/
data/raw/GSE278450/
```

Place the GENCODE reference at:

```text
data/reference/gencode.v49.primary_assembly.annotation.gtf.gz
```

Detailed dataset-specific requirements are documented under [`code/00_preprocessing/`](code/00_preprocessing/).

## Execution

### 1. Dataset-specific preprocessing

For each dataset, run the three notebooks in numerical order:

```text
00a_*_build_raw_anndata.ipynb
00b_*_quality_control.ipynb
00c_*_doublet_diagnostic.ipynb
```

The Scrublet notebooks retain doublet scores and calls as diagnostic metadata. Predicted doublets were not removed from the main integration inputs. The main pipeline uses the four `postQC.h5ad` objects.

### 2. Main analysis

Run the notebooks under [`code/01_main_analysis/`](code/01_main_analysis/) from `01` through `31`, using a fresh kernel and executing each notebook from top to bottom.

The authoritative run order is stored in:

[`docs/main_pipeline_run_order.tsv`](docs/main_pipeline_run_order.tsv)

Important boundaries:

- Notebook 13 prepares CopyKAT microbatches and generates R runner scripts.
- Run the generated CopyKAT jobs before notebook 14.
- Notebook 24 requires internet access to the g:Profiler API.
- Notebooks 26 and 28 require LIANA.
- Notebook 30 requires Squidpy.
- Notebook 31 is exploratory CellRank analysis and is not RNA-velocity or lineage-tracing evidence.

## Expected major dimensions

| Analysis object | Expected dimensions |
|---|---:|
| Integrated full-gene object | 351,427 cells × 15,176 genes |
| HVG/scVI branch | 351,427 cells × 8,000 genes |
| Malignant-state analysis | 161,884 cells |
| Exploratory CellRank subset | 20,000 cells |

Assertions in the notebooks stop execution when critical dimensions or required metadata do not match the recorded workflow.

## Documentation

- [`docs/CLEANING_REPORT.md`](docs/CLEANING_REPORT.md): changes made during repository preparation
- [`docs/main_pipeline_run_order.tsv`](docs/main_pipeline_run_order.tsv): ordered notebook execution plan
- [`docs/original_to_clean_notebook_mapping.tsv`](docs/original_to_clean_notebook_mapping.tsv): mapping from original to cleaned notebooks
- [`docs/notebook_validation.json`](docs/notebook_validation.json): notebook-level static validation
- [`docs/package_validation_summary.json`](docs/package_validation_summary.json): package-level validation summary

## Large files and generated outputs

Do not commit raw count matrices, AnnData objects, model checkpoints, CopyKAT outputs, figures, logs, or generated result tables. The repository `.gitignore` excludes these classes of files.

## Citation

Please cite the associated article and the archived software release. Machine-readable citation metadata are provided in [`CITATION.cff`](CITATION.cff).

The Zenodo DOI will be added after the first public GitHub release is archived.

## License

The analysis code is released under the [MIT License](LICENSE). Third-party software and source datasets remain subject to their respective licenses and terms.
