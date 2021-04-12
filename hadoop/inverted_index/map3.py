#!/usr/bin/env python3
"""Map 3."""

import sys

# format: <word>\t<idf> <doc> <count> <normalized sum>\n
for line in sys.stdin:
    word = (line.split("\t")[1]).split(" ")[1]
    idf = (line.split("\t")[1]).split(" ")[2]
    doc = line.split("\t")[0]
    count = ((line.split("\t")[1]).split(" ")[3]).split("\n")[0]
    normalized_sum = (line.split("\t")[1]).split(" ")[0]
    sys.stdout.write(word + "\t" + idf + " " + doc + " " +
                     count + " " + normalized_sum + "\n")
