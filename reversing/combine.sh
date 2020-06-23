#!/bin/bash

files="SPHOST.header offset0 offset1 offset2.header offset2.A offset2.B offset3 offset5 offset6"
outfile="SPHOST.BRN.new"

if [[ -z "$1" ]]; then
    echo "Usage: $0 <files in order to append...>"
    echo "Using default files"
else
    files="$@"
fi

echo "Combining $files"

[ -e "$outfile" ] && rm "$outfile"
for f in $files; do
    cat $f >> "$outfile"
done
