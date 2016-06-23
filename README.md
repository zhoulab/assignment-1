# p53-chip-seq-anno

Generate anno parsing results table and figures for P53 project

run script: `python P53_ChIPSeq_Anno.py`

## About

The purpose of this script is identify patterns in annotation distribution (%) from the data source.

## Data Source

.anno (tab-delimited text) files from Homer annotation output of P53 ChIP-seq; .bed format files

## Process

For each .anno file in the Dm and Mammals directories, get occurence counts under the 'Annotation' column for:

1. non-coding
2. Intergenic
3. intron
4. exon
5. promoter-TSS
6. TTS
7. 5' UTR
8. 3' UTR

Output a summary .txt (tab-delimited text) file for each anno folder including total counts for each .anno file.

Generate pie charts for each file with a consistent color-to-value legend.

## Requirements

1. `matplotlib` (for pie charts)

All other dependencies are included in the python standard library.

## Directory tree

The following directory tree is assumed by `P53_ChIPSeq_Anno.py`:

```
BASE_DIR
│
├───p53-chip-seq-anno (this Git repository)
│   │   P53_ChIPSeq_Anno.py
│   │   ...
│
├───data
│   └───Annos
│       ├───Dm
│       │   │   R_P53_NT60_M14.anno
│       │   │   R_P53_XR60_M14.anno
│       │   │   R_P53NT60_A.anno
│       │   │   ...
│       │
│       └───Mammals
│           │   Akdemir_p53_DOX.anno
│           │   Akdemir_p53_RA.anno
│           │   Akdemir_p53_Untr.anno
│           │   ...
│
└───results
    └───P53-ChIPSeq-Anno-results
        │   Dm-results.txt
        │   Mammals-results.txt
        │
        └───plots
            │   R_P53_NT60_M14.jpg
            │   Akdemir_p53_DOX.jpg
            │   ...

```
