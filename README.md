**************************************************************************************************************
# Protein Embedding Based Alignments (PEbA)
**************************************************************************************************************

This project uses Rostlab's ProtT5-XL-UniRef50 encoder (https://huggingface.co/Rostlab/prot_t5_xl_uniref50) to
embed protein sequences, and then calculates the cosine similarity between each residue's vector to align them 
using traditional sequence alignment algorithms. The cosine similarity scores are used in place of substitution
matrices, such as BLOSUM, with the goal of producing accurate alignments for sequences that share low character
identity (<20-35%), referred to as the "twilight zone" of protein sequence alignment.

PEbA is implemented in local_PEbA.py, where it uses the Smith-Waterman 'local' algorithm to align two sequences.
The script for substitution matrix based alignments are in local_MATRIX.py, which currently supports all BLOSUM 
matrices and PFASUM60 for testing purposes.

The PEbA script is designed to be run from the command line. The following arguments are allowed, with -embed1
-embed2 being optional arguments if the corresponding sequences from -file1 and -file2 have already been
been embedded and saved as a numpy array:

    -file1 <file1.fa>   : Path to first sequence fasta file
    -file2 <file2.fa>   : Path to second sequence fasta file
    -embed1 <file1.txt> : Path to first sequence embedding file
    -embed2 <file2.txt> : Path to second sequence embedding file
    -gopen <int/float>  : Gap opening penalty
    -gext <int/float>   : Gap extension penalty
    -encoder <str>      : Encoder used to generate embeddings

Embeddings from any model can be used as long as the embeddings are a 1D array the same length as the sequence.
The -encoder argument is used to specify the model used and written to the output .msf file for reference.

**************************************************************************************************************
# Comparing PEbA to Reference Alignments
**************************************************************************************************************

To determine if PEbA alignments produce more accurate alignments than those with subsitution matrices, both 
types of alignments are compared to reference alignments from BAliBASE 4 (https://www.lbgi.fr/balibase/).
BAliBASE alignments are structure based benchmarks used to compare new methods of alignment, such as this one. 
The references of most interest include RV11, sequences with <20% identity, and RV12, sequences with 20-40% 
identity, but other references with higher % identity are also used for comparison.

The 'Total Column Score' (TCS) is used to compare the performance between the alignments generated by this
project to the reference alignments. This percentage indicates how many residue pairs are shared between two
alignments. compute_tcs.py computes this metric between two alignments, the first being the reference alignment,
and the second being the alignment being compared. An example of the output is shown below:


TCS: 55.06   ref_length: 690   comparison_length: 356   similarity: 14.61


TCS is a percentage between 0-100, 0 representing no shared residue pairs between two alignments, and 100
representing all residue pairs are found in both alignments. The TCS metric is calculated by dividing the
number of shared residue pairs between the reference and test alignment by the number of pairs in the reference
alignment, and then multiplying by 100. The ref_length is the length of the reference alignment, and the
comparison_length is the number of residue pairs being compared (gaps are not counted). The similarity is
the percentage of identical residues between the two sequences that are matched together i.e. if a pair
has the same two residues, it is a match.