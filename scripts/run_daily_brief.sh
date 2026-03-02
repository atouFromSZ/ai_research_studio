#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

source .venv/bin/activate
PYTHONPATH=src python -m ai_research_studio.cli daily-brief