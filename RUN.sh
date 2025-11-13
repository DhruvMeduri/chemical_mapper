#!/bin/bash
python3 mapper-interactive-cli.py ./CLI_examples/smiles_scaffolds_3_5000.csv --intervals 50:50:1 --overlaps 50:50:1 --clusterer dbscan --eps 2.5 --min_samples 2 --filter l2norm -output ./CLI_examples
