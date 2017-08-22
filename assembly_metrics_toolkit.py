#!/usr/bin/python
import argparse
import subprocess
import os
import shutil
from itertools import islice
import json

parser = argparse.ArgumentParser(description='Calculate various assembly metrics')
parser.add_argument('scaffolds_file', metavar='scaffolds_file', help='a fasta file of scaffolds (can be .gz)')
parser.add_argument('contigs_file', metavar='contigs_file', help='a fasta file of contigs (can be .gz)', nargs='?')
parser.add_argument('-o', metavar='output_path', help='where a JSON output file will be generated at', nargs=1)
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
    lines = stdout.split('\n')
    result = {}
    for line in islice(lines, 4, None):
        temp = line.split('  ')
        temp = list(filter(None, temp))
        temp = [ t.lstrip(' ') for t in temp ]
        if len(temp):
            result[temp[0]] = ' '.join(temp[1:])
    if type == 'split-scaffolds':
        keys = list(result.keys())
        for k in keys:
            if 'contigs' in k or 'Contigs' in k or 'contig' in k or 'Contig' in k:
                result [ k+ ' (split contigs)' ] = result[k]
                del result[k]
    elif type == 'scaffolds-only':
        keys = list(result.keys())
        for k in keys:
            if 'contigs' in k or 'Contigs' in k or 'contig' in k or 'Contig' in k or 'N50' in k or 'L50' in k:
                del result[k]
    else: # type == 'contigs-only'
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
                    result[h + ' (scaffolds)'] = v
            values = f.readline().rstrip('\n').split('\t')[1:]
            for h, v in zip(header, values):
                if h in selected_features:
                    result[h + ' (split contigs)'] = v
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
    return result

