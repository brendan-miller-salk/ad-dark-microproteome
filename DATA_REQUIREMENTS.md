# Data Requirements and File Formats

This document specifies the input data requirements for running the brain microprotein discovery pipeline.

## Required Input Files

### **Core Data Files (`Code/data/`)**

#### 1. `microprotein_master.csv`
**Description**: Master database of all discovered microproteins with annotations

#### 2. `ac_list_mapping.csv`
**Description**: Mapping between accession numbers and Ensembl gene IDs
**Columns Required**:
- Accession identifiers
- Corresponding Ensembl gene IDs

#### 3. `brain_espresso_medianCPM05.csv`
**Description**: ESPRESSO long-read RNA-seq data processed to CPM with filtering
**Format**: Expression matrix with genes/transcripts as rows, samples as columns

#### 4. `counts.csv`
**Description**: RNA-seq count data for differential expression analysis
**Format**: Count matrix with genes as rows, samples as columns

#### 5. `combined_gpath_results.csv`
**Description**: Gene pathway analysis results by cell type
**Columns Required**:
- Gene identifiers
- Cell type classifications
- Pathway scores/enrichments

### **Analysis-Specific Input Files**

#### **Long-read RNA Analysis**
- ESPRESSO abundance files (`.esp` format)
- Sample metadata files
- Reference annotations

#### **Short-read RNA Analysis**  
- Combined count matrices (hg38 and hg19)
- ROSMAP metadata files:
  - `synapse_download_rnaseq.csv`
  - `ROSMAP_assay_rnaSeq_metadata.csv`
  - `ROSMAP_clinical.csv`

#### **TMT Proteomics Analysis**
- FragPipe output directories with:
  - Protein identification files
  - Quantification matrices
  - Quality control metrics

#### **RP3 Analysis**
- RiboCode output files:
  - `.bed`, `.gtf`, `.txt` format files
  - Mapping group files with RPKM values

#### **Annotation Pipeline**
- smORF GTF files
- Ensembl reference annotations
- ShortStop pipeline outputs

## File Format Examples

### **microprotein_master.csv** (first few columns)
```csv
Database,protein_class_length,discovery_origin,Global.PG.Q.Value,gene_symbol,sequence
Salk,Microprotein,proteogenomics,0.001,GENE1,MATKL...
Salk,Microprotein,ribocode_shortstop,,GENE2,MVKLS...
```

### **Expression Matrix Format**
```csv
gene_id,sample1,sample2,sample3,...
ENSG00000001,12.5,8.2,15.1,...
ENSG00000002,0.0,2.1,1.8,...
```

## Getting Help

If you need clarification on file formats or have questions about adapting the pipeline to your data:
- Contact: brmiller@salk.edu