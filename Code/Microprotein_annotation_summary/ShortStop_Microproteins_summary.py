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
# Sort so MS rows come first for each sequence
df = df.sort_values(by='has_MS', ascending=False)
df = df.drop_duplicates(subset='sequence')

# === 6. Set annotation label based on which evidence is present ===
df['Annotation Status'] = df['has_MS'].map({True: 'MS', False: 'RiboCode_SAM'})

# === Keep only rows with valid shortstop annotations ===
summary = df.loc[df['shortstop_label'].notna(), [
    'sequence',
    'CLICK_UCSC',
    'gene_symbol',
    'smorf_type',
    'shortstop_label',
    'shortstop_score',
    'Annotation Status'
]].rename(columns={
    'sequence': 'Microprotein Sequence',
    'gene_symbol': 'smORF ID',
    'smorf_type': 'smORF Class',
    'shortstop_label': 'ShortStop Label',
    'shortstop_score': 'ShortStop Score'
})

# === Print ShortStop label counts ===
print(summary['ShortStop Label'].value_counts())
print("\nCounts by Annotation Status:")
print(summary['Annotation Status'].value_counts())

# === Save summary ===
outdir = '/Users/brendanmiller/Library/CloudStorage/Box-Box/brendan_alan_shared_folder/AD_paper/Github/Results/Annotations'
summary.to_csv(os.path.join(outdir, 'ShortStop_Microproteins_summary.csv'), index=False)

outdir_supplement = '/Users/brendanmiller/Library/CloudStorage/Box-Box/brendan_alan_shared_folder/AD_paper/supplementary'
summary.to_csv(os.path.join(outdir_supplement, 'Table3_ShortStop_Microproteins_summary.csv'), index=False)

# === Save summary ===
outdir = '/Users/brendanmiller/Library/CloudStorage/Box-Box/brendan_alan_shared_folder/AD_paper/Github/Results/Annotations'
summary.to_csv(os.path.join(outdir, 'ShortStop_Microproteins_summary.csv'), index=False)

outdir_supplement = '/Users/brendanmiller/Library/CloudStorage/Box-Box/brendan_alan_shared_folder/AD_paper/supplementary'
summary.to_csv(os.path.join(outdir_supplement, 'Table3_ShortStop_Microproteins_summary.csv'), index=False)