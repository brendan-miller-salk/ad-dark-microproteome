# Long-read RNA Analysis

This module processes long-read RNA sequencing data using ESPRESSO and performs differential expression analysis.

## Overview
- **Input**: Raw ESPRESSO abundance files
- **Output**: CPM-normalized data and differential expression results
- **Main Script**: `Long-Read_Transcriptomics_Results_summary.py`

## Analysis Steps

### 1. Data Processing (`ESPRESSO_data_processing_scripts/`)
1. **`convert_ESPERSSO_to_CPM.sh`** - Shell script wrapper for CPM conversion
2. **`convert_ESPRESSO_to_CPM_and_filter.py`** - Converts raw ESPRESSO counts to CPM and applies filtering
3. **`deseq_brain_espresso.r`** - Performs differential expression analysis using DESeq2

### 2. Results Summary
- **`Long-Read_Transcriptomics_Results_summary.py`** - Generates final summary tables and statistics

## Usage

### Run Individual Components:
```bash
# Data processing
cd ESPRESSO_data_processing_scripts/
bash convert_ESPERSSO_to_CPM.sh
Rscript deseq_brain_espresso.r

# Generate summary
cd ..
python Long-Read_Transcriptomics_Results_summary.py
```

### Run All Steps:
```bash
# From repository root
bash run_all_analyses.sh
```

## Dependencies
- Python: pandas, numpy, argparse
- R: DESeq2, dplyr, biomaRt
- ESPRESSO output files

## Outputs
- CPM-normalized expression matrices
- Differential expression results
- Summary statistics and tables
