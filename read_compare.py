"""================================================================================================
This script reads csv files containing results from compute_pra and parses for relevant info.

Ben Iovino  04/05/23   VecAligns
================================================================================================"""

import csv
import os
import pickle
import argparse


def read_csv(filename):
    """=============================================================================================
    This function accepts a csv filename and returns a list of lists with each line being a list.

    :param filename: csv file to be read
    :return: list of lists
    ============================================================================================="""

    with open(filename, 'r', encoding='utf8') as file:
        reader = csv.reader(file)
        data = list(reader)
    return data


def parse_data(data, parse):
    """=============================================================================================
    This function accepts a list of lists and parses for relevant info.

    :param data: list of lists
    :param parse: output to be parsed
    :return: list of lists
    ============================================================================================="""

    avg_align = 0
    count = 0
    for line in data:

        # Even lines are from method 1
        if count == 0 or count % 2 == 0:
            for key, value in COMPARE_DICT_M1.items():
                if parse == 'id':
                    if float(line[3]) <= key:
                        value[0] += float(line[0])/100
                        value[1] += 1
                        break
                elif parse == 'len':
                    if float(line[1]) <= key:
                        value[0] += float(line[0])/100
                        value[1] += 1
                        break

        # Odd lines are from method 2
        else:
            for key, value in COMPARE_DICT_M2.items():
                if parse == 'id':
                    if float(line[3]) <= key:
                        value[0] += float(line[0])/100
                        value[1] += 1
                        break
                elif parse == 'len':
                    if float(line[1]) <= key:
                        value[0] += float(line[0])/100
                        value[1] += 1
                        break

        avg_align += float(line[1])
        count += 1

    return avg_align, count


def avg_dict():
    """=============================================================================================
    This function takes a dictionary with a list of values and returns a dictionary with the average
    of the values.

    :return: dict
    ============================================================================================="""

    # Dicts are global
    for key, value in COMPARE_DICT_M1.items():
        if value[1] > 10: # Want at least 10 alignments in this range before we average
            COMPARE_DICT_M1[key] = value[0]/value[1]*100
        else:
            COMPARE_DICT_M1[key] = 0
    for key, value in COMPARE_DICT_M2.items():
        if value[1] > 10:
            COMPARE_DICT_M2[key] = value[0]/value[1]*100
        else:
            COMPARE_DICT_M2[key] = 0

    # Print results
    print(f'M1: {COMPARE_DICT_M1}')
    print()
    print(f'M2: {COMPARE_DICT_M2}')

    # Save to pickle
    with open('compare_dict_m1.pkl', 'wb') as file:
        pickle.dump(COMPARE_DICT_M1, file)
    with open('compare_dict_m2.pkl', 'wb') as file:
        pickle.dump(COMPARE_DICT_M2, file)


def main():
    """=============================================================================================
    This function initializes global dictionaries where values from csv files are stored in buckets.
    It then reads every csv file in the directory structure and parses for info of interest. It then
    finds the average of each bucket and prints the results.
    ============================================================================================="""

    # Arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', type=str, default='/home/ben/Desktop/PEbA_Data/Runs/gen3/PEBA-BLOSUM/run9')
    parser.add_argument('-t', type=str, default='len')
    args = parser.parse_args()

    # Store values from csv
    global COMPARE_DICT_M1  #pylint: disable=W0601
    global COMPARE_DICT_M2  #pylint: disable=W0601

    # Identity buckets
    if args.t == 'id':
        COMPARE_DICT_M1 = {9: [0, 0], 19: [0, 0], 29: [0, 0], 39: [0, 0], 49: [0, 0],
                     59: [0, 0], 69: [0, 0], 79: [0, 0], 89: [0, 0], 99: [0, 0]}
        COMPARE_DICT_M2 = {9: [0, 0], 19: [0, 0], 29: [0, 0], 39: [0, 0], 49: [0, 0],
                     59: [0, 0], 69: [0, 0], 79: [0, 0], 89: [0, 0], 99: [0, 0]}

    # Length buckets
    elif args.t == 'len':
        COMPARE_DICT_M1 = {499: [0, 0], 999: [0, 0], 1499: [0, 0], 1999: [0, 0], 2499: [0, 0]}
        COMPARE_DICT_M2 = {499: [0, 0], 999: [0, 0], 1499: [0, 0], 1999: [0, 0], 2499: [0, 0]}

    # Directory structure -> set/run/ref/msa/compare.csv
    # Want to read every single csv
    avg_align, count = 0, 0
    path = args.p
    #for run in os.listdir(path):  #pylint: disable=R1702
    for ref in os.listdir(f'{path}'):
        for msa in os.listdir(f'{path}/{ref}'):
            if msa.startswith('B'):
                for file in os.listdir(f'{path}/{ref}/{msa}'):
                    if file.endswith('csv'):

                        # Read csv and parse
                        data = read_csv(f'{path}/{ref}/{msa}/{file}')
                        a, b = parse_data(data, args.t)
                        avg_align += a
                        count += b

    #print(COMPARE_DICT_M1)
    #print(COMPARE_DICT_M2)

    # Find average for each key
    avg_dict()


if __name__ == "__main__":
    main()