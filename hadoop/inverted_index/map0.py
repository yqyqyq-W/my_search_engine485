#!/usr/bin/env python3
"""Map 0."""

import csv
import sys

csv.field_size_limit(sys.maxsize)

for line in csv.reader(sys.stdin):
    sys.stdout.write("doc\t1\n")
