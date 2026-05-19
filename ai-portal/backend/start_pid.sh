#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo $$ > /tmp/ai-portal-backend.pid
logdir="./logs"
mkdir -p "$logdir"

exec uvicorn app.main:app \
  --host 0.0.0.0 --port 8000 \
  --reload \
  --timeout-keep-alive 300 \
  >> "$logdir/backend.log" 2>&1
