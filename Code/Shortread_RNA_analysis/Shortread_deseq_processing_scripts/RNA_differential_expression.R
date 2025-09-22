library("DESeq2")
library(dplyr)
library(tibble)
library(plotly)
library(biomaRt)
font_add_google("Roboto", "roboto")
showtext_auto()

setwd("/Users/brendanmiller/Library/CloudStorage/Box-Box/brain_smorfs/shortstop/deseq_on_rosmap/")

# Load Counts ----
counts_hg38 <- read.csv('/Users/brendanmiller/Library/CloudStorage/Box-Box/brain_smorfs/shortstop/deseq_on_rosmap/combined_counts_pe_150_cpm05.csv', row.names = 1, check.names = FALSE)

counts_hg19 <- read.csv('/Users/brendanmiller/Library/CloudStorage/Box-Box/brain_smorfs/shortstop/deseq_on_rosmap/combined_counts_hg19_cpm05.csv', row.names = 1, check.names = FALSE)
# Rename columns
colnames(counts_hg19) <- sapply(colnames(counts_hg19), function(name) {
  if (grepl("\\.final$", name)) {  # Check if the name ends with '.final'
    paste0("Sample_", sub("\\.final$", "", name))  # Remove '.final' and add 'Sample_' prefix
  } else {
    name  # Keep the name unchanged
  }
})

counts_hg38$gene_id <- rownames(counts_hg38)
counts_hg19$gene_id <- rownames(counts_hg19)

# Combine by row names
combined_counts <- merge(counts_hg38, counts_hg19, by = "gene_id", all = TRUE)
rownames(combined_counts) <- combined_counts$gene_id
combined_counts <- combined_counts[,-1]
dim(combined_counts)
head(combined_counts)

synapse_tmt_meta <- read.csv('/Users/brendanmiller/Library/CloudStorage/Box-Box/brain_smorfs/rosmap_metadata/synapse_download_rnaseq.csv')

combined_counts <- combined_counts %>%
  dplyr::select(all_of(intersect(colnames(combined_counts), synapse_tmt_meta$specimenID)))
dim(combined_counts)

# Load metadata ----
rna_meta <- read.csv('/Users/brendanmiller/Library/CloudStorage/Box-Box/brain_smorfs/rosmap_metadata/ROSMAP_assay_rnaSeq_metadata.csv')
clinical_meta <- read.csv('/Users/brendanmiller/Library/CloudStorage/Box-Box/brain_smorfs/rosmap_metadata/ROSMAP_clinical.csv')

rna_clinical_meta <- merge(synapse_tmt_meta, rna_meta, by = "specimenID") %>%
  merge(clinical_meta, by = "individualID") %>%
  dplyr::mutate(age_death = ifelse(age_death == "90+", 91, age_death)) %>%
  dplyr::mutate(age_death = as.numeric(age_death)) %>%
  dplyr::filter(!is.na(age_death)) %>%
  dplyr::filter(specimenID %in% colnames(combined_counts)) %>%
  dplyr::filter(!duplicated(specimenID))

dim(rna_clinical_meta)

# Create a function to classify each case based on the revised rubric
classify_case <- function(braak, cerad, mmse, cogdx) {
  # Convert CERAD scores according to the new mapping
  cerad <- ifelse(cerad == 4, 0,
                  ifelse(cerad == 3, 1,
                         ifelse(cerad == 2, 2,
                                ifelse(cerad == 1, 3, cerad))))
  
  # Determine dementia status
  dementia <- (mmse < 24) | (cogdx >= 4)
  
  # Apply classification rubric
  if (cerad >= 0 & cerad <= 1 & braak >= 0 & braak <= 3 & !dementia) {
    if (braak == 3 & cerad != 0) {
      return(NA)  # Special condition: Braak = 3 requires CERAD = 0 (actual CERAD = 4)
    }
    return("Control")
  } else if (cerad >= 1 & cerad <= 3 & braak >= 3 & braak <= 6 & !dementia) {
    return("AsymAD")
  } else if (cerad >= 2 & cerad <= 4 & braak >= 3 & braak <= 6 & dementia) {
    return("AD")  # Expanded to include CERAD = 4 for AD
  } else {
    return(NA)
  }
}

