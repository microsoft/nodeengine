#!/usr/bin/env bash
# Copyright (c) Microsoft. All rights reserved.

# invoke this script in the current shell using `source .activate-venv.sh` (from any folder)

# Change current dir to repo root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && cd .. && pwd)"

# Activate virtual environment
if [ ! -d "${ROOT}/.venv" ]; then
    echo "${ROOT}/.venv directory not found"
    exit 1
else
    source ${ROOT}/.venv/bin/activate
fi
