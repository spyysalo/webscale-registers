#!/bin/bash

# Vvalidate HPLT data package split.

set -euo pipefail

source common.sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 PACKAGE" >&2
    echo >&2
    echo "example: $0 cleaned/eng_Latn/1" >&2
    exit 1
fi

PACKAGE="$1"

get_lock "$PACKAGE"

STATS_PATH="$STATS_BASE_DIR/${PACKAGE%%.*}.txt"
LINE_COUNT=$(awk '{ print $1 }' "$STATS_PATH")

PREDICT_DIR="$PREDICT_BASE_DIR/${PACKAGE%%.*}"
PREDICT_COUNT=$(find "$PREDICT_DIR" -name '*.jsonl' | wc -l)

echo -n "Validating $PREDICT_DIR ... "

if [ $PREDICT_COUNT -ne $SPLIT_PARTS ]; then
    echo "Error: predicted file count mismatch ($PREDICT_COUNT vs $SPLIT_PARTS)" >&2
    echo >&2
    echo "You may want to delete $SPLIT_DIR and rerun." >&2
    exit 1
fi

PREDICT_TOTAL_LINES=$(find "$PREDICT_DIR" -name '*.jsonl' | xargs cat | wc -l)

if [ $PREDICT_TOTAL_LINES -ne $LINE_COUNT ]; then
    echo "Error: predicted line count mismatch ($PREDICT_TOTAL_LINES vs $LINE_COUNT)" >&2
    echo >&2
    echo "You may want to delete $PREDICT_DIR and rerun." >&2
    exit 1
fi

echo "OK ($PREDICT_TOTAL_LINES lines)"
