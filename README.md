# glioma-cnv-single-cell-atlas

Reproducible analysis code and supporting materials for:

**CNV-Informed Single-Cell Integration Across the Glioma Spectrum Maps Malignant-State Heterogeneity and Candidate Tumor–Microenvironment Communication Axes**

## Overview

This repository accompanies an integrative single-cell RNA-sequencing analysis of four publicly available human glioma datasets spanning lower-grade glioma, glioblastoma, newly diagnosed glioblastoma, and recurrent glioblastoma.

The workflow includes:

- dataset-specific quality control and gene harmonization
- scVI-based integration and Leiden clustering
- marker-guided annotation
- CopyKAT- and infercnvpy-supported CNV assessment
- sample-level compartment and malignant-state analyses
- pseudobulk differential expression
- curated over-representation analysis and g:Profiler validation
- LIANA ligand–receptor inference
- Squidpy transcriptomic support analysis
- exploratory CellRank fate mapping

## Public datasets

The study reanalyzes the following NCBI Gene Expression Omnibus accessions:

- GSE103224
- GSE141383
- GSE182109
- GSE278450

Raw data are not redistributed in this repository.

## Repository structure

- `code/` — analysis scripts and notebooks
- `config/` — analysis parameters and configuration files
- `metadata/` — sample manifests, harmonization files, and non-sensitive metadata
- `environment/` — package versions and environment specifications
- `docs/` — workflow notes and reproducibility documentation
- `supplementary/` — final supplementary files and selected supporting outputs

## Reproducibility status

The repository is being prepared for the first archived release. Exact execution order, software versions, and input/output relationships will be documented before release.

## Citation

A formal citation will be provided through the archived Zenodo release. See `CITATION.cff`.

## License

Code is released under the MIT License. Third-party datasets and graphical resources remain subject to their original licenses and terms.
