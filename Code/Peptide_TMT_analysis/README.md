# TMT Proteomics Analysis

This module processes TMT (Tandem Mass Tag) proteomics data from FragPipe and performs quantitative analysis.

## Overview
- **Input**: FragPipe TMT results from multiple rounds
- **Output**: Quantified protein abundances and statistical comparisons
- **Main Script**: `Proteomics_Results_summary.py`

## Analysis Steps

### 1. Data Processing (`fragpipe_results_processing_scripts/`)

#### Protein ID Processing:
1. **`process_proteinID_from_TMT_round1.py`** - Process protein identifications from TMT round 1
2. **`process_proteinID_frmo_TMT_round2.py`** - Process protein identifications from TMT round 2
3. **`find_unique_tryptic_peptides.py`** - Identify unique tryptic peptides

#### Matrix Generation and Correction:
4. **`generate_raw_TMT_intensity_matrix_across_batches.R`** - Generate raw intensity matrices
5. **`TMT_regressed_corrrected_matrix.R`** - Apply batch correction and normalization

#### Statistical Analysis (TAMPOR):
6. **`TAMPOR_round1.R`** - TMT analysis for round 1
7. **`TAMPOR_round2.R`** - TMT analysis for round 2  
8. **`TAMPOR_combined_rounds.R`** - Combined analysis across rounds
9. **`TMT_ANOVA.R`** - ANOVA testing across conditions

### 2. Results Summary
- **`Proteomics_Results_summary.py`** - Generates final summary tables and statistics

## Usage

### Run All Processing Steps:
```bash
cd fragpipe_results_processing_scripts/

# Process protein IDs
python process_proteinID_from_TMT_round1.py
python process_proteinID_frmo_TMT_round2.py
python find_unique_tryptic_peptides.py

# Generate and correct matrices
Rscript generate_raw_TMT_intensity_matrix_across_batches.R
Rscript TMT_regressed_corrrected_matrix.R

# Statistical analysis
Rscript TAMPOR_round1.R
Rscript TAMPOR_round2.R
Rscript TAMPOR_combined_rounds.R
Rscript TAMPOR_microproteins.R
Rscript TMT_ANOVA.R

# Generate final summary
cd ..
python Proteomics_Results_summary.py
```

## Dependencies
- Python: pandas, numpy, os
- R: Various statistical packages (dplyr, ggplot2, etc.)
- FragPipe output files

## Outputs
- Processed protein abundance matrices
- Statistical test results
- Microprotein quantification summaries
- Quality control metrics
