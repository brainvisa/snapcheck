#!/bin/bash
# Build the HTML documentation of this project (docs/_build/html) and export it in DEST/<package>,
# where <package> is the name of the python package (pyproject.toml).
#
# Usage: scripts/export_docs.sh DEST
# A previous export of the package in DEST is replaced.
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: $0 DEST" >&2
    exit 1
fi
DEST="$(realpath -m "$1")"
cd "$(dirname "$0")/.."

NAME="$(grep -m 1 '^name = ' pyproject.toml | cut -d '"' -f 2)"

make -C docs html
rm -rf "${DEST:?}/${NAME:?}"
mkdir -p "$DEST"
cp -r docs/_build/html "$DEST/$NAME"
echo "Documentation exported in $DEST/$NAME"
