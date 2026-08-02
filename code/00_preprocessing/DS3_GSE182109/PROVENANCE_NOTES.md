# DS3 provenance and implementation notes

## Removed stale content

The uploaded raw-build notebook contained four exploratory cells for a
different mouse dataset (`GSE241037`). Those cells were unrelated to
GSE182109 and are excluded.

## Raw-build logic retained

The valid GSE182109 cell showed that 44 sample prefixes were read with
`scanpy.read_10x_mtx`, gene symbols were made unique, cell barcodes were
suffixed with the sample prefix, and samples were concatenated with an outer
gene join. The cleaned notebook preserves that behavior while validating all
10x triplets and consolidating feature metadata across the outer union.

## QC logic retained

The cleaned QC notebook preserves the exact cell thresholds, the final
45,000-count ceiling, and the minimum-10-cell gene filter that produced
218,735 cells and 30,284 genes.

## Doublet interpretation

The uploaded notebook also created a 215,808-cell derivative after removing
2,927 predicted doublets. That derivative was not used by the reported main
pipeline: the integrated total of 351,427 cells requires all 218,735 DS3
post-QC cells. Therefore, the cleaned notebook retains Scrublet calls as
diagnostic metadata and does not export the filtered derivative as the main
analysis input.
