# Brain Microproteins Dashboard

Interactive dashboard for exploring canonical vs noncanonical microproteins in Alzheimer's Disease.

## 🚀 Live Dashboard

Access the live dashboard at: [Your Streamlit App URL]

## 📊 Features

- **Interactive Data Exploration**: Filter and search through microprotein datasets
- **Color-coded Analysis**: Swiss-Prot (canonical) vs Noncanonical microproteins
- **Multiple Analysis Types**: 
  - Annotation Summary
  - Proteomics (TMT)
  - Proteomics + RiboSeq (RP3)
  - Short-Read RNA in AD
  - Long-Read RNA in AD
  - scRNA Enrichment
  - ShortStop Classification
- **UCSC Browser Integration**: Direct links to genome browser
- **Download Results**: Export filtered data as CSV

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run microproteins_dashboard.py
```

## 📁 Data

The dashboard reads CSV files from the following directories:
- `Annotations/` - Annotation and discovery data
- `Proteomics/` - Mass spectrometry results
- `RP3/` - Ribosome profiling data
- `Transcriptomics/` - RNA-seq analysis results
- `scRNA_Enrichment/` - Single-cell analysis

## 👨‍🔬 Citation

Created by Dr. Brendan Miller in Dr. Alan Saghatelian's laboratory at the Salk Institute.

## 📄 License

[Add your license information here]