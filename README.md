# Assembly Metrics Toolkit

[![Build Status](https://travis-ci.org/NAL-i5K/Assembly_Metrics_Toolkit.svg?branch=master)](https://travis-ci.org/NAL-i5K/Assembly_Metrics_Toolkit)
[![Build status](https://ci.appveyor.com/api/projects/status/pnflujnpvf6v7ilj/branch/master?svg=true)](https://ci.appveyor.com/project/hsiaoyi0504/assembly-metrics-toolkit/branch/master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/76c8df26e1bf4888833a95c616bbe99c)](https://www.codacy.com/app/NAL-i5K/Assembly_Metrics_Toolkit?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=NAL-i5K/Assembly_Metrics_Toolkit&amp;utm_campaign=Badge_Grade)

## Prerequisite

* Perl
  * Cpanm
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

We are using the scaffolds and contigs of *Athalia rosae* provided by [i5k Workspace@NAl](https://i5k.nal.usda.gov/Athalia_rosae).

``` shell
wget "https://i5k.nal.usda.gov/data/Arthropoda/athros-(Athalia_rosae)/BCM-After-Atlas/1.Genome%20Assembly/BCM-After-Atlas/Contigs/Aros01112013-contigs.fa.gz"
wget "https://i5k.nal.usda.gov/data/Arthropoda/athros-(Athalia_rosae)/BCM-After-Atlas/1.Genome%20Assembly/BCM-After-Atlas/Scaffolds/Aros01112013-genome.fa.gz"
```

### Run the script

``` shell
python ./assembly_metrics_toolkit.py -s ./Aros01112013-genome.fa.gz -o example_scaffolds_only.json
python ./assembly_metrics_toolkit.py -s ./Aros01112013-genome.fa.gz -c ./Aros01112013-contigs.fa.gz -o example_scaffolds_and_contigs.json
```

These commands will generate two json files, which are the same as [example_scaffolds_only.json](example/example_scaffolds_only.json) and [example_scaffolds_and_contigs.json](example/example_scaffolds_and_contigs.json), respectively.

These json files can be further visualized through [Assembly_Metrics_Visualization](https://github.com/NAL-i5K/Assembly_Metrics_Visualization).

## Acknowledgement

* `assemblathon_stats.pl` and `FAlite.pm` are from [ucdavis-bioinformatics/assemblathon2-analysis](https://github.com/ucdavis-bioinformatics/assemblathon2-analysis) GitHub Repo.
* `asm2stats.minmaxgc.pl` is from [rjchallis/assembly-stats](https://github.com/rjchallis/assembly-stats) GitHub Repo, and is modified to also support `.gz` input fasta file.
