#!/usr/bin/python3.5
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
        result = process_assemblathon_stats(p.stdout, 'scaffolds-only')
    else:
        result_scaffolds = process_assemblathon_stats(p.stdout, 'scaffolds-only')
        p = subprocess.run(['./assemblathon_stats.pl', scaffolds_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        result_contigs = process_assemblathon_stats(p.stdout, 'contigs-only')
        result = {**result_scaffolds, **result_contigs}
    return result

def run_asm2stats(scaffolds_file):
    p = subprocess.run(['./asm2stats.minmaxgc.pl', scaffolds_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    result = json.loads(p.stdout)
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
            if 'contigs' in k or 'Contigs' in k or 'contig' in k or 'Contig' in k:
                del result[k]
    else: # type == 'contigs-only'
        keys = list(result.keys())
        for k in keys:
            if 'scaffolds' in k or 'Scaffolds' in k or 'scaffold' in k or 'Scaffold' in k:
                del result[k]
    return result

def post_process_result(scaffolds_file, contigs_file, result):
    rename = {
            'N50 scaffold length': 'N50 of scaffolds',
            'L50 scaffold count': 'L50 of scaffolds',
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
    keys = list(result.keys())
    for key in keys:
        if key in rename:
            result[rename[key]] = result[key]
            del result[key]
    remove = [
    ]
    for key in remove:
        if key in result:
            del result[key]
    if 'GC content of scaffolds (%)' not in result:
        gc_ratio = float(result['Scaffold C (%)']) + float(result['Scaffold G (%)'])
        not_n_ratio = gc_ratio + float(result['Scaffold T (%)']) + float(result['Scaffold A (%)'])
        result['GC content of scaffolds (%)'] = str(round( gc_ratio / not_n_ratio * 100, 2))
    if contigs_file is not None and 'GC content of contigs (%)' not in result:
        gc_ratio = float(result['Contig C (%)']) + float(result['Contig G (%)'])
        not_n_ratio = gc_ratio + float(result['Contig T (%)']) + float(result['Contig A (%)'])
        result['GC content of contigs (%)'] = str(round( gc_ratio / not_n_ratio * 100, 2))
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
            'Mean scaffold size',
            'Median scaffold size',
            'Scaffold A (%)',
            'Scaffold C (%)',
            'Scaffold G (%)',
            'Scaffold T (%)',
            'Scaffold N (%)',
            'Scaffold non-ACGTN (%)',
            'Number of scaffold non-ACGTN nt',
            'GC content of scaffolds (%)',
            'N50 of scaffolds',
            'L50 of scaffolds',
    ]
    if contigs_file is not None:
        order += [
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
                'Mean contig size',
                'Median contig size',
                'Contig A (%)',
                'Contig C (%)',
                'Contig G (%)',
                'Contig T (%)',
                'Contig N (%)',
                'Contig non-ACGTN (%)',
                'Number of contig non-ACGTN nt'
                'GC content of contigs (%)',
                'N50 of contigs',
                'L50 of contigs',
        ]
    for o in order:
        if o in result:
            print(o + ': ' + result[o])
    return result

if __name__ == '__main__':
    result_assemblathon = run_assemblathon_stats(args.scaffolds_file, args.contigs_file)
    result_asm2stats = run_asm2stats(args.scaffolds_file)
    result = {**result_assemblathon, **result_asm2stats}
    result = post_process_result(args.scaffolds_file, args.contigs_file, result)
    if args.o:
        with open(args.o[0], 'w') as f:
            f.write(json.dumps(result, sort_keys=True, indent=4))
    

