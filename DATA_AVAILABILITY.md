# Brain Microprotein Discovery Project - Methods & Code

**Note: This repository contains the statistical methods and analysis code used in our study to identify canonical and noncanonical microproteins and their differential expression profile in AD. Due to data privacy regulations and file size constraints, raw input data files are not included. This repository serves as a comprehensive documentation of our differential expression pipeline for replication upon receiving raw data. A run_all_analyses.sh script is incldued to process summary files from our processed data.**

## **Repository Purpose**

This repository provides:
- **Complete analysis code** used in the study
- **Detailed methodology documentation**
 - **Example data structures** and file formats
 - **Reproducible summary statistics pipeline** 
 - **Environment setup** and dependency management

## Data Availability

### **Raw Data Sources**
The following data types were used in this study:

1. **Long-read RNA-seq (ESPRESSO output)**
   - Source: Heberle et al.
   - Input: `.esp` abundance files following custom ESPRESSO (see methods) pipeline; raw FASTQ can be accessed
   - Access: Synapse

2. **Short-read RNA-seq** 
   - Source:  ROSMAP consortium, AD Knowledge Portal
   - Access: Available through Synapse
   - Input: Count files following FeatureCount of a GTF file containing GENCODEv43 and unannotated microproteins (DDA, DIA, RiboCode, ShortStop). Available upon request and with data agreements.

3. **TMT Proteomics (FragPipe output)**
   - Source: ROSMAP consortium, AD Knowledge Portal
   - Access: Synapse
   - Input: Matrices containing raw TMT intensity values from fragpipe workflows (directories included). Available upon request and with data agreements.

4. **Ribosome Profiling (RP3/RiboCode)**
   - Source: Duffy et al.
   - Access: dbGap
   - Input: RiboCode output files (.bed, .gtf, .txt). Must go through dbGap—scripts available upon request of raw .fastq files.

5. **Single-cell RNA-seq**
   - Source: Mathys et al. and other published datasets
   - Access and Input: Supplementary of original manuscript from source

## Using This Repository

### **For Replicating Methods**
1. Set up the environment: `bash setup_environment.sh`
2. Place data files in the expected locations (see Data Requirements below)
3. Run the analysis: `bash run_all_analyses.sh`

### **For Methods Reference**
- Browse the analysis modules in `Code/`
- Each module has detailed documentation in its README
- View the complete pipeline in `run_all_analyses.sh`

## Data Requirements

See `DATA_REQUIREMENTS.md` for detailed specifications of required input files and formats.

---

## Data Access & Collaboration

For access to processed data files or collaboration opportunities:
- **Email**: brmiller@salk.edu
- **Institution**: Salk Institute
- **Lab**: PBL-A

We are happy to collaborate and share processed data files under appropriate data sharing agreements as well as data accessibilty approval as outlined by AD Knolwedge Portal.
