#!/bin/bash
# Adam Docker Entrypoint
# Ensures directories exist and config is set up

set -e

CONFIG_FILE="/home/adam/.openclaw/openclaw.json"
DEFAULT_CONFIG="/home/adam/default-openclaw.json"

# Create .openclaw directory if it doesn't exist
mkdir -p /home/adam/.openclaw/workspace

# Copy minimal config if none exists (just gateway.mode=local)
# Full config is created by `openclaw setup` with Codex OAuth
if [ ! -f "$CONFIG_FILE" ]; then
    echo "No config found, copying minimal default..."
    cp "$DEFAULT_CONFIG" "$CONFIG_FILE"
    echo "Config initialized. Run 'openclaw setup' to configure Codex OAuth."
fi

# Execute the main command
exec "$@"
