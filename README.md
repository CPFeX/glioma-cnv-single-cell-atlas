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
│   ├── 01_main_analysis/     # 31 ordered analysis notebooks
│   └── validation/           # Patient-level sensitivity and other audit notebooks
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

The initial repository preparation included the following steps. Later executed validation notebooks retain their recorded outputs; the list is not a claim that every current notebook is output-free:

- machine-specific absolute paths were removed;
- paths resolve from the repository root or `GLIOMA_PROJECT_ROOT`;
- stored notebook outputs and execution counters were cleared;
- Python code cells were checked for syntax validity;
- input/output contracts and expected object dimensions were added;
- the obsolete Enrichr branch was removed;
- g:Profiler is retained as an online enrichment annotation workflow;
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

- Notebooks 04–05 retain a fresh integration/clustering reproducibility audit. Notebook 06 transfers the archived canonical embeddings and 18-cluster partition to the article branch; the fresh run yielded 15 clusters at resolution 0.6.
- Notebook 13 documents the CopyKAT microbatch design. Notebook 14 integrates checked canonical archived calls from 176 microbatches; a modern CopyKAT rerun is not required for the article branch. See [`COPYKAT_REPRODUCIBILITY.md`](COPYKAT_REPRODUCIBILITY.md).
- Notebook 24 requires internet access to the g:Profiler API.
- Notebooks 26 and 28 require LIANA.
- Notebook 30 requires Squidpy.
- Notebook 31 replays mapped archived exploratory CellRank outputs and does not refit the historical kernel or GPCCA model. It is not RNA-velocity or lineage-tracing evidence.

### 3. Source-backed patient-level sensitivity analyses

The atlas contains 83 samples from 57 independent patients. Regional samples are aggregated within patients; reused numeric DS3 identifiers across diagnostic groups do not establish longitudinal pairing. Four notebooks under `code/validation` document the initial patient-condition diagnostic, corrected source-backed design, composition/program reanalysis, and malignant pseudobulk reanalysis.

See [`docs/PATIENT_LEVEL_REPRODUCIBILITY.md`](docs/PATIENT_LEVEL_REPRODUCIBILITY.md) for the execution order, required inputs, statistical qualifications, and archived result package. The checked package in [`supplementary/patient_level_sensitivity/`](supplementary/patient_level_sensitivity/) contains the 39 authoritative saved outputs used in the revised manuscript. It is tracked explicitly outside the ignored working-output directory. No inference was rerun while preparing this release.

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

Raw single-cell count matrices, AnnData objects, model checkpoints, figures and working logs remain excluded. Explicit release exceptions include the canonical CopyKAT archive and the checked patient-level result package under `supplementary/patient_level_sensitivity/`. The latter includes small aggregated patient pseudobulk matrices, result tables and provenance; it does not include raw single-cell matrices. Working outputs under `metadata/sensitivity/` remain ignored.

## Citation

Please cite the associated article and the archived software release. Machine-readable citation metadata are provided in [`CITATION.cff`](CITATION.cff).

The primary workflow version 1.0.1 is archived at [10.5281/zenodo.23015399](https://doi.org/10.5281/zenodo.23015399). The prepared version 1.1.0 adds the later patient-level sensitivity code and checked result package. Its version-specific DOI is pending publication; the 1.0.1 DOI must not be presented as the archive for these later additions. See [`docs/RELEASE_NOTES_v1.1.0.md`](docs/RELEASE_NOTES_v1.1.0.md).

## License

The analysis code is released under the [MIT License](LICENSE). Third-party software and source datasets remain subject to their respective licenses and terms.
