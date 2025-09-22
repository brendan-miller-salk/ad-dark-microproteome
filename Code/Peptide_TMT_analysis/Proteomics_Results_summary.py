import pandas as pd
import os

# === 1. Load MASTER file ===
df = pd.read_csv('../data/microprotein_master.csv', low_memory=False)

# === 2. Keep only entries for microproteins ===
df_noncanonical = df[
    (df['Database'].isin(['Salk', 'TrEMBL'])) &
    (df['protein_class_length'] == 'Microprotein')
].copy()

df_noncanonical.loc[df_noncanonical['Database'] == 'TrEMBL', 'smorf_type'] = 'TrEMBL'
df_noncanonical.loc[df_noncanonical['Database'] == 'TrEMBL', 'genomic_coordinates'] = df_noncanonical['gene_id']
df_noncanonical.loc[df_noncanonical['Database'] == 'TrEMBL', 'gene_name'] = df_noncanonical['gene_id']

# === 3. Define MS and Ribo+SAM masks ===
df_noncanonical['has_MS'] = df_noncanonical['total_unique_spectral_counts'] > 0
df_noncanonical['has_RiboSAM'] = (
    (df_noncanonical['RiboCode'] == True) &
    (df_noncanonical['shortstop_label'].isin(['SAM-Secreted', 'SAM-Intracellular'])) &
    (~df_noncanonical['smorf_type'].isin(['oORF', 'isoORF']))
)

# === 4. Keep rows with either MS or RiboSAM ===
#df_noncanonical = df_noncanonical[df_noncanonical['has_MS'] | df_noncanonical['has_RiboSAM']].copy()
df_noncanonical = df_noncanonical[df_noncanonical['has_MS']].copy()


# === 5. Prioritize MS over RiboSAM by sorting then dropping duplicates ===
# Sort so MS rows come first for each sequence
df_noncanonical = df_noncanonical.sort_values(by='has_MS', ascending=False)
df_noncanonical = df_noncanonical.drop_duplicates(subset='sequence')

# === 6. Set annotation label based on which evidence is present ===
df_noncanonical['Annotation Status'] = df_noncanonical['has_MS'].map({True: 'MS', False: 'RiboCode_SAM'})

print(f"Counts by Annotation Status:")
print(df_noncanonical['Annotation Status'].value_counts())

# === Extract relevant columns ===
summary_salk = df_noncanonical[[
    'sequence',
    'CLICK_UCSC',
    'TMT_log2fc',
    'TMT_pvalue',
    'TMT_qvalue',
    'Database',
    'protein_class_length',
    'gene_symbol',
    'protein_length',
    'start_codon',
    'smorf_type',
    'total_razor_spectral_counts',
    'total_unique_spectral_counts'
]]

# === Extract non-Salk microproteins (e.g., Swiss-Prot) ===
non_salk = df[
    (df['Database'] == 'Swiss-Prot') &
    (df['protein_class_length'] == 'Microprotein') &
    (df['MS_razor_evidence'] == True)
]

summary_non_salk = non_salk[[
    'sequence',
    'CLICK_UCSC',
    'TMT_log2fc',
    'TMT_pvalue',
    'TMT_qvalue',
    'Database',
    'protein_class_length',
    'gene_symbol',
    'protein_length',
    'start_codon',
    'smorf_type',
    'total_razor_spectral_counts',
    'total_unique_spectral_counts'
]]

# === Combine Salk + non-Salk microproteins ===
summary_all = pd.concat([summary_salk, summary_non_salk], ignore_index=True)

outdir = '/Users/brendanmiller/Library/CloudStorage/Box-Box/brendan_alan_shared_folder/AD_paper/Github/Results/Proteomics'

# === Optional: save combined output ===
summary_all.to_csv(os.path.join(outdir, 'Proteomics_Results_summary.csv'), index=False)

# === Preview ===
print(summary_all.head())

outdir_supplement = '/Users/brendanmiller/Library/CloudStorage/Box-Box/brendan_alan_shared_folder/AD_paper/supplementary'
summary_salk.to_csv(os.path.join(outdir_supplement, 'Table4a_Noncanonical_Proteomics_Results_summary.csv'), index=False)

outdir_supplement = '/Users/brendanmiller/Library/CloudStorage/Box-Box/brendan_alan_shared_folder/AD_paper/supplementary'
summary_non_salk.to_csv(os.path.join(outdir_supplement, 'Table4b_SwissProt_Proteomics_Results_summary.csv'), index=False)