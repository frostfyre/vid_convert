#!/bin/bash

# Check if the user provided a directory
if [ -z "$1" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Assign the directory to a variable
directory=$1

# Find all subdirectories and count files in each
find "$directory" -type d | while read subfolder; do
    count=$(find "$subfolder" -maxdepth 1 -type f | wc -l)
    echo "$subfolder: $count files"
done
