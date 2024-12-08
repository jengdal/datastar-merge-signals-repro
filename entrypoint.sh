#!/bin/sh

cd merge
uv run fastapi dev merge.py --host 0.0.0.0 --port 8082 --no-reload
