#!/bin/bash
# Run just the FastAPI backend

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Starting FactTrace API on http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""

python -m uvicorn api.server:app --reload --port 8000 --host 0.0.0.0
