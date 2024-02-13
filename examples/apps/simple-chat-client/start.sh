#!/usr/bin/env bash

set -e

# Change current dir to repo root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && cd ../../.. && pwd)"
cd "$ROOT"

# Activate virtual environment
if [ ! -d "${ROOT}/.venv" ]; then
    echo "${ROOT}/.venv directory not found"
    exit 1
else
    source ${ROOT}/.venv/bin/activate
fi

# Start the app under examples/apps/simple-chat-client
uvicorn examples.apps.simple-chat-client.app:app --reload
