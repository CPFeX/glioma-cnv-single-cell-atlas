# Canonical CopyKAT artifacts

These files define the paper-reproduction branch of the CopyKAT analysis.

The archived prediction bundle SHA256 is:

`7b3f8c2b87847fcbcf3dff54a37dc077782e465da662cfcb9288914b9b9610b3`

`copykat_microbatch_final_cell_calls_HVG8000_r0_6.tsv.gz` and
`copykat_canonical_manifest.tsv` are generated once from the historical
Notebook-14 final-cell-call TSV by:

```bash
python scripts/prepare_copykat_canonical_archive.py
```

The main Notebook 14 verifies the manifest and historical hard checkpoints
before writing any canonical downstream output.
