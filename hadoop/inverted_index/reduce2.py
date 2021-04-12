#!/usr/bin/env python3
"""Reduce 2."""

import sys

sum_dict = {}
line_arr = []
for line in sys.stdin:
    line_arr.append(line)
    doc = line.split("\t")[0]
    idf = float((line.split("\t")[1]).split(" ")[1])
    count = int((line.split("\t")[1]).split(" ")[2])
    tmp = (idf ** 2) * count ** 2
    if doc in sum_dict:
        sum_dict[doc] += tmp
    else:
        sum_dict[doc] = tmp

# format: <docid>\t<normalized sum> <word> <idf> <count>
for line in line_arr:
    doc = line.split("\t")[0]
    sys.stdout.write(doc + "\t" + str(sum_dict[doc]) + " "
                     + line.split("\t")[1])
