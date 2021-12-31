#!/bin/sh
set -e

PYCRC=`dirname $0`/../pycrc.py
outdir_old="/tmp/pycrc_out"
outdir_new="/tmp/pycrc_new"
tarfile="pycrc_files.tar.gz"

usage() {
        echo >&2 "usage: $0 [OPTIONS]"
        echo >&2 ""
        echo >&2 "with OPTIONS in"
        echo >&2 "        -c    check the generated output"
        echo >&2 "        -g    generate the database"
        echo >&2 "        -n    no cleanup: don't delete the directories with the generated code"
        echo >&2 "        -h    this help message"
}


opt_check=off
opt_no_cleanup=off
opt_generate=off

while getopts cgnh opt; do
    case "$opt" in
        c)  opt_check=on;;
        g)  opt_generate=on;;
        n)  opt_no_cleanup=on;;
        h)  usage
            exit 0
            ;;
        \?) usage       # unknown flag
            exit 1
            ;;
    esac
done
shift `expr $OPTIND - 1`

if [ -e "$outdir_old" ]; then
    echo >&2 "Output directory $outdir_old exists!"
    exit 1
fi
if [ -e "$outdir_new" ]; then
    echo >&2 "Output directory $outdir_new exists!"
    exit 1
fi


cleanup() {
    if [ "$opt_no_cleanup" = "on" ]; then
        echo "No cleanup. Please delete $outdir_old and $outdir_new when you're done"
    else
        rm -rf "$outdir_old" "$outdir_new"
    fi
}

trap cleanup 0 1 2 3 15


populate() {
    outdir=$1
    mkdir -p "$outdir"
    models=`awk 'BEGIN { FS="'"'"'" } $2 == "name" && $3 ~ /^: */ { print $4 }' ../crc_models.py`
    for m in $models; do
        for algo in "bit-by-bit" "bit-by-bit-fast" "bitwise-expression" "table-driven"; do
            $PYCRC --model $m --algorithm $algo --generate h -o "${outdir}/${m}_${algo}.h"
            $PYCRC --model $m --algorithm $algo --generate c -o "${outdir}/${m}_${algo}.c"
            sed -i -e 's/Generated on ... ... .. ..:..:.. ....,/Generated on XXX XXX XX XX:XX:XX XXXX,/; s/by pycrc v[0-9.]*/by pycrc vXXX/;' "${outdir}/${m}_${algo}.h"
            sed -i -e 's/Generated on ... ... .. ..:..:.. ....,/Generated on XXX XXX XX XX:XX:XX XXXX,/; s/by pycrc v[0-9.]*/by pycrc vXXX/;' "${outdir}/${m}_${algo}.c"
        done
    done
}

do_check() {
    tar xzf "$tarfile" -C "`dirname $outdir_new`"
    populate "$outdir_new"
    diff -ru "$outdir_old" "$outdir_new"
}


if [ "$opt_check" = "on" ]; then
    if [ ! -f "$tarfile" ]; then
        echo >&2 "Can't find tarfile $tarfile"
        exit 1
    fi
    do_check
fi

if [ "$opt_generate" = "on" ]; then
    populate "$outdir_old"
    dirname="`dirname $outdir_old`"
    basename="`basename $outdir_old`"
    tar czf "$tarfile" -C "$dirname" "$basename"
fi
