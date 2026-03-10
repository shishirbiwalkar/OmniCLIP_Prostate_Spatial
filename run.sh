#!/bin/bash
# OmniCLIP - One-line pipeline runner
# Usage: ./run.sh [setup|annotate|embed]
cd "$(dirname "$0")"
python run.py "${1:-annotate}"
