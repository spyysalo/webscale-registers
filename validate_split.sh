#!/bin/bash

# Vvalidate HPLT data package split.

set -euo pipefail

source common.sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 PACKAGE" >&2
    echo >&2
    echo "example: $0 cleaned/eng_Latn/1.jsonl.zst" >&2
    exit 1
fi

PACKAGE="$1"

get_lock "$PACKAGE"

STATS_PATH="$STATS_BASE_DIR/${PACKAGE%%.*}.txt"
LINE_COUNT=$(awk '{ print $1 }' "$STATS_PATH")

SPLIT_DIR="$SPLIT_BASE_DIR/${PACKAGE%%.*}"
SPLIT_COUNT=$(find "$SPLIT_DIR" -name '*.jsonl' | wc -l)

echo -n "Validating $SPLIT_DIR ... "

if [ $SPLIT_COUNT -ne $SPLIT_PARTS ]; then
    echo "Error: split file count mismatch ($SPLIT_COUNT vs $SPLIT_PARTS)" >&2
    echo >&2
    echo "You may want to delete $SPLIT_DIR and rerun." >&2
    exit 1
fi

SPLIT_TOTAL_LINES=$(find "$SPLIT_DIR" -name '*.jsonl' | xargs cat | wc -l)

if [ $SPLIT_TOTAL_LINES -ne $LINE_COUNT ]; then
    echo "Error: split line count mismatch ($SPLIT_TOTAL_LINES vs $LINE_COUNT)" >&2
    echo >&2
    echo "You may want to delete $SPLIT_DIR and rerun." >&2
    exit 1
fi

echo "OK ($SPLIT_TOTAL_LINES lines)"
