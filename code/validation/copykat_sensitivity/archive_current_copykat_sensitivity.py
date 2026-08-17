#!/usr/bin/env python
from pathlib import Path
import os
import shutil

import pandas as pd
import scanpy as sc


CURRENT_SENSITIVITY_COUNTS = {
    "aneuploid": 236321,
    "diploid": 78019,
    "not.defined": 37085,
    "missing": 2,
}

CANONICAL_COUNTS = {
    "aneuploid": 202895,
    "diploid": 111493,
    "not.defined": 37037,
    "missing": 2,
}


def find_repo(start=None):
    start = Path.cwd() if start is None else Path(start)
    start = start.expanduser().resolve()

    for p in (start, *start.parents):
        if (
            (p / "README.md").exists()
            and (p / "metadata").exists()
            and (p / "data").exists()
        ):
            return p

    return start


PROJECT_DIR = find_repo()
METADATA_DIR = PROJECT_DIR / "metadata"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed" / "integrated"

SENS_METADATA_DIR = (
    METADATA_DIR
    / "sensitivity"
    / "copykat_v1_2_5_known_normals"
)

SENS_H5AD_DIR = (
    PROCESSED_DIR
    / "sensitivity"
)

STANDARD_FINAL = (
    METADATA_DIR
    / "copykat_microbatch_final_cell_calls_HVG8000_r0_6.tsv"
)

STANDARD_H5AD = (
    PROCESSED_DIR
    / "GBM_core_4datasets_fullgene_marker_based_annotation_bias_status_copykat_microbatch.h5ad"
)

METADATA_FILES = [
    "copykat_microbatch_all_prediction_rows_HVG8000_r0_6.tsv",
    "copykat_microbatch_target_only_predictions_HVG8000_r0_6.tsv",
    "copykat_microbatch_final_cell_calls_HVG8000_r0_6.tsv",
    "copykat_microbatch_overall_summary_HVG8000_r0_6.tsv",
    "copykat_microbatch_batch_qc_summary_HVG8000_r0_6.tsv",
    "copykat_microbatch_cluster_summary_HVG8000_r0_6.tsv",
    "copykat_microbatch_annotation_summary_HVG8000_r0_6.tsv",
    "copykat_microbatch_dataset_summary_HVG8000_r0_6.tsv",
    "copykat_microbatch_condition_summary_HVG8000_r0_6.tsv",
    "copykat_microbatch_patient_summary_HVG8000_r0_6.tsv",
    "copykat_microbatch_cluster_condition_summary_HVG8000_r0_6.tsv",
    "copykat_microbatch_cluster_interpretation_HVG8000_r0_6.tsv",
    "copykat_microbatch_integration_output_manifest_HVG8000_r0_6.tsv",
]


def call_counts_from_tsv(path):
    df = pd.read_csv(
        path,
        sep="\t",
        usecols=[
            "copykat_microbatch_pred",
        ],
    )

    return (
        df[
            "copykat_microbatch_pred"
        ]
        .astype(str)
        .value_counts()
        .to_dict()
    )


def exact_counts(observed, expected):
    return all(
        int(
            observed.get(
                call,
                0,
            )
        )
        == value
        for call, value
        in expected.items()
    )


if not STANDARD_FINAL.exists():
    print(
        "No standard Notebook-14 final-call TSV exists. "
        "Nothing needs to be archived."
    )
    raise SystemExit(0)

counts = call_counts_from_tsv(
    STANDARD_FINAL
)

print(
    "Existing standard CopyKAT counts:",
    counts,
)

if exact_counts(
    counts,
    CANONICAL_COUNTS,
):
    print(
        "The standard outputs are already canonical historical outputs. "
        "No sensitivity archival is required."
    )
    raise SystemExit(0)

if not exact_counts(
    counts,
    CURRENT_SENSITIVITY_COUNTS,
):
    raise RuntimeError(
        "Existing standard CopyKAT outputs match neither the known "
        "historical canonical result nor the known CopyKAT 1.2.5 "
        "known-normal sensitivity rerun. Refusing to move unknown outputs."
    )

SENS_METADATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

SENS_H5AD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

for name in METADATA_FILES:
    src = METADATA_DIR / name

    if not src.exists():
        continue

    dst = SENS_METADATA_DIR / name

    if dst.exists():
        raise FileExistsError(
            f"Sensitivity destination already exists: {dst}"
        )

    print(
        "[MOVE]",
        src,
        "->",
        dst,
    )

    src.replace(
        dst
    )

if STANDARD_H5AD.exists():
    check = sc.read_h5ad(
        STANDARD_H5AD,
        backed="r",
    )

    try:
        if (
            "copykat_microbatch_pred"
            not in check.obs.columns
        ):
            raise RuntimeError(
                "Existing standard H5AD lacks copykat_microbatch_pred."
            )

        h5_counts = (
            check.obs[
                "copykat_microbatch_pred"
            ]
            .astype(str)
            .value_counts()
            .to_dict()
        )

    finally:
        check.file.close()

    if not exact_counts(
        h5_counts,
        CURRENT_SENSITIVITY_COUNTS,
    ):
        raise RuntimeError(
            "Existing standard H5AD does not match the known current "
            "sensitivity rerun. Refusing to move it."
        )

    dst_h5ad = (
        SENS_H5AD_DIR
        / "GBM_core_4datasets_fullgene_marker_based_annotation_bias_status_"
          "copykat_sensitivity_v1_2_5_known_normals.h5ad"
    )

    if dst_h5ad.exists():
        raise FileExistsError(
            f"Sensitivity H5AD destination already exists: {dst_h5ad}"
        )

    print(
        "[MOVE]",
        STANDARD_H5AD,
        "->",
        dst_h5ad,
    )

    STANDARD_H5AD.replace(
        dst_h5ad
    )

print(
    "\nDONE: current CopyKAT 1.2.5 known-normal outputs were preserved "
    "under the sensitivity directories. The standard Notebook-14 output "
    "paths are now free for the canonical historical integration."
)
