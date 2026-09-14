#!/usr/bin/env bash
set -euo pipefail

python scripts/seed_demo_data.py
python -m streamlit run app/streamlit_app.py
