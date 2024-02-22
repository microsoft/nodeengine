#!/usr/bin/env bash

set -e

# Change current dir to repo root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && cd ../../.. && pwd)"
cd "$ROOT"

./tools/activate-venv.sh

# Start the app under examples/apps/simple-chat-client
uvicorn examples.apps.simple-chat-client.app:app --reload
