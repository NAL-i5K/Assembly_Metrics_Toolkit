# Assembly Metrics Toolkit

[![Build Status](https://travis-ci.org/NAL-i5K/Assembly_Metrics_Toolkit.svg?branch=master)](https://travis-ci.org/NAL-i5K/Assembly_Metrics_Toolkit)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/76c8df26e1bf4888833a95c616bbe99c)](https://www.codacy.com/app/NAL-i5K/Assembly_Metrics_Toolkit?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=NAL-i5K/Assembly_Metrics_Toolkit&amp;utm_campaign=Badge_Grade)

## Prerequisite

* Perl
* Python 2.7 or 3.5

## Installation

`cpanm --installdeps .`

## Usage

``` shell
usage: python assembly_metrics_toolkit.py [-h] [-s scaffolds_file]
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

We are using the scaffolds and contigs of *Agrilus planipennis* provided by [i5k Workspace@NAl](https://i5k.nal.usda.gov/Agrilus_planipennis).

``` shell
wget https://i5k.nal.usda.gov/sites/default/files/data/Arthropoda/agrpla-%28Agrilus_planipennis%29/BCM-After-Atlas/1.Genome%20Assembly/BCM-After-Atlas/Contigs/Aplan.contigs.80.fa.gz
wget https://i5k.nal.usda.gov/sites/default/files/data/Arthropoda/agrpla-%28Agrilus_planipennis%29/BCM-After-Atlas/1.Genome%20Assembly/BCM-After-Atlas/Scaffolds/Aplan.scaffolds.50.fa.gz
```

### Run the script

``` shell
python ./assembly_metrics_toolkit.py -s ./Aplan.scaffolds.50.fa.gz -o example_scaffolds_only.json
python ./assembly_metrics_toolkit.py -s ./Aplan.scaffolds.50.fa.gz  -c ./Aplan.contigs.80.fa.gz -o example_scaffolds_and_contigs.json
```

These commands will generate two json files, which are the same as [example_scaffolds_only.json](example/example_scaffolds_only.json) and [example_scaffolds_and_contigs.json](example/example_scaffolds_and_contigs.json), respectively.

These json files can be further visualized through [Assembly_Metrics_Visualization](https://github.com/NAL-i5K/Assembly_Metrics_Visualization).

## Acknowledgement

* `assemblathon_stats.pl` and `FAlite.pm` are from [ucdavis-bioinformatics/assemblathon2-analysis](https://github.com/ucdavis-bioinformatics/assemblathon2-analysis) GitHub Repo.
* `asm2stats.minmaxgc.pl` is from [rjchallis/assembly-stats](https://github.com/rjchallis/assembly-stats) GitHub Repo, and is modified to also support `.gz` input fasta file.
