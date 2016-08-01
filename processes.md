# Processes

## Annotation count

    ./run_anno_count

### Overview

Identify patterns in annotation distribution (%) from the data source.

### Method

For each `.anno` file in the user-specified annotation folder(s), get occurence counts under the **Annotation** column for:

1. non-coding
2. Intergenic
3. intron
4. exon
5. promoter-TSS
6. TTS
7. 5' UTR
8. 3' UTR

Output a summary tab-delimited text file for each anno folder including total counts for each `.anno` file.

Generate pie charts for each `.anno` file with a consistent color-to-value legend.

## Gene search

    ./run_gene_search

### Overview

Search for occurences of a gene in the data source.

### Method

For each `.anno` file in the user-specified annotation folder, get rows containing an **exact match** of the search value under the **Gene Name** column.

Rows are stored with attributes **Start**, **End**, and **Length**.

## Remove repeats

    ./run_remove_repeats

### Overview

Extract lines that are **not** in the repetitive sequence regions (repeats).

### Method

For each `.anno` file in the user-specified annotation folder(s), get rows containing non-repeat annotations under the **Detailed Annotation** column.

Non-repeat annotations are defined as:

1. TSS
1. TTS
1. exon
1. 5' UTR
1. 3' UTR
1. CpG
1. intron
1. Intergenic
1. non-coding

(from http://homer.salk.edu/homer/ngs/annotation.html)

Rows are saved with columns **Chr**, **Start**, **End**, and **PeakID**.

For reference, full rows are stored in `results/P53-ChIPSeq-Anno_remove-repeats/[ANNO_FOLDER]-no_repeats/no_repeats_full_rows/` and repeat rows in `results/P53-ChIPSeq-Anno_remove-repeats/[ANNO_FOLDER]-no_repeats/repeats_only_full_rows/`

