"""================================================================================================
This script parses BAliBASE reference folders. MSF files are written pairwise alignments between
each pair of two sequences. It also parses FASTA files to then write each sequence to an individual
FASTA file. It then creates global NW and PEbA alignments between each pair of sequences for the
purpose of comparison to the reference BAliBASE pairwise alignments

Ben Iovino  02/03/23   VecAligns
================================================================================================"""

import os
from Bio import SeqIO


def parse_ref_folder(path):
    """=============================================================================================
    This function accepts a folder name parses every MSF and FASTA file to write each pairwise
    alignment and fasta sequence to their own files.

    :param path: directory path to folder
    ============================================================================================="""

    # Get MSF and FASTA files
    msf_files = []
    fasta_files = []
    for file in os.listdir(path):
        if file.endswith('.msf'):  # Append to msf list
            msf_files.append(f'{path}/{file}')
        if file.endswith('.tfa'):  # Append to fasta list
            fasta_files.append(f'{path}/{file}')
    return msf_files, fasta_files


def parse_fasta(filename):
    """=============================================================================================
    This function accepts a fasta file with multiple sequences in each one and writes each sequence
    to its own file in the corresponding folder.

    :param filename: name of file
    return: sequence and id
    ============================================================================================="""

    # Get reference folder name and folder for the correpsonding fasta files
    refname = filename.split('/')[-2:]  # First index is ref folder, second is fa file
    refname[1] = refname[1].split('.tfa')[0]  # Remove file extension
    if not os.path.isdir(f'bb_data/{refname[0]}/{refname[1]}'):
        os.makedirs(f'bb_data/{refname[0]}/{refname[1]}')

    # Parse fasta file and write each sequence to its own file in the corresponding folder
    seq = ''
    seqs = []
    with open(filename, 'r', encoding='utf8') as file:
        for seq in SeqIO.parse(file, 'fasta'):
            SeqIO.write(seq, f'bb_data/{refname[0]}/{refname[1]}/{seq.id}.fa', 'fasta')
            seqs.append(f'{seq.id}.fa')
    return seqs


def parse_msf(filename, id1, id2):
    """=============================================================================================
    This function accepts an MSF file and returns the pairwise alignment between two sequences.

    :param filename: name of file
    :param id1: first sequence id
    :param id2: second sequence id
    return: align1, align2 - corresponding pairwise alignments
    ============================================================================================="""

    seq1 = []
    seq2 = []
    with open(filename, 'r', encoding='utf8') as file:
        for line in file:
            if line.startswith(id1):
                seq1.append(''.join(line.split()[1:]))
            elif line.startswith(id2):
                seq2.append(''.join(line.split()[1:]))

    # Go through both sequences and remove positions with gaps in both
    seq1 = list(''.join(seq1))
    seq2 = list(''.join(seq2))
    for i in range(len(seq1)):  # pylint: disable=C0200
        if seq1[i] == '.' and seq2[i] == '.':
            seq1[i] = ''
            seq2[i] = ''
    align1 = ''.join(seq1)
    align2 = ''.join(seq2)
    return align1, align2


def write_align(seq1, seq2, id1, id2, path):
    """=============================================================================================
    This function accepts two sequences after gaps have been introduced and writes them to a file
    in MSF format, with some extra information about the alignment parameters.

    :param seq1: first aligned sequence
    :param seq2: second aligned sequence
    :param id1: first sequence id
    :param id2: second sequence id
    :param path: directory
    ============================================================================================="""

    # Length of alignment
    length = len(seq1)

    # Add space every 10 characters
    seq1 = [seq1[i:i+10] for i in range(0, len(seq1), 10)]
    seq1 = ' '.join(seq1)
    seq2 = [seq2[i:i+10] for i in range(0, len(seq2), 10)]
    seq2 = ' '.join(seq2)

    # Split sequences every 50 characters
    seq1_split = [seq1[i:i+55] for i in range(0, len(seq1), 55)]
    seq2_split = [seq2[i:i+55] for i in range(0, len(seq2), 55)]

    # Add extra spaces to either id if they are not the same length
    if len(id1) != len(id2):
        if len(id1) > len(id2):
            id2 = id2 + ' ' * (len(id1) - len(id2))
        else:
            id1 = id1 + ' ' * (len(id2) - len(id1))

    # Write to a new line for every index in the split list i.e. every 55 characters
    with open(f'{path}.msf', 'w', encoding='utf8') as file:
        file.write('PileUp\n\n\n\n')
        file.write(f'   MSF:  {length}  Type:  P\n\n')
        file.write(f' Name: {id1} oo  Len:  {length}\n')
        file.write(f' Name: {id2} oo  Len:  {length}\n\n//\n\n\n\n')
        for i in range(len(seq1_split)):  # pylint: disable=C0200
            file.write(f'{id1}      {seq1_split[i]}\n')
            file.write(f'{id2}      {seq2_split[i]}\n\n')

            
