#!/usr/bin/env python3
"""Reduce 1."""
import sys
import math

file = open("total_document_count.txt", "r")
doc_count = int((file.readline()).split("\n")[0])
file.close()
# format: key: word\t<docid>, val: count
key_dict = {}
for line in sys.stdin:
    key = line.split(" ")[0]
    if key in key_dict:
        key_dict[key] += 1
    else:
        key_dict[key] = 1

# format: word\t<docid> <count>\t<docid> <count>...
word_dict = {}
for key in key_dict:
    word = key.split("\t")[0]
    if word in word_dict:
        word_dict[word] = word_dict[word] + "\t" + \
                          key.split("\t")[1] + " " + str(key_dict[key])
    else:
        word_dict[word] = "\t" + key.split("\t")[1] + " " + str(key_dict[key])

for key in word_dict:
    val = word_dict[key]
    nk = val.count("\t")
    idf = math.log(doc_count/nk, 10)
    word_dict[key] = "\t" + str(idf) + word_dict[key]

# format: word\t<idf>\t<docid> <count>\t<docid> <count>...\n
for key in word_dict:
    sys.stdout.write(key + word_dict[key] + "\n")
