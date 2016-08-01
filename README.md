# p53-chip-seq-anno

Analysis of annotation files for P53 project

## Quickstart

This script has multiple processes that can each be run by it's own shell script:

1. `./run_anno_count`
2. `./run_gene_search`
3. `./run_remove_repeats`

## Data Source

`.anno` (tab-delimited text) files from Homer annotation output of P53 ChIP-seq; `.bed` format files

## Requirements

1. `matplotlib>=1.4.0` (for pie charts)

All other dependencies are included in the Python Standard Library.

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
