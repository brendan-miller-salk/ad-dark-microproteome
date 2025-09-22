# Atlas of human brain microproteins with and without Alzheimer’s disease

## Overview

This repository includes the sequences, genomic coordinates, abundance data, and all code used in our manuscript. It covers:

- smORF annotation and classification
- Ribosome profiling evidence (RP3)
- Mass spectrometry evidence (TMT-MS)
- Peptide analysis in AD (TMT-MS)
- Transcriptomic analysis in AD (RNA-seq)
- Single-cell expression patterns (scRNA-seq)

## Reproducing Results

To reproduce the summary output files from raw and protected data:

1. Clone the repository
2. Run the setup script: `bash setup_environment.sh`
3. Execute the analysis pipeline: `bash run_all_analyses.sh --mode=run`

## Data Availability

Raw data files are excluded from this repository due to size constraints. 
See `DATA_AVAILABILITY.md` for download instructions and data access information.

## Requirements

See `requirements.txt` and `environment.yml` for dependencies.

## Contact

For questions or issues, contact: brmiller@salk.edu
