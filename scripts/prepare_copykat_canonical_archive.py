#!/usr/bin/env python
from pathlib import Path
import csv
import gzip
import hashlib
import os
import shutil
import sys

import pandas as pd


EXPECTED_BUNDLE_SHA256 = (
    "7b3f8c2b87847fcbcf3dff54a37dc077"
    "782e465da662cfcb9288914b9b9610b3"
)

EXPECTED_CALL_COUNTS = {
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
        ):
            return p

    return start


def sha256_file(path, chunk_size=8 * 1024 * 1024):
    digest = hashlib.sha256()

    with Path(path).open("rb") as handle:
        while True:
            block = handle.read(chunk_size)
            if not block:
                break
            digest.update(block)

    return digest.hexdigest()


PROJECT_DIR = find_repo()
METADATA_DIR = PROJECT_DIR / "metadata"
HIST_DIR = METADATA_DIR / "historical_copykat"
CANONICAL_DIR = METADATA_DIR / "canonical"

SOURCE_CALLS = (
    HIST_DIR
    / "copykat_microbatch_final_cell_calls_HVG8000_r0_6.tsv"
)

SOURCE_BUNDLE_CANDIDATES = [
    CANONICAL_DIR
    / "copykat_microbatch_predictions_bundle_HVG8000_r0_6.tar.gz",

    HIST_DIR
    / "copykat_microbatch_predictions_bundle_HVG8000_r0_6.tar.gz",

    PROJECT_DIR
    / "copykat_microbatch_predictions_bundle_HVG8000_r0_6.tar.gz",
]

OUT_CALLS_GZ = (
    CANONICAL_DIR
    / "copykat_microbatch_final_cell_calls_HVG8000_r0_6.tsv.gz"
)

OUT_BUNDLE = (
    CANONICAL_DIR
    / "copykat_microbatch_predictions_bundle_HVG8000_r0_6.tar.gz"
)

OUT_MANIFEST = (
    CANONICAL_DIR
    / "copykat_canonical_manifest.tsv"
)

if not SOURCE_CALLS.exists():
    raise FileNotFoundError(
        "Historical final-cell-call TSV not found:\n"
        f"{SOURCE_CALLS}"
    )

bundle_source = next(
    (
        p
        for p in SOURCE_BUNDLE_CANDIDATES
        if p.exists()
    ),
    None,
)

if bundle_source is None:
    raise FileNotFoundError(
        "Canonical historical prediction bundle was not found."
    )

print("Historical calls:", SOURCE_CALLS)
print("Prediction bundle:", bundle_source)

calls = pd.read_csv(
    SOURCE_CALLS,
    sep="\t",
    usecols=[
        "cell_id",
        "copykat_microbatch_pred",
    ],
)

if len(calls) != 351427:
    raise RuntimeError(
        f"Historical final-call TSV has {len(calls)} rows; expected 351427."
    )

if calls["cell_id"].astype(str).duplicated().any():
    raise RuntimeError(
        "Historical final-call TSV contains duplicate cell IDs."
    )

counts = (
    calls[
        "copykat_microbatch_pred"
    ]
    .astype(str)
    .value_counts()
    .to_dict()
)

for call, expected in EXPECTED_CALL_COUNTS.items():
    observed = int(
        counts.get(
            call,
            0,
        )
    )

    if observed != expected:
        raise RuntimeError(
            f"Historical checkpoint failed for {call}: "
            f"{observed} != {expected}"
        )

bundle_sha = sha256_file(
    bundle_source
)

if bundle_sha != EXPECTED_BUNDLE_SHA256:
    raise RuntimeError(
        "Historical prediction bundle checksum mismatch."
    )

CANONICAL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

if bundle_source.resolve() != OUT_BUNDLE.resolve():
    tmp_bundle = OUT_BUNDLE.with_suffix(
        OUT_BUNDLE.suffix + ".tmp"
    )

    if tmp_bundle.exists():
        tmp_bundle.unlink()

    shutil.copyfile(
        bundle_source,
        tmp_bundle,
    )

    os.replace(
        tmp_bundle,
        OUT_BUNDLE,
    )

tmp_calls = OUT_CALLS_GZ.with_suffix(
    OUT_CALLS_GZ.suffix + ".tmp"
)

if tmp_calls.exists():
    tmp_calls.unlink()

print(
    "Creating deterministic gzip:",
    OUT_CALLS_GZ,
)

with SOURCE_CALLS.open("rb") as fin, tmp_calls.open("wb") as raw_out:
    with gzip.GzipFile(
        filename="",
        mode="wb",
        fileobj=raw_out,
        compresslevel=9,
        mtime=0,
    ) as gz:
        shutil.copyfileobj(
            fin,
            gz,
            length=8 * 1024 * 1024,
        )

    raw_out.flush()
    os.fsync(
        raw_out.fileno()
    )

os.replace(
    tmp_calls,
    OUT_CALLS_GZ,
)

calls_sha = sha256_file(
    OUT_CALLS_GZ
)

bundle_sha = sha256_file(
    OUT_BUNDLE
)

manifest = pd.DataFrame(
    [
        {
            "artifact": OUT_CALLS_GZ.name,
            "sha256": calls_sha,
            "size_bytes": OUT_CALLS_GZ.stat().st_size,
            "role": "canonical paper-defining CopyKAT final cell calls",
        },
        {
            "artifact": OUT_BUNDLE.name,
            "sha256": bundle_sha,
            "size_bytes": OUT_BUNDLE.stat().st_size,
            "role": "canonical archived 176-microbatch prediction provenance bundle",
        },
    ]
)

tmp_manifest = OUT_MANIFEST.with_suffix(
    OUT_MANIFEST.suffix + ".tmp"
)

manifest.to_csv(
    tmp_manifest,
    sep="\t",
    index=False,
)

os.replace(
    tmp_manifest,
    OUT_MANIFEST,
)

print("\nCANONICAL ARCHIVE READY")
print("Calls gzip:", OUT_CALLS_GZ)
print("Calls SHA256:", calls_sha)
print("Bundle:", OUT_BUNDLE)
print("Bundle SHA256:", bundle_sha)
print("Manifest:", OUT_MANIFEST)
print(
    "\nCommit metadata/canonical/ to the repository. "
    "Future users do not run this preparation script; they only run Notebook 14."
)
