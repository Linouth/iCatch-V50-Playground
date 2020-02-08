#!/bin/bash

files="SPHOST_header offset0 offset1 offset2 offset3 offset5 offset6"
outfile="SPHOST.BRN"

if [[ -z "$1" ]]; then
    echo "Usage: $0 <files in order to append...>"
    echo "Using default files"
else
    files="$@"
fi

# files="SPHOST_header offset0 offset1 offset2_header offset2.fat offset3 offset5 offset6"
echo "Combining $files"

[ -e "$outfile" ] && rm "$outfile"
for f in $files; do
    cat $f >> "$outfile"
done
