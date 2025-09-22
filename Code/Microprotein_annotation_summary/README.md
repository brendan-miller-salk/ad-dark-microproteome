# smORF Annotation Analysis

This module provides comprehensive annotation of small Open Reading Frames (smORFs) using the Annotator pipeline.

## Overview
- **Input**: smORF GTF files and reference annotations
- **Output**: Classified and annotated microproteins
- **Main Pipeline**: `run_Annotator.sh`

## Analysis Steps

### 1. Annotation Pipeline (`Annotator/`)
- **`run_Annotator.sh`** - Main pipeline script that runs the full annotation workflow
- **`Annotator/`** - Modular annotation pipeline source code

### 2. Summary Scripts
1. **`Brain_Microproteins_Discovery_summary.py`** - Summarizes brain-specific microprotein discoveries
2. **`ShortStop_Microproteins_summary.py`** - Processes ShortStop pipeline results  
3. **`RP3_Results_summary.py`** - Additional RP3 analysis specific to annotations

## Usage

### Run Full Annotation Pipeline:
```bash
bash run_Annotator.sh
```

### Generate Individual Summaries:
```bash
python Brain_Microproteins_Discovery_summary.py
python ShortStop_Microproteins_summary.py
python RP3_Results_summary.py
```

## Dependencies
- Python: pandas, numpy, os
- bedtools (for genomic intersections)
- Annotator pipeline dependencies

## Input Files Required
- smORF GTF files
- Ensembl reference annotations
- Microprotein master database

## Outputs
- Annotated smORF classifications
- Summary tables and statistics
- BED/GTF files for downstream analysis
