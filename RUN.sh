#!/bin/bash
python3 mapper-interactive-cli.py ./CLI_examples/test.csv --intervals 50:50:1 --overlaps 60:60:1 --clusterer dbscan --eps 2 --min_samples 4 --filter l2norm -output ./CLI_examples
