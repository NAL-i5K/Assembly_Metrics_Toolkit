import argparse
import subprocess
import os
import shutil
from itertools import islice

parser = argparse.ArgumentParser(description='Calculate various assembly metrics')
parser.add_argument('file_name', metavar='file', help='a fasta file of scaffolds (can be .gz)')

args = parser.parse_args()

def run_assemblathon_stats(file_name):
    p = subprocess.run(['./assemblathon_stats.pl', file_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    result = process_assemblation_stats(p.stdout)
    return result

def run_quast(file_name, only_scaffold=False):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    temp_path = os.path.join(dir_path, '.temp/')
    if os.path.isdir(temp_path):
        shutil.rmtree(temp_path)
    os.makedirs(temp_path)
    if only_scaffold:
        p = subprocess.run(['quast.py', file_name, '-o', temp_path, '--min-contig', '0', '-s', '--no-plots', '--no-html'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        p = subprocess.run(['quast.py', file_name, '-o', temp_path, '--min-contig', '0', '--no-plots', '--no-html'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with open(os.path.join(temp_path, 'transposed_report.tsv')) as f:
        header = f.readline()
        header = header.rstrip('\n').split('\t')
        values = f.readline()
        values = values.rstrip('\n').split('\t')
    result = {}
    for h,v in zip(header, values):
        result[h] = v
    return result

def run_busco(file_name):
    # TODO
    pass

def process_assemblation_stats(stdout):
    lines = stdout.split('\n')
    result = {}
    for line in islice(lines, 4, None):
        temp = line.split('  ')
        temp = list(filter(None, temp))
        temp = [ t.lstrip(' ') for t in temp ]
        if len(temp):
            result[temp[0]] = ' '.join(temp[1:])
    return result

if __name__ == '__main__':
    result_assemblathon = run_assemblathon_stats(args.file_name)
    result_quast = run_quast(args.file_name)
    selected_assemblathon_features = ['Number of scaffolds', 'Total size of scaffolds', 'Longest scaffold', 'Shortest scaffold', 'Number of scaffolds > 1K nt', 'Number of scaffolds > 10K nt', 'Number of scaffolds > 100K nt', 'Number of scaffolds > 1M nt', 'Number of scaffolds > 10M nt', 'Mean scaffold size', 'Median scaffold size', 'scaffold %A', 'scaffold %C', 'scaffold %G', 'scaffold %T', 'scaffold %N', 'scaffold %non-ACGTN' ]
    for f in selected_assemblathon_features:
        print(f + ':' + result_assemblathon[f])
    selected_quast_features = ['Total length (>= 0 bp)', 'Total length (>= 1000 bp)', 'Total length (>= 5000 bp)','Total length (>= 10000 bp)', 'Total length (>= 25000 bp)', 'Total length (>= 50000 bp)', 'N75', 'L75', 'GC (%)', "# N's per 100 kbp"]
    for f in selected_quast_features:
        print(f + ':' + result_quast[f])
