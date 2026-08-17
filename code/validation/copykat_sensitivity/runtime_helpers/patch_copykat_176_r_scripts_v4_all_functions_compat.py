from pathlib import Path
import shutil

BASE_DIR = Path(
    r"G:\Repository\glioma-cnv-single-cell-atlas\data\interim\integrated\CNV_inputs\CopyKAT_HVG8000_r0_6\batchwise_micro_all_cells"
)

scripts = sorted(
    BASE_DIR.glob("copykat_microbatch_*/run_copykat_microbatch_*.R")
)

if len(scripts) != 176:
    raise RuntimeError(
        f"Expected 176 R scripts, found {len(scripts)}"
    )

OLD = 'copykat_compat_env <- new.env(\n  parent = asNamespace("copykat")\n)\n\nfor (nm in ls(copykat_data_env, all.names = TRUE)) {\n  assign(\n    nm,\n    get(nm, envir = copykat_data_env, inherits = FALSE),\n    envir = copykat_compat_env\n  )\n}\n\nannotate_hg20_compat <- copykat::annotateGenes.hg20\nenvironment(annotate_hg20_compat) <- copykat_compat_env\nassign(\n  "annotateGenes.hg20",\n  annotate_hg20_compat,\n  envir = copykat_compat_env\n)\n\ncopykat_compat <- copykat::copykat\nenvironment(copykat_compat) <- copykat_compat_env'
NEW = 'copykat_ns <- asNamespace("copykat")\n\ncopykat_compat_env <- new.env(\n  parent = copykat_ns\n)\n\nfor (nm in ls(copykat_data_env, all.names = TRUE)) {\n  assign(\n    nm,\n    get(nm, envir = copykat_data_env, inherits = FALSE),\n    envir = copykat_compat_env\n  )\n}\n\ncopykat_function_names <- ls(\n  copykat_ns,\n  all.names = TRUE\n)\n\nn_functions_copied <- 0L\n\nfor (nm in copykat_function_names) {\n  obj <- get(\n    nm,\n    envir = copykat_ns,\n    inherits = FALSE\n  )\n\n  if (\n    is.function(obj)\n    && !is.primitive(obj)\n  ) {\n    fn <- obj\n    environment(fn) <- copykat_compat_env\n\n    assign(\n      nm,\n      fn,\n      envir = copykat_compat_env\n    )\n\n    n_functions_copied <- n_functions_copied + 1L\n  }\n}\n\nmessage(\n  "[COPYKAT COMPAT] functions retargeted=",\n  n_functions_copied\n)\n\nrequired_compat_functions <- c(\n  "copykat",\n  "annotateGenes.hg20",\n  "convert.all.bins.hg20"\n)\n\nmissing_compat_functions <- required_compat_functions[\n  !vapply(\n    required_compat_functions,\n    exists,\n    logical(1),\n    envir = copykat_compat_env,\n    inherits = FALSE\n  )\n]\n\nif (length(missing_compat_functions) > 0) {\n  stop(\n    "CopyKAT compatibility environment is missing functions: ",\n    paste(missing_compat_functions, collapse = ", ")\n  )\n}\n\ncopykat_compat <- get(\n  "copykat",\n  envir = copykat_compat_env,\n  inherits = FALSE\n)'

changed = 0
already = 0

for script in scripts:
    text = script.read_text(encoding="utf-8")

    if "[COPYKAT COMPAT] functions retargeted=" in text:
        already += 1
        continue

    if OLD not in text:
        raise RuntimeError(
            f"v3 compatibility block not found in {script}"
        )

    backup = script.with_suffix(".R.pre_v4_backup")

    if not backup.exists():
        shutil.copyfile(script, backup)

    text = text.replace(OLD, NEW, 1)

    script.write_text(
        text,
        encoding="utf-8",
    )

    changed += 1

print("=" * 80)
print("COPYKAT V4 PATCH COMPLETE")
print("=" * 80)
print("Scripts found:", len(scripts))
print("Patched now:", changed)
print("Already v4:", already)

batch1 = (
    BASE_DIR
    / "copykat_microbatch_0001"
    / "run_copykat_microbatch_0001.R"
)

check = batch1.read_text(encoding="utf-8")

required = [
    "[COPYKAT COMPAT] functions retargeted=",
    '"convert.all.bins.hg20"',
    "copykat_compat <- get(",
    "[NORM anchors requested]",
    "[NORM anchors matched]",
]

missing = [
    marker
    for marker in required
    if marker not in check
]

if missing:
    raise RuntimeError(
        f"Batch 0001 v4 validation failed: {missing}"
    )

print("Batch 0001 v4 validation: PASS")
print("Backups: *.R.pre_v4_backup")
