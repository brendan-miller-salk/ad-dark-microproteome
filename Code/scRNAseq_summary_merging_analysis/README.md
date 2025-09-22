# Single-cell RNA-seq Analysis

This module processes and integrates single-cell RNA sequencing data for cell-type specific analysis.

## Overview
- **Input**: Single-cell RNA-seq data and metadata
- **Output**: Cell-type enrichment results and integrated analyses
- **Main Script**: `scRNAseq_summary.R`

## Analysis Steps

### 1. Data Integration and Analysis
- **`scRNAseq_summary.R`** - Integrates scRNA-seq data with microprotein annotations

## Usage

```bash
Rscript scRNAseq_summary.R
```

## Dependencies
- R: dplyr, ggplot2, and other scRNA-seq analysis packages

## Outputs
- Cell-type specific expression profiles
- Enrichment analysis results
- Integrated summary tables
