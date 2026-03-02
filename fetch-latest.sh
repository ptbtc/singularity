#!/bin/bash
# Auto-fetch latest Innermost Loop posts and add to data.json
# Run daily via cron

set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
DATA="$DIR/data.json"

echo "[$(date)] Checking for new posts..."

# Get existing dates
EXISTING=$(python3 -c "
import json
with open('$DATA') as f:
    for e in json.load(f):
        print(e['date'])
")

# Try fetching the latest post page to find new dates
# The archive page lists recent posts
ARCHIVE=$(curl -sL "https://theinnermostloop.substack.com/p/welcome-to-$(date +%B | tr '[:upper:]' '[:lower:]')-$(date +%-d)-$(date +%Y)" 2>/dev/null || echo "")

if echo "$ARCHIVE" | grep -q "Page not found"; then
    echo "No post for today yet."
else
    echo "Post may exist for today. Manual processing needed."
    echo "Run the enrichment manually or wait for the cron agent."
fi

echo "Done."
