# RP3 (Ribosome Profiling) Analysis

This module processes ribosome profiling data using RiboCode to identify actively translated ORFs.

## Overview
- **Input**: RiboCode output files
- **Output**: Processed ORF classifications and statistics
- **Main Script**: `RP3_Results_summary.py`

## Analysis Steps

### 1. Data Processing
- **`RP3_Results_summary.py`** - Processes RiboCode results and generates summary statistics

## Usage

```bash
python RP3_Results_summary.py
```

## Dependencies
- Python: pandas, numpy, os

## Input Files Required
- RiboCode output files (`.bed`, `.gtf`, `.txt` formats)
- Mapping group files with RPKM values

## Outputs
- Processed ORF classifications
- Summary statistics
- Filtered mapping results
