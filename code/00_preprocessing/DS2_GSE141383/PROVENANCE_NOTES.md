# Provenance note

The first DS2 package assumed that the available inputs were per-sample h5ad
objects because the uploaded `Making-h5ad-GSE141383.ipynb` only loaded an h5ad
file and did not preserve its construction code.

Inspection of the extracted `GSE141383_RAW` directory established that the
actual starting inputs are nine files named `*.counts.txt.gz`. The corrected
00a notebook therefore replaces the reconstructed h5ad-to-h5ad merge with a
direct parser for those nine GEO count tables.

The original uploaded `Making-h5ad-GSE141383.ipynb` should not be published or
used in the final repository.
