#!/usr/bin/env python
from pathlib import Path
import csv, os, re, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

MANIFEST = Path(r"G:\Repository\glioma-cnv-single-cell-atlas\metadata\copykat_microbatch_input_manifest_HVG8000_r0_6.tsv")
MAX_WORKERS = 2
TIMEOUT_SECONDS = 8 * 3600
START_STAGGER_SECONDS = 8


def find_rscript():
    candidates = []
    if os.environ.get("RSCRIPT_BIN"):
        candidates.append(Path(os.environ["RSCRIPT_BIN"]))
    if shutil.which("Rscript"):
        candidates.append(Path(shutil.which("Rscript")))
    if os.name == "nt":
        root = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "R"
        if root.exists():
            for d in sorted(root.glob("R-*"), reverse=True):
                candidates += [d / "bin" / "Rscript.exe", d / "bin" / "x64" / "Rscript.exe"]
    seen = set()
    for p in candidates:
        try:
            p = p.expanduser().resolve()
        except Exception:
            continue
        k = str(p).lower()
        if k in seen:
            continue
        seen.add(k)
        if p.exists():
            return p
    raise RuntimeError("Rscript not found. Set RSCRIPT_BIN to the full Rscript.exe path.")


def clean_r_env(rscript):
    env = os.environ.copy()
    for key in [
        "CONDA_PREFIX", "CONDA_DEFAULT_ENV", "CONDA_PROMPT_MODIFIER",
        "CONDA_EXE", "CONDA_PYTHON_EXE", "_CE_CONDA", "_CE_M",
        "PYTHONHOME", "PYTHONPATH", "R_HOME", "MKL_THREADING_LAYER",
        "MKL_SERVICE_FORCE_INTEL", "KMP_DUPLICATE_LIB_OK",
    ]:
        env.pop(key, None)

    blocked = [r"\.conda\envs", r"\anaconda", r"\miniconda", r"\conda"]
    parts = []
    for part in env.get("PATH", "").split(os.pathsep):
        if not part:
            continue
        norm = part.lower().replace("/", "\\")
        if any(b.lower() in norm for b in blocked):
            continue
        parts.append(part)

    preferred = [str(Path(rscript).parent)]
    if os.name == "nt":
        preferred += [r"C:\Windows\System32", r"C:\Windows"]

    out, seen = [], set()
    for part in preferred + parts:
        k = part.lower()
        if k not in seen:
            seen.add(k)
            out.append(part)
    env["PATH"] = os.pathsep.join(out)

    if os.name == "nt":
        m = re.search(r"R-(\d+)\.(\d+)", str(rscript), flags=re.I)
        if m and env.get("LOCALAPPDATA"):
            lib = Path(env["LOCALAPPDATA"]) / "R" / "win-library" / f"{m.group(1)}.{m.group(2)}"
            if lib.exists():
                env["R_LIBS_USER"] = str(lib)
    return env


def bridge_test(rscript, env):
    code = (
        'cat("R_VERSION=",R.version.string,"\\n",sep="");'
        'cat("COPYKAT_INSTALLED=",requireNamespace("copykat",quietly=TRUE),"\\n",sep="");'
        'if(requireNamespace("copykat",quietly=TRUE))cat("COPYKAT_VERSION=",as.character(packageVersion("copykat")),"\\n",sep="")'
    )
    r = subprocess.run([str(rscript), "--vanilla", "-e", code], env=env,
                       capture_output=True, text=True, timeout=120, check=False)
    if r.returncode != 0 or "COPYKAT_INSTALLED=TRUE" not in r.stdout:
        raise RuntimeError(f"Clean R bridge failed. rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}")
    print(r.stdout.strip())


def load_rows():
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)
    with MANIFEST.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    if len(rows) != 176:
        raise RuntimeError(f"Expected 176 manifest rows, found {len(rows)}")
    return rows


def prediction_ok(row):
    p = Path(row["expected_prediction"])
    return p.exists() and p.stat().st_size > 0


