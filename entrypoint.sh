#!/bin/bash

# Check if no arguments are passed
if [ $# -eq 0 ]; then
    echo "Usage: $0 [gdb_remote | gdb_coredump] [arguments...]"
    exit 1
fi

# Determine the script to run based on the first argument

case "$1" in
    gdb_remote)
        echo "Running gdb_remote.py..."
        python3 gdb_remote.py "${@:2}"
        ;;
    gdb_coredump)
        echo "Running gdb_coredump.py..."
        python3 gdb_coredump.py "${@:2}"
        ;;
    *)
        echo "Error: Unknown script name '$1'."
        echo "Showing help for both scripts:"
        echo "-------------------------------------------------------------- help of gdb_remote.py"
        python3 gdb_remote.py --help
        echo "-------------------------------------------------------------- help of gdb_coredump.py"
        echo "gdb_coredump.py --help:"
        python3 gdb_coredump.py --help
        exit 1
        ;;
esac
