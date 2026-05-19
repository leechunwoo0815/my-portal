#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

echo $$ > /tmp/ai-portal-frontend.pid
logdir="./logs"
mkdir -p "$logdir"

npm run dev -- --host 0.0.0.0 --port 3000 \
  >> "$logdir/frontend.log" 2>&1
