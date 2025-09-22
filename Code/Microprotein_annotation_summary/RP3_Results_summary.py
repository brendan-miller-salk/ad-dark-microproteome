import numpy as np
import pandas as pd
import os

# 1) load MASTER
df = pd.read_csv('../data/microprotein_master.csv', low_memory=False)


# === Filter for Salk microproteins with evidence ===
df = df[
    (df['Database'].isin(['Salk', 'TrEMBL'])) &
    (df['protein_class_length'] == 'Microprotein')
].copy()
df.loc[df['Database'] == 'TrEMBL', 'smorf_type'] = 'TrEMBL'
df.loc[df['Database'] == 'TrEMBL', 'genomic_coordinates'] = df['gene_id']
df.loc[df['Database'] == 'TrEMBL', 'gene_name'] = df['gene_id']


# === 3. Define MS and Ribo+SAM masks ===
df['has_MS'] = df['total_unique_spectral_counts'] > 0
df['has_RiboSAM'] = (
    (df['RiboCode'] == True) &
    (df['shortstop_label'].isin(['SAM-Secreted', 'SAM-Intracellular'])) &
    (~df['smorf_type'].isin(['oORF', 'isoORF']))
)

# === 4. Keep rows with either MS or RiboSAM ===
df = df[df['has_MS'] | df['has_RiboSAM']].copy()

# === 5. Prioritize MS over RiboSAM by sorting then dropping duplicates ===
df = df.sort_values(by='has_MS', ascending=False)
df = df.drop_duplicates(subset='sequence')

# === Extract relevant columns ===
summary_salk = df[[
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

outdir = '/Users/brendanmiller/Library/CloudStorage/Box-Box/brendan_alan_shared_folder/AD_paper/Github/Results/RP3'

# === Optional: save combined output ===
summary_salk.to_csv(os.path.join(outdir, 'RP3_Results_summary.csv'), index=False)

# === Preview ===
print(summary_salk.head())

outdir_supplement = '/Users/brendanmiller/Library/CloudStorage/Box-Box/brendan_alan_shared_folder/AD_paper/supplementary'
summary_salk.to_csv(os.path.join(outdir_supplement, 'Table5_RP3_Results_summary.csv'), index=False)