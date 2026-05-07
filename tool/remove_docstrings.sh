#!/bin/bash
# Copyright (c) Meta Platforms, Inc. and affiliates

# Shell script wrapper for the remove_docstrings.py tool

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Show usage
function show_usage {
    echo "Usage: $(basename $0) [options] DIRECTORY"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -d, --dry-run  Perform a dry run (no changes are made)"
    echo "  -b, --backup   Create backup files before making changes"
    echo ""
    echo "Example:"
    echo "  $(basename $0) ~/my-python-project"
    echo "  $(basename $0) --dry-run ~/my-python-project"
    exit 1
}

# Parse arguments
DRY_RUN=""
BACKUP=false
DIRECTORY=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            ;;
        -d|--dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        -b|--backup)
            BACKUP=true
            shift
            ;;
        *)
            if [[ -z "$DIRECTORY" ]]; then
                DIRECTORY="$1"
            else
                echo "Error: Too many arguments"
                show_usage
            fi
            shift
            ;;
    esac
done

# Check if directory is provided
if [[ -z "$DIRECTORY" ]]; then
    echo "Error: No directory specified"
    show_usage
fi

# Check if directory exists
if [[ ! -d "$DIRECTORY" ]]; then
    echo "Error: Directory does not exist: $DIRECTORY"
    exit 1
fi

# Create backups if requested
if [[ "$BACKUP" = true ]]; then
    echo "Creating backups of Python files..."
    find "$DIRECTORY" -name "*.py" -type f -exec cp {} {}.bak \;
    echo "Backups created with .bak extension"
fi

# Run the Python script
python3 "$SCRIPT_DIR/remove_docstrings.py" $DRY_RUN "$DIRECTORY"

echo "Done!" 