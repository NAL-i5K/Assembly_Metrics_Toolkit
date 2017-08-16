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
        result = process_assemblathon_stats(p.stdout, 'split-scaffolds')
    else:
        result_scaffolds = process_assemblathon_stats(p.stdout, 'scaffolds-only')
        p = subprocess.run(['./assemblathon_stats.pl', scaffolds_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        result_contigs = process_assemblathon_stats(p.stdout, 'contigs-only')
        result = {**result_scaffolds, **result_contigs}
    return result

def run_quast(scaffolds_file, contigs_file=None):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    temp_path = os.path.join(dir_path, '.temp/')
    if os.path.isdir(temp_path):
        shutil.rmtree(temp_path)
    os.makedirs(temp_path)
    if contigs_file is None:
        p = subprocess.run(['quast.py', scaffolds_file, '-o', temp_path, '--min-contig', '0', '--contig-thresholds', '1000,10000,100000,1000000,10000000', '-s', '--no-plots', '--no-html'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = process_quast_result(temp_path, True)
    else:
        p = subprocess.run(['quast.py', scaffolds_file, contigs_file, '-o', temp_path, '--min-contig', '0', '--contig-thresholds', '1000,10000,100000,1000000,10000000', '--no-plots', '--no-html'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = process_quast_result(temp_path, False)
    return result

def run_busco(scaffolds_file, contigs_file, ref_file):
    # TODO
    pass

def process_assemblathon_stats(stdout, type='split-scaffolds'):
    #selected_features = set(['Number of scaffolds', 'Total size of scaffolds', 'Longest scaffold', 'Shortest scaffold', 'Number of scaffolds > 1K nt', 'Number of scaffolds > 10K nt', 'Number of scaffolds > 100K nt', 'Number of scaffolds > 1M nt', 'Number of scaffolds > 10M nt', 'Mean scaffold size', 'Median scaffold size', 'scaffold %A', 'scaffold %C', 'scaffold %G', 'scaffold %T', 'scaffold %N', 'scaffold %non-ACGTN' ])
    lines = stdout.split('\n')
    result = {}
    for line in islice(lines, 4, None):
        temp = line.split('  ')
        temp = list(filter(None, temp))
        temp = [ t.lstrip(' ') for t in temp ]
        if len(temp):
            result[temp[0]] = ' '.join(temp[1:])
    if type == 'split-scaffolds':
        #selected_features = []
        pass
    elif type == 'scaffolds-only':
        #selected_features = []
        keys = list(result.keys())
        for k in keys:
            if 'contigs' in k or 'Contigs' in k or 'contig' in k or 'Contig' in k or 'N50' in k or 'L50' in k:
                del result[k]
    else: # type == 'contigs-only'
        # selected_features = []
        keys = list(result.keys())
        for k in keys:
            if 'scaffolds' in k or 'Scaffolds' in k or 'scaffold' in k or 'Scaffold' in k or 'N50' in k or 'L50' in k:
                del result[k]
    return result

def process_quast_result(temp_path, only_scaffolds=False):
    selected_features = set(['Total length (>= 1000 bp)', 'Total length (>= 10000 bp)','Total length (>= 100000 bp)', 'Total length (>= 1000000 bp)', 'Total length (>= 10000000 bp)', 'N50', 'N75', 'L50', 'L75', 'GC (%)', "# N's per 100 kbp"])
    if only_scaffolds:
        with open(os.path.join(temp_path, 'transposed_report.tsv')) as f:
            header = f.readline()
            header = header.rstrip('\n').split('\t')[1:]
            result = {}
            values = f.readline().rstrip('\n').split('\t')[1:]
            for h, v in zip(header, values):
                if h in selected_features:
                    result[h] = v
            values = f.readline().rstrip('\n').split('\t')[1:]
            for h, v in zip(header, values):
                if h in selected_features:
                    result[h + ' (split contigs)'] = v
            #removed_features = set(result['original'].keys()) - selected_features
            #for r in removed_features:
            #    del result['original'][r]
            #    del result['split'][r]
    else:
        with open(os.path.join(temp_path, 'transposed_report.tsv')) as f:
            header = f.readline()
            header = header.rstrip('\n').split('\t')[1:]
            values = f.readline()
            values = values.rstrip('\n').split('\t')[1:]
            result = {}
            for h,v in zip(header, values):
                if h in selected_features:
                    result[h + ' (scaffolds)'] = v
            values = f.readline().rstrip('\n').split('\t')[1:]
            for h, v in zip(header, values):
                if h in selected_features:
                    result[h + ' (contigs)'] = v
        #removed_features = set(result.keys()) - selected_features
        #for r in removed_features:
        #    del result[r]
    return result

def print_result(scaffolds_file, contigs_file, result):
    if contigs_file is None:
        order = ['Total length (>= 1000 bp)', 'Total length (>= 10000 bp)','Total length (>= 100000 bp)', 'Total length (>= 1000000 bp)', 'Total length (>= 10000000 bp)',
                 'GC (%)', 'N50', 'N75', 'L50', 'L75', "# N's per 100 kbp"]
        order =  order + [ o + ' (split contigs)' for o in order]
        # TODO
    else:
        order = ['Total length (>= 1000 bp)', 'Total length (>= 10000 bp)','Total length (>= 100000 bp)', 'Total length (>= 1000000 bp)', 'Total length (>= 10000000 bp)',
                  'GC (%)', 'N50', 'N75', 'L50', 'L75', "# N's per 100 kbp"]
        order = [ o + ' (scaffolds)' for o in order] + [ o + ' (contigs)' for o in order]
    for o in order:
        print(o + ': ' + result[o])

if __name__ == '__main__':
    result_assemblathon = run_assemblathon_stats(args.scaffolds_file, args.contigs_file)
    result_quast = run_quast(args.scaffolds_file, args.contigs_file)
    result = {**result_assemblathon, **result_quast}
    print_result(args.scaffolds_file, args.contigs_file, result)
