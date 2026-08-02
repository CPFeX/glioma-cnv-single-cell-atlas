# DS4 provenance and implementation notes

## Raw merge

The cleaned build notebook preserves the source notebook's valid logic:
22 files matching `*_RawData.tsv.gz` are read as gene-by-cell tables,
transposed, converted to sparse matrices, and concatenated with an outer gene
join. The source notebook ignored normalized tables, and the cleaned version
does the same.

The cleaned version adds deterministic file discovery, the exact historical
sample set, count validation, collision-safe cell identifiers, audit tables,
and saved-file validation.

## QC

Unrelated imports and machine-specific working-directory changes were removed.
The source thresholds and both filtering stages were retained. The original
code created `adata.raw` and a full counts layer before filtering; the cleaned
notebook creates only the final counts layer after filtering to reduce memory
without changing retained cells or genes.

## Doublet interpretation

The Scrublet notebook added scores and calls to the 88,094-cell post-QC object
but did not remove predicted doublets. The cleaned version preserves this
diagnostic-only interpretation.