def run_one(row, rscript, env):
    batch = row["batch_id"]
    batch_dir = Path(row["batch_dir"])
    pred = Path(row["expected_prediction"])
    r_script = Path(row["r_script"])
    log = batch_dir / f"{batch}_run.log"

    if prediction_ok(row):
        return {"batch": batch, "status": "SKIP", "rc": 0, "log": str(log)}
    if not r_script.exists():
        return {"batch": batch, "status": "FAIL", "rc": 127, "log": str(log), "error": f"Missing {r_script}"}

    batch_dir.mkdir(parents=True, exist_ok=True)
    start = time.time()
    with log.open("w", encoding="utf-8", errors="replace") as h:
        try:
            p = subprocess.run([str(rscript), "--vanilla", str(r_script)], cwd=str(batch_dir), env=env,
                               stdout=h, stderr=subprocess.STDOUT, timeout=TIMEOUT_SECONDS, check=False)
            rc = int(p.returncode)
        except subprocess.TimeoutExpired:
            rc = 124
            h.write("\n[TIMEOUT] Batch exceeded 8 hours.\n")
        except Exception as e:
            rc = 125
            h.write("\n[RUNNER ERROR] " + repr(e) + "\n")

    mins = (time.time() - start) / 60.0
    if rc != 0:
        return {"batch": batch, "status": "FAIL", "rc": rc, "mins": mins, "log": str(log)}
    if not pred.exists() or pred.stat().st_size == 0:
        return {"batch": batch, "status": "FAIL", "rc": 126, "mins": mins, "log": str(log), "error": "prediction TSV missing/empty"}
    return {"batch": batch, "status": "PASS", "rc": 0, "mins": mins, "log": str(log)}


def main():
    print("=" * 88)
    print("COPYKAT 2-WORKER MICRO-BATCH RUNNER")
    print("=" * 88)
    rscript = find_rscript()
    env = clean_r_env(rscript)
    print("Rscript:", rscript)
    print("Manifest:", MANIFEST)
    print("Workers:", MAX_WORKERS)
    print("R_LIBS_USER:", env.get("R_LIBS_USER", "<R default>"))
    print("\n[BRIDGE TEST]")
    bridge_test(rscript, env)

    rows = load_rows()
    complete = [r for r in rows if prediction_ok(r)]
    pending = [r for r in rows if not prediction_ok(r)]
    print("\nAlready complete:", len(complete))
    print("Pending:", len(pending))

    if not pending:
        print("[DONE] All 176 prediction TSVs already exist.")
        return 0

    print("\nAt most 2 independent batches will run at once; each R script remains n.cores=1.")
    failures, passed = [], 0
    next_i, active = 0, {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        while next_i < len(pending) and len(active) < MAX_WORKERS:
            row = pending[next_i]
            print("[START]", row["batch_id"])
            fut = ex.submit(run_one, row, rscript, env)
            active[fut] = row
            next_i += 1
            if START_STAGGER_SECONDS and len(active) < MAX_WORKERS and next_i < len(pending):
                time.sleep(START_STAGGER_SECONDS)

        while active:
            done, _ = wait(active.keys(), return_when=FIRST_COMPLETED)
            for fut in done:
                row = active.pop(fut)
                try:
                    res = fut.result()
                except Exception as e:
                    res = {"batch": row["batch_id"], "status": "FAIL", "rc": 125,
                           "log": str(Path(row["batch_dir"]) / f'{row["batch_id"]}_run.log'), "error": repr(e)}

                if res["status"] == "PASS":
                    passed += 1
                    print("[PASS]", res["batch"], f'{res.get("mins", float("nan")):.1f} min')
                elif res["status"] == "SKIP":
                    print("[SKIP]", res["batch"])
                else:
                    failures.append(res)
                    print("[FAIL]", res["batch"], "return_code=", res.get("rc"))
                    print("Log:", res.get("log"))
                    if res.get("error"):
                        print("Error:", res["error"])

            if failures:
                print("\n[STOP SCHEDULING] Failure detected. Any already-running batch will be allowed to finish.")
                continue

            while next_i < len(pending) and len(active) < MAX_WORKERS:
                row = pending[next_i]
                print("[START]", row["batch_id"])
                fut = ex.submit(run_one, row, rscript, env)
                active[fut] = row
                next_i += 1
                if START_STAGGER_SECONDS and len(active) < MAX_WORKERS and next_i < len(pending):
                    time.sleep(START_STAGGER_SECONDS)

    now = sum(1 for r in rows if prediction_ok(r))
    print("\n" + "=" * 88)
    print("RUN SUMMARY")
    print("=" * 88)
    print("Previously complete:", len(complete))
    print("Passed this run:", passed)
    print("Prediction TSVs now present:", now, "/ 176")

    if failures:
        print("Failures:", len(failures))
        print("First failed batch:", failures[0]["batch"])
        print("Log:", failures[0].get("log"))
        return 1
    if now != 176:
        print("[INCOMPLETE] No failure, but not all predictions are present.")
        return 2

    print("[DONE] All 176 CopyKAT prediction TSVs are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
