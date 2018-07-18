#!/usr/env/bin python
from __future__ import print_function
import argparse
import subprocess
from itertools import islice
import json
from sys import argv, exit
import re

def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


def run_assemblathon_stats(scaffolds_file=None, contigs_file=None):
    if contigs_file is None:
        try:
            stdout = subprocess.check_output(
                ['perl', 'assemblathon_stats.pl', scaffolds_file],
                stderr=subprocess.STDOUT,
                universal_newlines=True)
            result = process_assemblathon_stats(stdout, 'scaffolds-only')
        except subprocess.CalledProcessError as e:
            print(e.output)
            raise
    elif scaffolds_file is None:
        try:
            stdout = subprocess.check_output(
                ['perl', 'assemblathon_stats.pl', contigs_file],
                stderr=subprocess.STDOUT,
                universal_newlines=True)
            result = process_assemblathon_stats(stdout, 'contigs-only')
        except subprocess.CalledProcessError as e:
            print(e.output)
            raise
    else:
        try:
            stdout = subprocess.check_output(
                ['perl', 'assemblathon_stats.pl', scaffolds_file],
                stderr=subprocess.STDOUT,
                universal_newlines=True)
        except subprocess.CalledProcessError as e:
            print(e.output)
            raise
        try:
            result_scaffolds = process_assemblathon_stats(
                stdout, 'scaffolds-only')
            stdout = subprocess.check_output(
                ['perl', 'assemblathon_stats.pl', scaffolds_file],
                stderr=subprocess.STDOUT,
                universal_newlines=True)
            result_contigs = process_assemblathon_stats(stdout, 'contigs-only')
            result = merge_two_dicts(result_scaffolds, result_contigs)
        except subprocess.CalledProcessError as e:
            print(e.output)
            raise
    return result


def run_asm2stats(scaffolds_file):
    try:
        stdout = subprocess.check_output(
            ['perl', 'asm2stats.minmaxgc.pl', scaffolds_file],
            stderr=subprocess.STDOUT,
            universal_newlines=True)
        result = json.loads(stdout)
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise
    return result


def run_busco(scaffolds_file, contigs_file, ref_file):
    # TODO
    pass


def process_assemblathon_stats(stdout, kind='split-scaffolds'):
    lines = stdout.split('\n')
    result = {}
    for line in islice(lines, 4, None):
        temp = line.split('  ')
        temp = list(filter(None, temp))
        temp = [t.lstrip(' ') for t in temp]
        if len(temp):
            result[temp[0]] = ' '.join(temp[1:])
    if kind == 'split-scaffolds':
        keys = list(result.keys())
        for k in keys:
            if 'contigs' in k or 'Contigs' in k or 'contig' in k or 'Contig' in k:
                result[k + ' (split contigs)'] = result[k]
                del result[k]
    elif kind == 'scaffolds-only':
        keys = list(result.keys())
        for k in keys:
            if 'contigs' in k or 'Contigs' in k or 'contig' in k or 'Contig' in k:
                del result[k]
    else:  # type == 'contigs-only'
        keys = list(result.keys())
        for k in keys:
            if 'scaffolds' in k or 'Scaffolds' in k or 'scaffold' in k or 'Scaffold' in k:
                del result[k]
    return result

def rename_dict(dict_in, names):
    keys = list(dict_in.keys())
    for key in keys:
        if key in names:
            result[names[key]] = dict_in[key]
            del dict_in[key]
    return dict_in

def split_numbers(dict_in):
    keys = list(dict_in.keys())
    keys = [key for key in keys if 'Number of scaffolds (>=' in key or 'Number of contigs (>=' in key ]
    for key in keys:
        num = re.findall(r'\d+', key)
        value = dict_in[key].split(' ')
        if 'Number of scaffolds (>=' in key:
            if 'k nt)' in key:
                dict_in['Percentage of scaffolds (>= {}k nt) (%)'.format(num[0])] = value[1].rstrip('%')
            else:  # 'M nt)' in key
                dict_in['Percentage of scaffolds (>= {}M nt) (%)'.format(num[0])] = value[1].rstrip('%')
        elif 'Number of contigs (>=' in key:
            if 'k nt)' in key:
                dict_in['Percentage of contigs (>= {}k nt) (%)'.format(num[0])] = value[1].rstrip('%')
            else:  # 'M nt)' in key
                dict_in['Percentage of contigs (>= {}M nt) (%)'.format(num[0])] = value[1].rstrip('%')
        dict_in[key] = value[0]
    return dict_in

