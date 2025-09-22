import pandas as pd
import os


# === 1. Load MASTER file ===
df = pd.read_csv('../data/microprotein_master.csv', low_memory=False)

# === 2. Keep only Salk microproteins ===
df = df[
    (df['Database'].isin(['Salk', 'TrEMBL'])) &
    (df['protein_class_length'] == 'Microprotein')
].copy()
df.loc[df['Database'] == 'TrEMBL', 'smorf_type'] = 'TrEMBL'
df.loc[df['Database'] == 'TrEMBL', 'genomic_coordinates'] = df['gene_id']
df.loc[df['Database'] == 'TrEMBL', 'gene_name'] = df['gene_id']

# === 3. Define MS and Ribo+SAM masks (now including DIA evidence) ===
# Include DIA evidence with Global.PG.Q.Value <= 0.01
df['has_MS'] = (
    (df['total_unique_spectral_counts'] > 0) |
    (~df['Global.PG.Q.Value'].isna() & (df['Global.PG.Q.Value'] <= 0.01))
)
df['has_RiboSAM'] = (
    (df['RiboCode'] == True) &
    (df['shortstop_label'].isin(['SAM-Secreted', 'SAM-Intracellular'])) &
    (~df['smorf_type'].isin(['oORF', 'isoORF']))
)

# === 4. Keep rows with either MS or RiboSAM ===
df = df[df['has_MS'] | df['has_RiboSAM']].copy()

# === 5. Prioritize MS over RiboSAM by sorting then dropping duplicates ===
# Sort so MS rows come first for each sequence
df = df.sort_values(by='has_MS', ascending=False)
df = df.drop_duplicates(subset='sequence')

# === 6. Set annotation label based on which evidence is present ===
df['Annotation Status'] = df['has_MS'].map({True: 'MS', False: 'RiboCode_SAM'})

# 6) select & rename summary columns
summary = df[[
    'sequence',
    'CLICK_UCSC',
    'genomic_coordinates',
    'smorf_type',
    'gene_name',
    'protein_length',
    'Annotation Status'
]].rename(columns={
    'genomic_coordinates': 'smORF Coordinates',
    'smorf_type':           'smORF Class',
    'gene_name':          'Parent Gene',
    'protein_length':       'Microprotein Length',
    'sequence':             'Microprotein Sequence'
})

# Show sequences that start with M first
summary['start_codon'] = summary['Microprotein Sequence'].str.startswith('M')
summary = summary.sort_values(by='start_codon', ascending=False)
summary.drop(columns='start_codon', inplace=True)

# 7) write out
outdir = '../../Results/Annotations'
os.makedirs(outdir, exist_ok=True)
summary.to_csv(os.path.join(outdir, 'Brain_Microproteins_Discovery_summary.csv'),
               index=False)

# GitHub version - supplementary output commented out for relative path compatibility
# outdir_supplement = '/Users/brendanmiller/Library/CloudStorage/Box-Box/brendan_alan_shared_folder/AD_paper/supplementary'
# summary.to_csv(os.path.join(outdir_supplement, 'Table1_Brain_Microproteins_Discovery_summary.csv'),
#                index=False)

# preview
print(summary.head())

# Print dimensions
print(f"Number of rows: {summary.shape[0]}")

# print smORF Class 
print(f"Unique smORF Classes: {summary['smORF Class'].unique()}")

print("\nCounts of Annotation Status:")
print(df['Annotation Status'].value_counts())

# Additional summary showing DDA vs DIA breakdown
print("\nBreakdown of MS evidence types:")
df['DDA_evidence'] = df['total_unique_spectral_counts'] > 0
df['DIA_evidence'] = (~df['Global.PG.Q.Value'].isna() & (df['Global.PG.Q.Value'] <= 0.01))
df['MS_type'] = df.apply(lambda row: 
    'DDA+DIA' if row['DDA_evidence'] and row['DIA_evidence'] else
    'DDA only' if row['DDA_evidence'] else
    'DIA only' if row['DIA_evidence'] else
    'No MS', axis=1)

print(df[df['has_MS']]['MS_type'].value_counts())
