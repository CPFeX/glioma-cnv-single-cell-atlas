# Main analysis notebook order

Run all notebooks from a fresh kernel, top to bottom, in numeric filename order.

## Integration and clustering

| Order | Notebook | Purpose |
|---:|---|---|
| 01 | `01_merge_harmonized_datasets.ipynb` | Harmonize gene identifiers and merge four post-QC datasets |
| 02 | `02_standardize_metadata.ipynb` | Standardize dataset, sample, patient, and condition metadata |
| 03 | `03_select_hvg8000.ipynb` | Select 8,000 highly variable genes |
| 04 | `04_train_scvi.ipynb` | Train scVI and calculate the latent representation |
| 05 | `05_select_leiden_resolution.ipynb` | Evaluate Leiden resolutions and retain `r = 0.6` |
| 06 | `06_transfer_scvi_to_fullgene.ipynb` | Transfer latent coordinates and cluster labels to the full-gene object |

## Marker annotation

| Order | Notebook | Purpose |
|---:|---|---|
| 07 | `07_marker_de.ipynb` | Calculate cluster marker genes |
| 08 | `08_marker_annotation.ipynb` | Assign marker-supported draft annotations |
| 09 | `09_annotation_bias_qc.ipynb` | Audit annotation composition and candidate CNV-reference groups |

## CNV inference and final compartments

| Order | Notebook | Purpose |
|---:|---|---|
| 10 | `10_prepare_infercnvpy_inputs.ipynb` | Prepare ordered-gene infercnvpy inputs |
| 11 | `11_run_infercnvpy.ipynb` | Run infercnvpy robustness strategies |
| 12 | `12_infercnvpy_qc.ipynb` | Summarize infercnvpy results |
| 13 | `13_prepare_copykat_microbatches.ipynb` | Prepare CopyKAT microbatches and R runner scripts |
| 14 | `14_integrate_copykat.ipynb` | Integrate completed CopyKAT predictions |
| 15 | `15_build_cnv_consensus.ipynb` | Combine CopyKAT, infercnvpy, and marker evidence |
| 16 | `16_validate_cnv_consensus.ipynb` | Validate CNV-supported compartments |
| 17 | `17_finalize_annotation.ipynb` | Create the final annotation and compartment object |

**Required boundary:** after notebook 13, execute the generated R/CopyKAT jobs and confirm completion before running notebook 14.

## Composition and malignant states

| Order | Notebook | Purpose |
|---:|---|---|
| 18 | `18_differential_abundance.ipynb` | Sample-level composition and differential abundance |
| 19 | `19_correct_da_binomial_glm.ipynb` | Corrected binomial-GLM sensitivity analysis |
| 20 | `20_define_malignant_states.ipynb` | Define malignant states and program scores |

## Pseudobulk and enrichment

| Order | Notebook | Purpose |
|---:|---|---|
| 21 | `21_malignant_state_pseudobulk.ipynb` | Malignant-state pseudobulk differential expression |
| 22 | `22_condition_pseudobulk.ipynb` | Condition-level and within-state pseudobulk analyses |
| 23 | `23_curated_enrichment.ipynb` | Curated over-representation analysis |
| 24 | `24_gprofiler_validation.ipynb` | g:Profiler validation of selected gene lists |

Notebook 24 requires internet access to the g:Profiler API. Enrichr is not part of the release workflow.

## Cell–cell communication

| Order | Notebook | Purpose |
|---:|---|---|
| 25 | `25_prepare_liana_inputs.ipynb` | Prepare LIANA cell groups and inputs |
| 26 | `26_run_liana_global.ipynb` | Global LIANA inference |
| 27 | `27_clean_liana_global_labels.ipynb` | Standardize labels and focused axes |
| 28 | `28_run_liana_condition_specific.ipynb` | Condition-specific LIANA analyses |
| 29 | `29_prioritize_liana_axes.ipynb` | Prioritize communication axes |
| 30 | `30_squidpy_lr_support.ipynb` | Squidpy transcriptomic support |

## Exploratory trajectory analysis

| Order | Notebook | Purpose |
|---:|---|---|
| 31 | `31_cellrank_exploratory.ipynb` | Memory-safe exploratory CellRank fate mapping |

CellRank is exploratory and should not be interpreted as RNA-velocity or lineage-tracing evidence.

## Expected major dimensions

| Object | Expected dimensions |
|---|---:|
| Integrated full-gene object | 351,427 cells × 15,176 genes |
| HVG/scVI object | 351,427 cells × 8,000 genes |
| Malignant-state object | 161,884 cells |
| CellRank subset | 20,000 cells |

The machine-readable authoritative run order is stored in [`../../docs/main_pipeline_run_order.tsv`](../../docs/main_pipeline_run_order.tsv).
