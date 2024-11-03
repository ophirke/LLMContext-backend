#!/usr/bin/env bash

source .venv/bin/activate

python3 init_db.py

fastapi dev backend.py