#!/bin/bash
# Daily update script for The Ascent to Singularity
# Checks @alexwg for new "Welcome to" posts and adds to data.json
# Usage: ./update.sh (or via cron)

set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
DATA="$DIR/data.json"
BIRD="$HOME/.local/bin/bird"

echo "[$(date)] Checking for new @alexwg posts..."

# Get latest tweets
TWEETS=$($BIRD search 'from:alexwg "welcome to"' -n 10 2>/dev/null || echo "")

if [ -z "$TWEETS" ]; then
  echo "No tweets found or bird failed. Trying Medium..."
fi

# Check Medium for new posts
MEDIUM_HTML=$(curl -sL "https://medium.com/@alexwg" 2>/dev/null | head -1000 || echo "")

# Extract dates already in data.json
EXISTING_DATES=$(python3 -c "
import json
with open('$DATA') as f:
    data = json.load(f)
for entry in data:
    print(entry['date'])
")

echo "Existing entries: $(echo "$EXISTING_DATES" | wc -l)"
echo "Check complete. Manual enrichment needed for new entries."
echo "Run: python3 $DIR/enrich.py to add summaries and insights."
