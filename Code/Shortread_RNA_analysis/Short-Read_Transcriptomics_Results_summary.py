import pandas as pd
import os

# === 1. Load MASTER file ===
df = pd.read_csv('../data/microprotein_master.csv', low_memory=False)

# === 2. Keep only microproteins (from all databases) ===
df = df[df['protein_class_length'] == 'Microprotein'].copy()

# === 3. Separate processing for Salk/TrEMBL vs Swiss-Prot ===
# Process Salk and TrEMBL microproteins
salk_trembl_df = df[df['Database'].isin(['Salk', 'TrEMBL'])].copy()
salk_trembl_df.loc[salk_trembl_df['Database'] == 'TrEMBL', 'smorf_type'] = 'TrEMBL'
salk_trembl_df.loc[salk_trembl_df['Database'] == 'TrEMBL', 'genomic_coordinates'] = salk_trembl_df['gene_id']
salk_trembl_df.loc[salk_trembl_df['Database'] == 'TrEMBL', 'gene_name'] = salk_trembl_df['gene_id']

# === 4. Define MS and Ribo+SAM masks for Salk/TrEMBL ===
salk_trembl_df['has_MS'] = salk_trembl_df['total_unique_spectral_counts'] > 0
salk_trembl_df['has_RiboSAM'] = (
    (salk_trembl_df['RiboCode'] == True) &
    (salk_trembl_df['shortstop_label'].isin(['SAM-Secreted', 'SAM-Intracellular'])) &
    (~salk_trembl_df['smorf_type'].isin(['oORF', 'isoORF']))
)

# === 5. Keep rows with either MS or RiboSAM for Salk/TrEMBL ===
salk_trembl_df = salk_trembl_df[salk_trembl_df['has_MS'] | salk_trembl_df['has_RiboSAM']].copy()

# === 6. Prioritize MS over RiboSAM by sorting then dropping duplicates ===
# Sort so MS rows come first for each sequence
salk_trembl_df = salk_trembl_df.sort_values(by='has_MS', ascending=False)
salk_trembl_df = salk_trembl_df.drop_duplicates(subset='sequence')

# === 7. Set annotation label based on which evidence is present ===
salk_trembl_df['Annotation Status'] = salk_trembl_df['has_MS'].map({True: 'MS', False: 'RiboCode_SAM'})

# === Extract relevant columns from Salk/TrEMBL ===
summary_salk = salk_trembl_df[[
    'sequence',
    'CLICK_UCSC',
    'rosmapRNA_baseMean',
	'rosmapRNA_log2FoldChange',
	'rosmapRNA_stat',
	'rosmapRNA_pvalue',
	'rosmapRNA_padj',
	'rosmapRNA_non_smorf_hit',
	'rosmapRNA_body',
	'ROSMAP_BulkRNAseq_CPM',
	'ROSMAP_BulkRNAseq_CPM_Zscore',
    'Database',
    'gene_symbol',
    'protein_length',
    'start_codon',
    'smorf_type',
    'total_razor_spectral_counts',
    'total_unique_spectral_counts'
]]

# === Extract Swiss-Prot microproteins from original df ===
non_salk = df[df['Database'] == 'Swiss-Prot']

summary_non_salk = non_salk[[
    'sequence',
    'CLICK_UCSC',
    'rosmapRNA_baseMean',
    'rosmapRNA_log2FoldChange',
    'rosmapRNA_stat',
    'rosmapRNA_pvalue',
    'rosmapRNA_padj',
    'rosmapRNA_non_smorf_hit',
    'rosmapRNA_body',
    'ROSMAP_BulkRNAseq_CPM',
    'ROSMAP_BulkRNAseq_CPM_Zscore',
    'Database',
    'gene_symbol',
    'protein_length',
    'start_codon',
    'smorf_type',
    'total_razor_spectral_counts',
    'total_unique_spectral_counts'
]]

# === Combine Salk + non-Salk microproteins ===
summary_all = pd.concat([summary_salk, summary_non_salk], ignore_index=True)

# === Create output directories ===
outdir = '../../Results/Transcriptomics'
os.makedirs(outdir, exist_ok=True)

outdir_supplement = '../../supplementary'
os.makedirs(outdir_supplement, exist_ok=True)

# === Save output files ===
summary_all.to_csv(os.path.join(outdir, 'Short-Read_Transcriptomics_Results_summary.csv'), index=False)
summary_salk.to_csv(os.path.join(outdir_supplement, 'Table6a_Noncanonical_Short-Read_Transcriptomics_Results_summary.csv'), index=False)
summary_non_salk.to_csv(os.path.join(outdir_supplement, 'Table6b_SwissProt_Short-Read_Transcriptomics_Results_summary.csv'), index=False)

# === Preview ===
print("Short-Read Transcriptomics Results Summary:")
print(f"Noncanonical (Salk/TrEMBL) microproteins: {len(summary_salk)}")
print(f"Swiss-Prot microproteins: {len(summary_non_salk)}")
print(f"Total microproteins: {len(summary_all)}")
print("\nFirst few rows of combined data:")
print(summary_all.head())