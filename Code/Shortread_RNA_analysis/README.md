# Short-read RNA Analysis

This module processes short-read RNA sequencing data for differential expression analysis.

## Overview
- **Input**: RNA-seq count matrices, created using FeatureCount on aligned BAM files accessed through Synapse
- **Output**: Differential expression results and statistics
- **Main Script**: `Short-Read_Transcriptomics_Results_summary.py`

## Analysis Steps

### 1. Data Processing (`Shortread_deseq_processing_scripts/`)
1. **`RNA_differential_expression.R`** - Comprehensive DESeq2 analysis including:
   - Data loading and preprocessing
   - Metadata integration
   - Differential expression testing
   - Gene annotation

### 2. Results Summary
- **`Short-Read_Transcriptomics_Results_summary.py`** - Generates final summary tables

## Usage

### Run Individual Components:
```bash
# Differential expression analysis
cd Shortread_deseq_processing_scripts/
Rscript RNA_differential_expression.R

# Generate summary
cd ..
python Short-Read_Transcriptomics_Results_summary.py
```

## Dependencies
- R: DESeq2, dplyr, tibble, plotly, biomaRt, org.Hs.eg.db, AnnotationDbi
- Python: pandas, numpy

## Input Files Required
- Combined count matrices (hg38 and hg19)
- Synapse RNA-seq metadata
- ROSMAP clinical metadata

## Outputs
- Differential expression results
- Normalized expression data
- Statistical summaries
