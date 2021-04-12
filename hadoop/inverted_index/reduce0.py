#!/usr/bin/env python3
"""Reduce 0."""
import sys

result = 0
for line in sys.stdin:
    result += 1

sys.stdout.write(str(result) + "\t \n")
with open("total_document_count.txt", "w") as file:
    file.write(str(result) + "\n")