def parse_align_files(msf_files, fasta_files, ref_dir):
    """=============================================================================================
    This function accepts lists of two sets of files and a directory to place them in where they
    are parsed correspondingly. As they are parsed, they are also aligned using global_align.py
    and PEbA_align.py.

    :param msf_files: list of msf files
    :param fasta_files: list of fasta files
    :param ref_dir: directory to place files in
    :param tokenizer: loaded tokenizer
    :param model: loaded encoder
    ============================================================================================="""

    # Parse each fasta file, store names of each for subsequent msf parsing
    seqs = []
    for file in fasta_files:
        new_seqs = parse_fasta(file)
        seqs.append(new_seqs)  # Store in nested list to access only relevant fa files for each msf

    # Parse each msf file
    for i, file in enumerate(msf_files):
        ref_align = file.rsplit('/', maxsplit=1)[-1].strip('.msf')  # Get name of ref alignment
        sequences = seqs[i]  # Get corresponding fasta files for this msf file

        # Only want to align each sequence to every other sequence once
        file_count = 0  # Keep track of number of files for naming purposes
        for i, seq in enumerate(sequences):
            loop_count = i  # Keep track of number of loops so no repeats occur
            while loop_count != len(sequences):
                if seq != sequences[loop_count]:  # Don't want to align a sequence to itself

                    # Align sequences with local programs
                    args = (f'-file1 bb_data/{ref_dir}/{ref_align}/{seq} '
                            f'-file2 bb_data/{ref_dir}/{ref_align}/{sequences[loop_count]} '
                            f'-gopen {-11} '
                            f'-gext {-1} '
                            f'-blosum {45}')
                    os.system(f"python global_align.py {args}")

                    # Embed sequences in this script to save time on loading models
                    args = (f'-file1 bb_data/{ref_dir}/{ref_align}/{seq} '
                            f'-file2 bb_data/{ref_dir}/{ref_align}/{sequences[loop_count]} '
                            f'-gopen {-11} '
                            f'-gext {-1} ')
                    os.system(f"python PEbA_align.py {args}")

                    # Grab alignment from reference MSA
                    seq1, seq2 = seq.split('.')[0], sequences[loop_count].split('.')[0]  # Remove fa
                    align1, align2 = parse_msf(file, seq1, seq2)  # Gather pairwise alignment
                    file_path = f'bb_data/{ref_dir}/{ref_align}/{ref_align}_{file_count}'
                    write_align(align1, align2, seq1, seq2, file_path)  # Write pairwise alignment
                    file_count += 1
                loop_count+=1


def main():
    """=============================================================================================
    This function calls parse_ref_folder to get lists of all the msf and tfa fasta files in the
    reference directory of interest. It then calls parse_align_files to parse each tfa file and msf
    file, while also aligning each pariwise comparison of fasta sequences.
    ============================================================================================="""

    # Parse reference folder of interest
    path = 'BAliBASE_R1-5/bb3_release/RV11'
    ref_dir = path.rsplit('/', maxsplit=1)[-1]  # Get last directory in path
    msf_files, fasta_files = parse_ref_folder(path)
    if not os.path.isdir(f'bb_data/{ref_dir}'):
        os.makedirs(f'bb_data/{ref_dir}')

    # Sort each list of files to ensure they match up for msf parsing
    msf_files.sort()
    fasta_files.sort()
    parse_align_files(msf_files, fasta_files, ref_dir)


if __name__ == '__main__':
    main()