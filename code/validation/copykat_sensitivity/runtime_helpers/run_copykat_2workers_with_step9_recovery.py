#!/usr/bin/env python
from pathlib import Path
import csv
import shutil
import subprocess
import sys

ROOT = Path(r"G:\Repository\glioma-cnv-single-cell-atlas")
CODE_DIR = ROOT / r"code\01_main_analysis"
MANIFEST = ROOT / r"metadata\copykat_microbatch_input_manifest_HVG8000_r0_6.tsv"
INNER_RUNNER = CODE_DIR / "run_all_copykat_microbatches_2workers_cleanenv.py"
MAX_RESTARTS = 200


def valid_prediction(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            fields = set(reader.fieldnames or [])
            if not {"cell.names", "copykat.pred"}.issubset(fields):
                return False
            n = sum(1 for _ in reader)
        return n > 0
    except Exception:
        return False


def native_step9_paths(row):
    batch_id = row["batch_id"]
    batch_dir = Path(row["batch_dir"])
    native_pred = batch_dir / f"{batch_id}prediction.txt"
    native_bin = batch_dir / f"{batch_id}final_results_bin_by_cell.txt"
    return native_pred, native_bin


def recover_one(row):
    expected = Path(row["expected_prediction"])
    if valid_prediction(expected):
        return False, "already standardized"

    native_pred, native_bin = native_step9_paths(row)
    if not native_pred.exists() or native_pred.stat().st_size == 0:
        return False, "native prediction missing"
    if not native_bin.exists() or native_bin.stat().st_size == 0:
        return False, "native final bin-by-cell missing"

    # Validate CopyKAT native prediction before promoting it.
    try:
        with native_pred.open("r", encoding="utf-8-sig", errors="replace", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            fields = set(reader.fieldnames or [])
            if not {"cell.names", "copykat.pred"}.issubset(fields):
                return False, f"bad native header: {sorted(fields)}"
            rows = list(reader)
    except Exception as e:
        return False, f"native parse error: {e!r}"

    if not rows:
        return False, "native prediction has zero rows"

    names = [str(r["cell.names"]) for r in rows]
    if len(names) != len(set(names)):
        return False, "duplicate cell.names in native prediction"

    # CopyKAT writes prediction.txt before the heatmap. Preserve it byte-for-byte
    # as the standardized TSV expected by notebook 14 / the manifest.
    shutil.copyfile(native_pred, expected)

    if not valid_prediction(expected):
        expected.unlink(missing_ok=True)
        return False, "standardized prediction failed validation"

    batch_id = row["batch_id"]
    info = Path(row["batch_dir"]) / f"{batch_id}_run_info.tsv"
    with info.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
        writer.writerow([
            "batch_id", "status", "native_prediction", "native_bin_by_cell",
            "standard_prediction", "prediction_rows"
        ])
        writer.writerow([
            batch_id, "completed_step9_recovered_after_step10_failure",
            str(native_pred), str(native_bin), str(expected), len(rows)
        ])

    return True, f"{len(rows)} prediction rows"


def load_manifest():
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)
    with MANIFEST.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    if len(rows) != 176:
        raise RuntimeError(f"Expected 176 batches, found {len(rows)}")
    return rows


def recovery_pass(rows):
    recovered = []
    for row in rows:
        ok, detail = recover_one(row)
        if ok:
            recovered.append((row["batch_id"], detail))
    return recovered


def count_complete(rows):
    return sum(valid_prediction(Path(r["expected_prediction"])) for r in rows)


def main():
    rows = load_manifest()

    if not INNER_RUNNER.exists():
        raise FileNotFoundError(
            f"Expected existing 2-worker runner here:\n{INNER_RUNNER}"
        )

    print("=" * 88)
    print("COPYKAT 2-WORKER ORCHESTRATOR WITH STEP-9 RECOVERY")
    print("=" * 88)
    print("Inner runner:", INNER_RUNNER)
    print("Manifest:", MANIFEST)

    for cycle in range(1, MAX_RESTARTS + 1):
        recovered = recovery_pass(rows)
        for batch_id, detail in recovered:
            print(f"[RECOVERED] {batch_id}: {detail}")

        complete = count_complete(rows)
        print(f"[STATUS] valid standardized predictions: {complete} / 176")

        if complete == 176:
            print("[DONE] All 176 CopyKAT prediction TSVs are valid.")
            return 0

        print(f"[RUN CYCLE {cycle}] launching existing 2-worker runner...")
        proc = subprocess.run(
            [sys.executable, str(INNER_RUNNER)],
            cwd=str(CODE_DIR),
            check=False,
        )

        # Always attempt a recovery pass after the runner exits. This catches
        # std::bad_alloc or other failures occurring only after CopyKAT Step 9.
        recovered_after = recovery_pass(rows)
        for batch_id, detail in recovered_after:
            print(f"[RECOVERED AFTER RUN] {batch_id}: {detail}")

        complete_after = count_complete(rows)
        print(f"[STATUS] valid standardized predictions: {complete_after} / 176")

        if complete_after == 176:
            print("[DONE] All 176 CopyKAT prediction TSVs are valid.")
            return 0

        if proc.returncode == 0:
            print("[STOP] Inner runner returned 0 but 176 valid predictions are not present.")
            return 2

        if not recovered_after:
            print("[STOP] Runner failed and no new Step-9 output was recoverable.")
            print("This is a true failure before/within scientific inference, not just the heatmap.")
            return proc.returncode or 1

        print("[RESUME] Failure was recoverable from Step-9 outputs; restarting pending batches.\n")

    print("[STOP] Maximum restart cycles reached.")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
