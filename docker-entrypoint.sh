#!/bin/bash
# Adam Docker Entrypoint
# Ensures config exists before starting gateway

set -e

CONFIG_FILE="/home/adam/.openclaw/openclaw.json"
DEFAULT_CONFIG="/home/adam/default-openclaw.json"

# Create .openclaw directory if it doesn't exist
mkdir -p /home/adam/.openclaw/workspace

# Copy default config if none exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "No config found, copying default..."
    cp "$DEFAULT_CONFIG" "$CONFIG_FILE"
    echo "Config initialized at $CONFIG_FILE"
fi

# Execute the main command
exec "$@"
