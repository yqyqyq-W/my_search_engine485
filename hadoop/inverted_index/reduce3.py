#!/usr/bin/env python3
"""Reduce 3."""

import sys

# format: <word> <idf> <docid> <count> <sum> <docid> ....\n
last_word = ""
last_word_info = ""
for line in sys.stdin:
    line = line.split("\n")[0]
    word = line.split("\t")[0]
    idf = (line.split("\t")[1]).split(" ")[0]
    doc_info = (line.split("\t")[1]).split(" ")[1:]
    doc_info = doc_info[0] + " " + doc_info[1] + " " + doc_info[2]
    if word == last_word:
        last_word_info = last_word_info + " " + doc_info
    else:
        if last_word != "":
            sys.stdout.write(last_word + " " + last_word_info + "\n")
        last_word = word
        last_word_info = idf + " " + doc_info

sys.stdout.write(last_word + " " + last_word_info + "\n")
