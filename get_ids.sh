#!/bin/bash

# Download, validate and get document IDs from HPLT data package.

set -euo pipefail

source common.sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 PACKAGE" >&2
    echo >&2
    echo "example: $0 deduplicated/eng_Latn/1.jsonl.zst" >&2
    exit 1
fi

PACKAGE="$1"
get_lock "$PACKAGE"

ID_PATH="$ID_BASE_DIR/${PACKAGE%%.*}.txt.zst"
if [ -e "$ID_PATH" ]; then
    echo "$ID_PATH exists, exiting." >&2
    exit 1
fi

LOG_PATH="$LOG_BASE_DIR/${PACKAGE%%.*}.txt"
mkdir -p $(dirname "$LOG_PATH")

echo "$(date): START RUNNING get_ids.sh" >> "$LOG_PATH"

cat <<EOF

------------------------------------------------------------------------------
Download source package
------------------------------------------------------------------------------
EOF

URL="$BASE_URL/$PACKAGE"
DOWNLOAD_PATH="$DOWNLOAD_BASE_DIR/$PACKAGE"
mkdir -p "$(dirname "$DOWNLOAD_PATH")"

if [ -e "$DOWNLOAD_PATH" ]; then
    echo "$DOWNLOAD_PATH exists, skipping download."
else
    echo "Downloading $URL to $DOWNLOAD_PATH ..."
    echo "$(date): START download" >> "$LOG_PATH"
    wget "$URL" -O "$DOWNLOAD_PATH" --no-clobber
    echo "$(date): END download" >> "$LOG_PATH"
    echo "Done downloading."
fi

cat <<EOF

------------------------------------------------------------------------------
Validate source package checksum
------------------------------------------------------------------------------
EOF

echo "Validating checksum for $DOWNLOAD_PATH ..."
CHECKSUM_URL="$URL.md5"
SOURCE_CHECKSUM="$(curl -s "$CHECKSUM_URL" | awk '{ print $1 }')"

echo "$(date): START checksum" >> "$LOG_PATH"
LOCAL_CHECKSUM="$(time md5sum "$DOWNLOAD_PATH" | awk '{ print $1 }')"
echo "$(date): END checksum" >> "$LOG_PATH"

if [ "$SOURCE_CHECKSUM" != "$LOCAL_CHECKSUM" ]; then
    echo "Error: checksum mismatch ($SOURCE_CHECKSUM vs $LOCAL_CHECKSUM)" >&2
    echo >&2
    echo "You may want to delete $DOWNLOAD_PATH and rerun." >&2
    exit 1
fi
echo "Done validating checksum."

cat <<EOF

------------------------------------------------------------------------------
Get source package statistics
------------------------------------------------------------------------------
EOF

STATS_PATH="$STATS_BASE_DIR/${PACKAGE%%.*}.txt"
mkdir -p "$(dirname "$STATS_PATH")"

if [ -s "$STATS_PATH" ]; then
   echo "$STATS_PATH exists, skipping taking statistics."
else
    echo "Taking statistics for $DOWNLOAD_PATH to $STATS_PATH ..."
    echo "$(date): START stats" >> "$LOG_PATH"
    time zstdcat "$DOWNLOAD_PATH" | wc > "$STATS_PATH"
    echo "$(date): END stats" >> "$LOG_PATH"
    echo "Done taking statistics."
fi

LINE_COUNT=$(awk '{ print $1 }' "$STATS_PATH")
WORD_COUNT=$(awk '{ print $2 }' "$STATS_PATH")
CHAR_COUNT=$(awk '{ print $3 }' "$STATS_PATH")
echo "$DOWNLOAD_PATH: $LINE_COUNT lines, $WORD_COUNT words, $CHAR_COUNT chars"

cat <<EOF

------------------------------------------------------------------------------
Get IDs
------------------------------------------------------------------------------
EOF

ID_PATH="$ID_BASE_DIR/${PACKAGE%%.*}.txt.zst"
mkdir -p "$(dirname "$ID_PATH")"

if [ -s "$ID_PATH" ]; then
   echo "$ID_PATH exists, skipping taking statistics."
else
    echo "Getting IDs from $DOWNLOAD_PATH to $ID_PATH ..."
    echo "$(date): START get ids" >> "$LOG_PATH"
    time python3 get_ids.py "$DOWNLOAD_PATH" | zstd -o "$ID_PATH"
    echo "$(date): END get ids" >> "$LOG_PATH"
    echo "Done getting IDs."
fi

cat <<EOF

------------------------------------------------------------------------------
Validate IDs
------------------------------------------------------------------------------
EOF

echo "Checking ID count in $ID_PATH ..."
echo "$(date): START id count" >> "$LOG_PATH"
ID_COUNT=$(zstdcat "$ID_PATH" | wc -l)
echo "$(date): END id count" >> "$LOG_PATH"

if [ $ID_COUNT -ne $LINE_COUNT ]; then
    echo "Error: id count mismatch ($ID_COUNT vs $LINE_COUNT)" >&2
    echo >&2
    echo "You may want to delete $ID_PATH and rerun." >&2
    exit 1
fi
echo "Done checking ID count."
echo "$ID_PATH: $ID_COUNT IDs"

cat <<EOF

------------------------------------------------------------------------------
Remove downloaded data
------------------------------------------------------------------------------
EOF

echo "$(date): START remove download" >> "$LOG_PATH"
rm -rf "$DOWNLOAD_PATH"
echo "$(date): END remove download" >> "$LOG_PATH"

echo "$(date): END RUNNING get_ids.sh" >> "$LOG_PATH"
