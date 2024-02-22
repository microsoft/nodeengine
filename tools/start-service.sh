#!/usr/bin/env bash
# Copyright (c) Microsoft. All rights reserved.

set -e

# Change current dir to repo root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && cd .. && pwd)"
cd "$ROOT"

./tools/activate-venv.sh

# Start Node Engine service
node-engine-service --registry-root examples
