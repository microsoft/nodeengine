#!/usr/bin/env bash

set -e

# Change current dir to repo root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && cd .. && pwd)"
cd "$ROOT"

# Check whether to use "python" or "python3"
python_cmd=$(command -v python3 &> /dev/null && echo "python3" || echo "python")

# Activate virtual environment
if [ ! -d "${ROOT}/.venv" ]; then
    echo "${ROOT}/.venv directory not found"
    exit 1
else
    source ${ROOT}/.venv/bin/activate
fi

# Start Node Engine service
$python_cmd -m node_engine.start --local_files_root examples