def post_process_result(scaffolds_file, contigs_file, result):
    rename = {
        'N50 scaffold length': 'N50 of scaffolds',
        'L50 scaffold count': 'L50 of scaffolds',
        'Number of scaffolds > 1K nt': 'Number of scaffolds (>= 1k nt)',
        'Number of scaffolds > 10K nt': 'Number of scaffolds (>= 10k nt)',
        'Number of scaffolds > 100K nt': 'Number of scaffolds (>= 100k nt)',
        'Number of scaffolds > 1M nt': 'Number of scaffolds (>= 1M nt)',
        'Number of scaffolds > 10M nt': 'Number of scaffolds (>= 10M nt)',
        'scaffold %A': 'Scaffold A (%)',
        'scaffold %C': 'Scaffold C (%)',
        'scaffold %G': 'Scaffold G (%)',
        'scaffold %T': 'Scaffold T (%)',
        'scaffold %N': 'Scaffold N (%)',
        'scaffold %non-ACGTN': 'Scaffold non-ACGTN (%)',
        'N50 contig length': 'N50 of contigs',
        'L50 contig count': 'L50 of contigs',
        'Number of scaffold non-ACGTN nt': 'Number of scaffold non-ACGTN nt',
        'Number of contigs > 1K nt': 'Number of contigs (>= 1k nt)',
        'Number of contigs > 10K nt': 'Number of contigs (>= 10k nt)',
        'Number of contigs > 100K nt': 'Number of contigs (>= 100k nt)',
        'Number of contigs > 1M nt': 'Number of contigs (>= 1M nt)',
        'Number of contigs > 10M nt': 'Number of contigs (>= 10M nt)',
        'contig %A': 'Contig A (%)',
        'contig %C': 'Contig C (%)',
        'contig %G': 'Contig G (%)',
        'contig %T': 'Contig T (%)',
        'contig %N': 'Contig N (%)',
        'contig %non-ACGTN': 'Contig non-ACGTN (%)',
        'Number of contig non-ACGTN nt': 'Number of contig non-ACGTN nt',
    }
    result = rename_dict(result, rename)
    result = split_numbers(result)
    if scaffolds_file is not None and 'GC content of scaffolds (%)' not in result:
        gc_ratio = float(result['Scaffold C (%)']) + float(
            result['Scaffold G (%)'])
        not_n_ratio = gc_ratio + float(result['Scaffold T (%)']) + float(
            result['Scaffold A (%)'])
        result['GC content of scaffolds (%)'] = str(
            round(gc_ratio / not_n_ratio * 100, 2))
    if contigs_file is not None and 'GC content of contigs (%)' not in result:
        gc_ratio = float(result['Contig C (%)']) + float(
            result['Contig G (%)'])
        not_n_ratio = gc_ratio + float(result['Contig T (%)']) + float(
            result['Contig A (%)'])
        result['GC content of contigs (%)'] = str(
            round(gc_ratio / not_n_ratio * 100, 2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Calculate various assembly metrics')
    parser.add_argument(
        '-s',
        metavar='scaffolds_file',
        help='a fasta file of scaffolds (can be .gz)',
        nargs=1,
        default=None)
    parser.add_argument(
        '-c',
        metavar='contigs_file',
        help='a fasta file of contigs (can be .gz)',
        nargs=1,
        default=None)
    parser.add_argument(
        '-o',
        metavar='output_path',
        help='where a JSON output file will be generated at',
        nargs=1,
        default='output.json')
    args = parser.parse_args()
    scaffolds_file = args.s[0] if args.s is not None else None
    contigs_file = args.c[0] if args.c is not None else None
    if len(argv) == 1:
        parser.print_help()
        exit(1)
    result_assemblathon = run_assemblathon_stats(scaffolds_file, contigs_file)
    if scaffolds_file is not None:
        result_asm2stats = run_asm2stats(scaffolds_file)
        result = merge_two_dicts(result_assemblathon, result_asm2stats)
    else:
        result = result_assemblathon
    result = post_process_result(scaffolds_file, contigs_file, result)
    if args.o:
        with open(args.o[0], 'w') as f:
            f.write(json.dumps(result, sort_keys=True, indent=4))
    print('Finished, output json file is saved in {}'.format(args.o[0]))