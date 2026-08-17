#!/usr/bin/env python
from pathlib import Path
import os
import subprocess
import sys

RSCRIPT = Path(r"C:\Program Files\R\R-4.6.1\bin\Rscript.exe")

BATCH_DIR = Path(
    r"G:\Repository\glioma-cnv-single-cell-atlas\data\interim\integrated\CNV_inputs\CopyKAT_HVG8000_r0_6\batchwise_micro_all_cells\copykat_microbatch_0001"
)

R_SCRIPT = BATCH_DIR / "run_copykat_microbatch_0001.R"
PREDICTION = BATCH_DIR / "copykat_microbatch_0001_prediction.tsv"
LOG = BATCH_DIR / "copykat_microbatch_0001_run.log"

TIMEOUT_SECONDS = 8 * 3600

if not RSCRIPT.exists():
    raise FileNotFoundError(RSCRIPT)

if not R_SCRIPT.exists():
    raise FileNotFoundError(R_SCRIPT)


def sanitized_environment():
    env = os.environ.copy()

    for key in [
        "CONDA_PREFIX",
        "CONDA_DEFAULT_ENV",
        "CONDA_PROMPT_MODIFIER",
        "CONDA_EXE",
        "CONDA_PYTHON_EXE",
        "_CE_CONDA",
        "_CE_M",
        "PYTHONHOME",
        "PYTHONPATH",
        "R_HOME",
        "MKL_THREADING_LAYER",
        "MKL_SERVICE_FORCE_INTEL",
        "KMP_DUPLICATE_LIB_OK",
    ]:
        env.pop(key, None)

    parts = [
        part
        for part in env.get("PATH", "").split(os.pathsep)
        if part
    ]

    blocked = [
        r"\.conda\envs",
        r"\anaconda",
        r"\miniconda",
        r"\conda",
    ]

    clean = []

    for part in parts:
        normalized = part.lower().replace("/", "\\")

        if any(
            token.lower() in normalized
            for token in blocked
        ):
            continue

        clean.append(part)

    final = [
        str(RSCRIPT.parent),
        r"C:\Windows\System32",
        r"C:\Windows",
        *clean,
    ]

    unique = []
    seen = set()

    for part in final:
        key = part.lower()

        if key not in seen:
            seen.add(key)
            unique.append(part)

    env["PATH"] = os.pathsep.join(unique)

    user_lib = Path(
        r"C:\Users\AmirSilco\AppData\Local\R\win-library\4.6"
    )

    if user_lib.exists():
        env["R_LIBS_USER"] = str(user_lib)

    return env


env = sanitized_environment()

print("=" * 80)
print("COPYKAT END-TO-END TEST — BATCH 0001")
print("=" * 80)

print("Rscript:", RSCRIPT)
print("R script:", R_SCRIPT)
print("Prediction:", PREDICTION)
print("Log:", LOG)
print("R_LIBS_USER:", env.get("R_LIBS_USER", "<R default>"))

bridge = subprocess.run(
    [
        str(RSCRIPT),
        "--vanilla",
        "-e",
        (
            'cat("COPYKAT_INSTALLED=",'
            'requireNamespace("copykat",quietly=TRUE),"\\n",sep="");'
            'if(requireNamespace("copykat",quietly=TRUE))'
            'cat("COPYKAT_VERSION=",'
            'as.character(packageVersion("copykat")),"\\n",sep="")'
        ),
    ],
    env=env,
    capture_output=True,
    text=True,
    timeout=120,
    check=False,
)

print("\n[BRIDGE TEST]")
print(bridge.stdout.strip())

if bridge.returncode != 0:
    print(bridge.stderr)
    raise RuntimeError(
        f"Bridge test failed with return code {bridge.returncode}."
    )

if "COPYKAT_INSTALLED=TRUE" not in bridge.stdout:
    raise RuntimeError(
        "CopyKAT is not visible to clean Rscript."
    )

if PREDICTION.exists():
    print("\n[SKIP] Batch 0001 prediction already exists.")
    print(PREDICTION)
    sys.exit(0)

print("\n[RUN] Starting CopyKAT batch 0001.")
print("This may take substantial time.")

with LOG.open(
    "w",
    encoding="utf-8",
    errors="replace",
) as log_handle:

    try:
        completed = subprocess.run(
            [
                str(RSCRIPT),
                "--vanilla",
                str(R_SCRIPT),
            ],
            cwd=str(BATCH_DIR),
            env=env,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )

        status = int(
            completed.returncode
        )

    except subprocess.TimeoutExpired:
        status = 124

        log_handle.write(
            "\n[TIMEOUT] Batch 0001 exceeded 8 hours.\n"
        )

print("\nRETURN CODE:", status)

if status != 0:
    print("\n[FAILED] Inspect log:")
    print(LOG)
    sys.exit(status)

if not PREDICTION.exists():
    print("\n[FAILED] Rscript returned 0 but prediction is missing.")
    print("Inspect log:")
    print(LOG)
    sys.exit(126)

print("\n" + "=" * 80)
print("BATCH 0001 PASSED")
print("=" * 80)
print("Prediction:")
print(PREDICTION)
print("Size (bytes):", PREDICTION.stat().st_size)
print("Log:")
print(LOG)
