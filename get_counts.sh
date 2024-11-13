#!/bin/bash

# Get label counts from predictions.

set -euo pipefail

source common.sh

THRESHOLDS=$(seq 0.30 0.01 0.50 | tr '\n' ',' | perl -pe 's/,$//' 2>/dev/null)

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 PACKAGE" >&2
    echo >&2
    echo "example: $0 deduplicated/eng_Latn/1" >&2
    exit 1
fi

PACKAGE="$1"
get_lock "$PACKAGE"

COUNT_PATH="$COUNT_BASE_DIR/${PACKAGE%%.*}.json"
mkdir -p "$(dirname "$COUNT_PATH")"
if [ -e "$COUNT_PATH" ]; then
    echo "$COUNT_PATH exists, exiting." >&2
    exit 1
fi

PREDICT_DIR="$PREDICT_BASE_DIR/${PACKAGE%%.*}"

echo "Getting counts from $PREDICT_DIR to $COUNT_PATH ... "

time python3 label_counts.py \
     --thresholds "$THRESHOLDS" \
     "$PREDICT_DIR/"*.jsonl \
     > "$COUNT_PATH"

echo "Done getting counts from $PREDICT_DIR to $COUNT_PATH."
