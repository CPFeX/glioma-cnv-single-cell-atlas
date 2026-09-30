# v1.1.0 — Patient-level sensitivity analyses and archived results

Prepared for release; publication and a version-specific Zenodo DOI are pending.

This release extends the primary workflow with source-backed patient-level sensitivity analyses. It distinguishes 83 regional samples from 57 independent patients, corrects cross-cohort DS3 patient-identifier collisions, and reassesses compartment composition, malignant-state proportions, program scores and overall malignant pseudobulk expression after within-patient aggregation.

The release includes the four previously committed validation notebooks and a checked archive of 39 authoritative output files, identical to manuscript Additional file 3. The archive contains complete patient-level DE results and aggregated pseudobulk matrices, with SHA256 manifests and a read-only verification utility. The reproduction guide documents inputs, execution order and the earlier diagnostic's role.

The interpretation explicitly retains small-group limitations, condition–dataset confounding and the absence of significant within-DS3 ndGBM-versus-rGBM DE at the reporting threshold. Main analysis outputs remain unchanged. Documentation also clarifies use of archived canonical scVI/Leiden, CopyKAT and exploratory CellRank outputs. No inference was rerun during release packaging.

The existing v1.0.1 DOI identifies the earlier primary-workflow archive; it does not cover these additions. Keep prior releases and their tags. After v1.1.0 is published and archived, use its verified version DOI when citing this expanded release.