def post_process_result(scaffolds_file, contigs_file, result):
    rename = {
            'GC (%) (split contigs)': 'GC content of split contigs (%)',
            'N50 (split contigs)': 'N50 of split contigs',
            'N75 (split contigs)': 'N75 of split contigs',
            'L50 (split contigs)': 'L50 of split contigs',
            'L75 (split contigs)': 'L75 of split contigs',
            "# N's per 100 kbp (split contigs)": 'Number of N per 100k nt of split contigs',
            'GC (%) (contigs)': 'GC contnet of contigs (%)',
            'N50 (contigs)': 'N50 of contigs',
            'N75 (contigs)': 'N75 of contigs',
            'L50 (contigs)': 'L50 of contigs',
            'L75 (contigs)': 'L75 of contigs',
            "# N's per 100 kbp (contigs)": 'Number of N per 100k nt of contigs',
            'GC (%) (scaffolds)': 'GC contnet of scaffolds (%)',
            'N50 (scaffolds)': 'N50 of scaffolds',
            'N75 (scaffolds)': 'N75 of scaffolds',
            'L50 (scaffolds)': 'L50 of scaffolds',
            'L75 (scaffolds)': 'L75 of scaffolds',
            "# N's per 100 kbp (scaffolds)": 'Number of N per 100k nt of scaffolds',
            'Total length (>= 1000 bp) (split contigs)': 'Total length of split contigs (>= 1k nt)',
            'Total length (>= 10000 bp) (split contigs)': 'Total length of split contigs (>= 10k nt)',
            'Total length (>= 100000 bp) (split contigs)': 'Total length of split contigs (>= 100k nt)',
            'Total length (>= 1000000 bp) (split contigs)': 'Total length of split contigs (>= 1M nt)',
            'Total length (>= 10000000 bp) (split contigs)': 'Total length of split contigs (>= 10M nt)',
            'Total length (>= 1000 bp) (contigs)': 'Total length of contigs (>= 1k nt)',
            'Total length (>= 10000 bp) (contigs)': 'Total length of contigs (>= 10k nt)',
            'Total length (>= 100000 bp) (contigs)': 'Total length of contigs (>= 100k nt)',
            'Total length (>= 1000000 bp) (contigs)': 'Total length of contigs (>= 1M nt)',
            'Total length (>= 10000000 bp) (contigs)': 'Total length of contigs (>= 10M nt)',
            'Total length (>= 1000 bp) (scaffolds)': 'Total length of scaffolds (>= 1k nt)',
            'Total length (>= 10000 bp) (scaffolds)': 'Total length of scaffolds (>= 10k nt)',
            'Total length (>= 100000 bp) (scaffolds)': 'Total length of scaffolds (>= 100k nt)',
            'Total length (>= 1000000 bp) (scaffolds)': 'Total length of scaffolds (>= 1M nt)',
            'Total length (>= 10000000 bp) (scaffolds)': 'Total length of scaffolds (>= 10M nt)',
            'Number of scaffolds > 1K nt': 'Number of scaffolds (>= 1k nt)',
            'Number of scaffolds > 10K nt': 'Number of scaffolds (>= 10k nt)',
            'Number of scaffolds > 100K nt': 'Number of scaffolds (>= 100k nt)',
            'Number of scaffolds > 1M nt': 'Number of scaffolds (>= 1M nt)',
            'Number of scaffolds > 10M nt': 'Number of scaffolds (> 10M nt)',
            'scaffold %A': 'Scaffold A (%)',
            'scaffold %C': 'Scaffold C (%)',
            'scaffold %G': 'Scaffold G (%)',
            'scaffold %T': 'Scaffold T (%)',
            'scaffold %N': 'Scaffold N (%)',
            'scaffold %non-ACGTN': 'Scaffold non-ACGTN (%)',
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
            'Number of contigs (split contigs)': 'Number of split contigs',
            'Total size of contigs (split contigs)': 'Total size of split contigs',
            'Longest contig (split contigs)': 'Longest split contig',
            'Shortest contig (split contigs)': 'Shortest split contig',
            'Number of contigs > 1K nt (split contigs)': 'Number of split contigs (>= 1k nt)',
            'Number of contigs > 10K nt (split contigs)': 'Number of split contigs (>= 10k nt)',
            'Number of contigs > 100K nt (split contigs)': 'Number of split contigs (>= 100k nt)',
            'Number of contigs > 1M nt (split contigs)': 'Number of split contigs (>= 1M nt)',
            'Number of contigs > 10M nt (split contigs)': 'Number of split contigs (>= 10M nt)',
            'Mean contig size (split contigs)': 'Mean split contig size',
            'Median contig size (split contigs)': 'Median split contig size',
            'contig %A (split contigs)': 'Split contig A (%)',
            'contig %C (split contigs)': 'Split contig C (%)',
            'contig %G (split contigs)': 'Split contig G (%)',
            'contig %T (split contigs)': 'Split contig T (%)',
            'contig %N (split contigs)': 'Split contig N (%)',
            'contig %non-ACGTN (split contigs)': 'Split contig non-ACGTN (%)',
            'Number of contig non-ACGTN nt (split contigs)': 'Number of split contig non-ACGTN nt'
    }
    keys = list(result.keys())
    for key in keys:
        if key in rename:
            result[rename[key]] = result[key]
            del result[key]
    remove = [
            'Average length of break (>25 Ns) between contigs in scaffold (split contigs)',
            'Average number of contigs per scaffold (split contigs)',
            'L50 contig count (split contigs)',
            'N50 contig length (split contigs)',
            'Number of contigs in scaffolds (split contigs)',
            'Number of contigs not in scaffolds (split contigs)',
            'Percentage of assembly in scaffolded contigs (split contigs)',
            'Percentage of assembly in unscaffolded contigs (split contigs)',
    ]
    for key in remove:
        if key in result:
            del result[key]
    order = [
            # scaffolds
            'Number of scaffolds',
            'Total size of scaffolds',
            'Longest scaffold',
            'Shortest scaffold',
            'Number of scaffolds (>= 1k nt)',
            'Number of scaffolds (>= 10k nt)',
            'Number of scaffolds (>= 100k nt)',
            'Number of scaffolds (>= 1M nt)',
            'Number of scaffolds (>= 10M nt)',
            'Total length of scaffolds (>= 1k nt)',
            'Total length of scaffolds (>= 10k nt)',
            'Total length of scaffolds (>= 100k nt)',
            'Total length of scaffolds (>= 1M nt)',
            'Total length of scaffolds (>= 10M nt)',
            'Mean scaffold size',
            'Median scaffold size',
            'Scaffold A (%)',
            'Scaffold C (%)',
            'Scaffold G (%)',
            'Scaffold T (%)',
            'Scaffold N (%)',
            'Scaffold non-ACGTN (%)',
            'Number of scaffold non-ACGTN nt',
            'GC contnet of scaffolds (%)',
            'N50 of scaffolds',
            'N75 of scaffolds',
            'L50 of scaffolds',
            'L75 of scaffolds',
            'Number of N per 100k nt of scaffolds',
            # contigs
            'Number of contigs',
            'Total size of contigs',
            'Longest contig',
            'Shortest contig',
            'Number of contigs (>= 1k nt)',
            'Number of contigs (>= 10k nt)',
            'Number of contigs (>= 100k nt)',
            'Number of contigs (>= 1M nt)',
            'Number of contigs (>= 10M nt)',
            'Total length of contigs (>= 1k nt)',
            'Total length of contigs (>= 10k nt)',
            'Total length of contigs (>= 100k nt)',
            'Total length of contigs (>= 1M nt)',
            'Total length of contigs (>= 10M nt)',
            'Mean contig size',
            'Median contig size',
            'Contig A (%)',
            'Contig C (%)',
            'Contig G (%)',
            'Contig T (%)',
            'Contig N (%)',
            'Contig non-ACGTN (%)',
            'Number of contig non-ACGTN nt'
            'GC contnet of contigs (%)',
            'N50 of contigs',
            'N75 of contigs',
            'L50 of contigs',
            'L75 of contigs',
            'Number of N per 100k nt of contigs',
            # split contigs
            'Number of split contigs',
            'Total size of split contigs',
            'Longest split contig',
            'Shortest split contig',
            'Number of split contigs (>= 1k nt)',
            'Number of split contigs (>= 10k nt)',
            'Number of split contigs (>= 100k nt)',
            'Number of split contigs (>= 1M nt)',
            'Number of split contigs (>= 10M nt)',
            'Total length of split contigs (>= 1k nt)',
            'Total length of split contigs (>= 10k nt)',
            'Total length of split contigs (>= 100k nt)',
            'Total length of split contigs (>= 1M nt)',
            'Total length of split contigs (>= 10M nt)',
            'Mean split contig size',
            'Median split contig size',
            'Split contig A (%)',
            'Split contig C (%)',
            'Split contig G (%)',
            'Split contig T (%)',
            'Split contig N (%)',
            'Split contig non-ACGTN (%)',
            'Number of split contig non-ACGTN nt'
            'GC content of split contigs (%)',
            'N50 of split contigs',
            'N75 of split contigs',
            'L50 of split contigs',
            'L75 of split contigs',
            'Number of N per 100k nt of split contigs',
    ]
    for o in order:
        if o in result:
            print(o + ': ' + result[o])
    return result

if __name__ == '__main__':
    result_assemblathon = run_assemblathon_stats(args.scaffolds_file, args.contigs_file)
    result_quast = run_quast(args.scaffolds_file, args.contigs_file)
    result = {**result_assemblathon, **result_quast}
    result = post_process_result(args.scaffolds_file, args.contigs_file, result)
    if args.o:
        with open(args.o[0], 'w') as f:
            f.write(json.dumps(result, sort_keys=True, indent=4))
