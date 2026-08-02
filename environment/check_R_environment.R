# R environment used by the CopyKAT stage
# R 4.5.2
# CopyKAT 1.1.0
# Matrix 1.7-5
# dplyr 1.2.1
# data.table 1.18.2.1

required <- c("Matrix", "dplyr", "data.table")
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) {
  install.packages(missing, repos = "https://cloud.r-project.org")
}
if (!requireNamespace("copykat", quietly = TRUE)) {
  stop("Install CopyKAT 1.1.0 before running the generated microbatch scripts.")
}
cat("R:", as.character(getRversion()), "\n")
cat("CopyKAT:", as.character(packageVersion("copykat")), "\n")
