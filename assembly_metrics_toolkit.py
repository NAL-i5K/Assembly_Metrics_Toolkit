#!/usr/bin/python
import argparse
import subprocess
import os
import shutil
from itertools import islice

parser = argparse.ArgumentParser(description='Calculate various assembly metrics')
parser.add_argument('scaffolds_file', metavar='scaffolds_file', help='a fasta file of scaffolds (can be .gz)')
parser.add_argument('contigs_file', metavar='contigs_file', help='a fasta file of contigs (can be .gz)', nargs='?')
args = parser.parse_args()

def run_assemblathon_stats(scaffolds_file, contigs_file=None):
    p = subprocess.run(['./assemblathon_stats.pl', scaffolds_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if contigs_file is None:
        result = process_assemblathon_stats(p.stdout, True)
    else:
        result = process_assemblathon_stats(p.stdout, False)
    return result

def run_quast(scaffolds_file, contigs_file=None):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    temp_path = os.path.join(dir_path, '.temp/')
    if os.path.isdir(temp_path):
        shutil.rmtree(temp_path)
    os.makedirs(temp_path)
    if contigs_file is None:
        p = subprocess.run(['quast.py', scaffolds_file, '-o', temp_path, '--min-contig', '0', '-s', '--no-plots', '--no-html'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = process_quast_result(temp_path, True)
    else:
        p = subprocess.run(['quast.py', scaffolds_file, contigs_file, '-o', temp_path, '--min-contig', '0', '--no-plots', '--no-html'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = process_quast_result(temp_path, False)
    return result

def run_busco(scaffolds_file, contigs_file, ref_file):
    # TODO
    pass

def process_assemblathon_stats(stdout, only_scaffolds=False):
    selected_features = set(['Number of scaffolds', 'Total size of scaffolds', 'Longest scaffold', 'Shortest scaffold', 'Number of scaffolds > 1K nt', 'Number of scaffolds > 10K nt', 'Number of scaffolds > 100K nt', 'Number of scaffolds > 1M nt', 'Number of scaffolds > 10M nt', 'Mean scaffold size', 'Median scaffold size', 'scaffold %A', 'scaffold %C', 'scaffold %G', 'scaffold %T', 'scaffold %N', 'scaffold %non-ACGTN' ])
    lines = stdout.split('\n')
    result = {}
    for line in islice(lines, 4, None):
        temp = line.split('  ')
        temp = list(filter(None, temp))
        temp = [ t.lstrip(' ') for t in temp ]
        if len(temp):
            result[temp[0]] = ' '.join(temp[1:])
    if only_scaffolds: 
        # TODO
        pass
    else:
        removed_features = set(result.keys()) - selected_features
        for r in removed_features:
            del result[r]
    return result

def process_quast_result(temp_path, only_scaffolds=False):
    selected_features = set(['Total length (>= 0 bp)', 'Total length (>= 1000 bp)', 'Total length (>= 5000 bp)','Total length (>= 10000 bp)', 'Total length (>= 25000 bp)', 'Total length (>= 50000 bp)', 'N50', 'N75', 'L50', 'L75', 'GC (%)', "# N's per 100 kbp"])
    if only_scaffolds:
        with open(os.path.join(temp_path, 'transposed_report.tsv')) as f:
            header = f.readline()
            header = header.rstrip('\n').split('\t')[1:]
            result = {}
            result['original'] = {}
            values = f.readline().rstrip('\n').split('\t')[1:]
            for h, v in zip(header, values):
                result['original'][h] = v
            result['split'] = {}
            values = f.readline().rstrip('\n').split('\t')[1:]
            for h, v in zip(header, values):
                result['split'][h] = v
            removed_features = set(result['original'].keys()) - selected_features
            for r in removed_features:
                del result['original'][r]
                del result['split'][r]
    else:
        with open(os.path.join(temp_path, 'transposed_report.tsv')) as f:
            header = f.readline()
            header = header.rstrip('\n').split('\t')[1:]
            values = f.readline()
            values = values.rstrip('\n').split('\t')[1:]
        result = {}
        for h,v in zip(header, values):
            result[h] = v
        removed_features = set(result.keys()) - selected_features
        for r in removed_features:
            del result[r]
    return result

def combine_results(result_assemblathon, result_quast, result_busco=None):
    pass

if __name__ == '__main__':
    result_assemblathon = run_assemblathon_stats(args.scaffolds_file, args.contigs_file)
    result_quast = run_quast(args.scaffolds_file, args.contigs_file)
    print(result_assemblathon)
    print(result_quast)
    combine_results(result_assemblathon, result_quast)
