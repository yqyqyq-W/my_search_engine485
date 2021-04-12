#!/usr/bin/env python3
"""Map 2."""

import sys

# format: <docid>\t<word> <idf> <count>
for line in sys.stdin:
    keys = line.split("\t")
    for i in range(2, len(keys)):
        sys.stdout.write((keys[i]).split()[0] + "\t" + keys[0]
                         + " " + keys[1] + " " + (keys[i]).split()[1] + "\n")
