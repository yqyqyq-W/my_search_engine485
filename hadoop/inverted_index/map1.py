#!/usr/bin/env python3
"""Map 1."""

import csv
import sys
import re

file = open("stopwords.txt", 'r')
stopwords = set(file.readlines())
file.close()
csv.field_size_limit(sys.maxsize)


def word_process(words, filename):
    """Word process."""
    for tmp in words.split():
        tmp = re.sub(r'[^a-zA-Z0-9]+', '', tmp).lower().split()
        for word in tmp:
            if word+"\n" not in stopwords:
                sys.stdout.write(word + "\t" + filename + " 1\n")


for line in csv.reader(sys.stdin):
    word_process(line[1], line[0])
    word_process(line[2], line[0])

