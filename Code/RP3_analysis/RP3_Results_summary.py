import numpy as np
import pandas as pd
import os

# 1) load MASTER file
df = pd.read_csv('../data/microprotein_master.csv', low_memory=False)

# === Filter for Salk microproteins with evidence ===
salk_microproteins = df[
    (df['Database'].isin(['Salk', 'TrEMBL'])) &
    (df['protein_class_length'] == 'Microprotein') &
    (
        (df['total_unique_spectral_counts'] > 0) )
].copy()

print(f"Salk microproteins with evidence: {len(salk_microproteins):,}")

# === Extract relevant columns ===
summary_salk = salk_microproteins[[
    'sequence',
    'CLICK_UCSC',
    'RP3_Default',
    'RP3_MM_Amb',
    'RP3_Amb',
    'RP3_MM',
    'RiboCode',
    'Database',
    'gene_symbol',
    'protein_length',
    'start_codon',
    'smorf_type'
]]

outdir = '../../Results/RP3'
os.makedirs(outdir, exist_ok=True)

# === Optional: save combined output ===
summary_salk.to_csv(os.path.join(outdir, 'RP3_Results_summary.csv'), index=False)

# === Preview ===
print(summary_salk.head())

# Output to supplementary
outdir_supplement = '/Users/brendanmiller/Library/CloudStorage/Box-Box/brendan_alan_shared_folder/AD_paper/supplementary'
summary_salk.to_csv(os.path.join(outdir_supplement, 'Table5_RP3_Results_summary.csv'), index=False)
