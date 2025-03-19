#!/bin/bash
# Script to run venvkiller in development mode

cd "$(dirname "$0")"
source .venv/bin/activate

# Install in development mode if not already
if ! pip show venvkiller >/dev/null 2>&1; then
  echo "Installing venvkiller in development mode..."
  pip install -e .
fi

# Run venvkiller
echo "Starting venvkiller..."
python -m venvkiller.cli "$@" 