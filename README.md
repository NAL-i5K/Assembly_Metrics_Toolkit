# Assembly Metrics Toolkit

[![Build Status](https://travis-ci.org/NAL-i5K/Assembly_Metrics_Toolkit.svg?branch=master)](https://travis-ci.org/NAL-i5K/Assembly_Metrics_Toolkit)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/485c473433484161a68b11ca734ef949)](https://www.codacy.com/app/hsiaoyi0504/Assembly_Metrics_Toolkit?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hsiaoyi0504/Assembly_Metrics_Toolkit&amp;utm_campaign=Badge_Grade)

## Prerequsite

* Perl
* Python 3.5

## Installation

`cpanm install JSON`

## Usage

``` shell
usage: python3.5 assembly_metrics_toolkit.py [-h] [-s scaffolds_file]
[-c contigs_file] [-o output_path]

Calculate various assembly metrics

optional arguments:
  -h, --help         show this help message and exit
  -s scaffolds_file  a fasta file of scaffolds (can be .gz)
  -c contigs_file    a fasta file of contigs (can be .gz)
  -o output_path     where a JSON output file will be generated at
```

## Example

### Download the example files

We are using the scaffolds and contigs of *Cimex_lectularius* provided by [i5k Workspace@NAl](https://i5k.nal.usda.gov/Cimex_lectularius).

``` shell
wget https://i5k.nal.usda.gov/data/Arthropoda/cimlec-%28Cimex_lectularius%29/Current%20Genome%20Assembly/1.Genome%20Assembly/BCM-After-Atlas/Contigs/Clec_Bbug02212013.contigs.fa.gz
wget https://i5k.nal.usda.gov/data/Arthropoda/cimlec-%28Cimex_lectularius%29/Current%20Genome%20Assembly/1.Genome%20Assembly/BCM-After-Atlas/Scaffolds/Clec_Bbug02212013.genome.fa.gz
```

### Run the script

```
python3.5 ./assembly_metrics_toolkit.py -s ./sample_data/BCM-After-Atlas/Scaffolds/Clec_Bbug02212013.genome.fa.gz -o output_1.json
python3.5 ./assembly_metrics_toolkit.py -s ./sample_data/BCM-After-Atlas/Scaffolds/Clec_Bbug02212013.genome.fa.gz  -c ./sample_data/BCM-After-Atlas/Contigs/Clec_Bbug02212013.contigs.fa.gz -o output_2.json
```

These commands will generate two json files, which are the same as [example_scaffolds_only.json](example/example_scaffolds_only.json) and [example_scaffolds_and_contigs.json](example/example_scaffolds_and_contigs.json), respectively.

## Acknowledgement

 * `assemblathon_stats.pl` and `FAlite.pm` are from [ucdavis-bioinformatics/assemblathon2-analysis](https://github.com/ucdavis-bioinformatics/assemblathon2-analysis) GitHub Repo.
 * `asm2stats.minmaxgc.pl` is from [rjchallis/assembly-stats](https://github.com/rjchallis/assembly-stats) GitHub Repo, and is modified to also support `.gz` input fasta file.