# Apply the function to each row in the metadata dataframe
rna_clinical_meta <- rna_clinical_meta %>%
  dplyr::mutate(new_dx = mapply(classify_case, braaksc, ceradsc, cts_mmse30_lv, cogdx)) %>%
  dplyr::filter(!is.na(new_dx)) %>%
  dplyr::mutate(msex = as.factor(msex))
dim(rna_clinical_meta)
table(rna_clinical_meta$new_dx)



### Run DESeq2 ----
combined_counts[is.na(combined_counts)] <- 0
combined_counts <- combined_counts[, rna_clinical_meta$specimenID]
dds <- DESeqDataSetFromMatrix(countData = combined_counts, colData = rna_clinical_meta, design = ~ RIN + sequencingBatch + msex + age_death + pmi + new_dx)
dds <- DESeq(dds, parallel = TRUE)
#saveRDS(dds, '/Users/brendanmiller/Library/CloudStorage/Box-Box/brain_smorfs/shortstop/deseq_on_rosmap/dds.rds')
dds <- readRDS('/Users/brendanmiller/Library/CloudStorage/Box-Box/brain_smorfs/shortstop/deseq_on_rosmap/dds.rds')


### Run PCA ----
vsd <- vst(dds, blind = FALSE)
pca_data <- plotPCA(vsd, intgroup = "sequencingBatch", returnData = TRUE)
percentVar <- round(100 * attr(pca_data, "percentVar"))

ggplot(pca_data, aes(x = PC1, y = PC2, color = sequencingBatch)) +
  geom_point(size = 3) +
  xlab(paste0("PC1: ", percentVar[1], "% variance")) +
  ylab(paste0("PC2: ", percentVar[2], "% variance")) +
  ggtitle("PCA Plot of Samples") +
  theme_minimal()




### Run results contrast to find AD vs. Control ----
res_new_dx <- results(dds, contrast = c("new_dx", "AD", "Control"))

res_new_dx_df <- res_new_dx %>% as.data.frame()
res_new_dx_df$gene_id <- rownames(res_new_dx_df)
res_new_dx_df$logP <- -log10(res_new_dx_df$padj)
res_new_dx_df$type <- ifelse(grepl("^ENSG", res_new_dx_df$gene_id), "ENSEMBL", "Salk")

res_new_dx_df <- res_new_dx_df %>%
  dplyr::select(baseMean, log2FoldChange, lfcSE, stat, pvalue, padj) %>%
  dplyr::rename_with(~ paste0("rosmapRNA_", .), everything()) %>%
  dplyr::mutate(gene_id = rownames(res_new_dx_df)) 
head(res_new_dx_df)

# Convert ENSG IDs to gene symbols using org.Hs.eg.db
library(org.Hs.eg.db)
library(AnnotationDbi)
res_new_dx_df$temp_gene_id <- sub("\\..*$", "", res_new_dx_df$gene_id)
ensembl_gene_symbols <- res_new_dx_df$temp_gene_id

gene_symbols <- mapIds(
  org.Hs.eg.db,
  keys = ensembl_gene_symbols,
  column = "SYMBOL",
  keytype = "ENSEMBL",
  multiVals = "first"
)

# Add gene symbols to results
res_new_dx_df$gene_symbol <- gene_symbols[ensembl_gene_symbols]
res_new_dx_df$gene_id <- ifelse(is.na(res_new_dx_df$gene_symbol), res_new_dx_df$gene_id, res_new_dx_df$gene_symbol)

res_new_dx_df <- res_new_dx_df %>%
  dplyr::select(-c('gene_symbol', 'temp_gene_id'))

write.csv(res_new_dx_df, '/Users/brendanmiller/Library/CloudStorage/Box-Box/brain_smorfs/shortstop/deseq_on_rosmap/rosmap_tmt_rna_deseq2_cpm05_control_vs_ad_results.csv', row.names = FALSE)
