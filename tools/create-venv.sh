#!/usr/bin/env bash
# Copyright (c) Microsoft. All rights reserved.

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && cd .. && pwd)"
cd "$ROOT"

python_cmd=$(command -v python3 &> /dev/null && echo "python3" || echo "python")

$python_cmd -m venv .venv
