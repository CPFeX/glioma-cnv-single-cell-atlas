# CopyKAT reproducibility layout

This patch separates **paper-result reproduction** from **modern rerun sensitivity analysis**.

## Main paper pipeline

Use this order in `code/01_main_analysis/`:

1. `13_prepare_copykat_microbatches.ipynb`
   - Prepares and documents the CopyKAT microbatch design.
   - The paper-defining result does not require rerunning CopyKAT with the current package version.

2. `14_integrate_copykat_canonical.ipynb`
   - Validates the archived canonical CopyKAT artifacts under `metadata/canonical/`.
   - Integrates the historical paper-defining cell calls.
   - Writes the standard H5AD consumed by Notebook 15.
   - Hard-checks the paper-defining counts:
     - aneuploid: 202,895
     - diploid: 111,493
     - not.defined: 37,037
     - missing: 2

3. `15_build_cnv_consensus.ipynb`
   - Must consume the standard canonical H5AD produced by Notebook 14.

## Canonical archive

Commit these files under `metadata/canonical/`:

- `copykat_microbatch_final_cell_calls_HVG8000_r0_6.tsv.gz`
- `copykat_microbatch_predictions_bundle_HVG8000_r0_6.tar.gz`
- `copykat_canonical_manifest.tsv`

The historical 176-microbatch prediction bundle has the fixed SHA256:

`7b3f8c2b87847fcbcf3dff54a37dc077782e465da662cfcb9288914b9b9610b3`

The compressed final-cell-call table is produced once from the historical Notebook-14 TSV with:

```bash
python scripts/prepare_copykat_canonical_archive.py
```

After repository preparation, ordinary users **do not run that script**. They clone the already-committed canonical archive and run Notebook 14.

## Sensitivity analysis

The later CopyKAT 1.2.5 + known-normal rerun is retained under:

`code/validation/copykat_sensitivity/`

and, for generated outputs:

- `metadata/sensitivity/copykat_v1_2_5_known_normals/`
- `data/processed/integrated/sensitivity/`

It is not silently substituted for the paper-defining result.

The read-only audit found a strong version/baseline-dependent shift, including substantial increases in aneuploid calls in reference/non-malignant-like compartments. This is why the rerun is treated as a sensitivity analysis rather than as an automatic replacement.

## One-time migration for the current working repository

If the standard Notebook-14 output paths currently contain the CopyKAT 1.2.5 known-normal rerun, run:

```bash
python code/validation/copykat_sensitivity/archive_current_copykat_sensitivity.py
```

The helper validates the known sensitivity call counts before moving anything. It refuses to move unknown outputs.

Then run:

```text
14_integrate_copykat_canonical.ipynb
```

The main output path is restored to the canonical historical result, so Notebook 15 can remain in the normal numerical sequence.
