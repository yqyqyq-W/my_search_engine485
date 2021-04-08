#!/bin/bash
#
# Example of how to chain mapreduce jobs together.  The output of one
# job is the input to the next.
#
# Hadoop options
# jar index/hadoop/hadoop-streaming-2.7.2.jar   # Hadoop configuration
# -input <directory>                            # Input directory
# -output <directory>                           # Output directory
# -mapper <exec_name>                           # Mapper executable
# -reducer <exec_name>                          # Reducer executable

# Stop on errors
# See https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
set -Eeuo pipefail

# Remove first output directory, if it exists
rm -rf output1

# Run first MapReduce job
hadoop \
  jar ../hadoop-streaming-2.7.2.jar \
  -input input \
  -output output1 \
  -mapper ./somemap.py \
  -reducer ./somereduce.py \

# Remove second output directory, if it exists
rm -rf output2

# Run second MapReduce job
hadoop \
  jar hadoop-streaming-2.7.2.jar \
  -input output1 \
  -output output2 \
  -mapper ./somemap.py \
  -reducer ./somereduce.py
