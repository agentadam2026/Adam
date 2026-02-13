#!/bin/bash
# Adam Docker Setup Script
# 
# This script builds and starts Adam in a Docker container.
# Run from the repository root: ./docker-setup.sh

set -e

echo "═══════════════════════════════════════════════════"
echo "  Setting up Adam - Frankenstein's Agent"
echo "═══════════════════════════════════════════════════"
echo

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "✗ Docker is required but not installed."
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "✗ Docker daemon is not running."
    exit 1
fi

echo "✓ Docker is available"

# Check for .env file
if [ ! -f .env ]; then
    echo
    echo "Creating .env file..."
    cat > .env << 'EOF'
# Adam Environment Variables
# Add your API keys here

# OpenAI (required - Adam uses gpt-4o by default)
OPENAI_API_KEY=

# Anthropic (optional, for switching models later)
ANTHROPIC_API_KEY=
EOF
    echo "✓ Created .env file - add your OPENAI_API_KEY before starting"
fi

# Build the image
echo
echo "Building Adam Docker image..."
docker compose build adam
echo "✓ Image built"

# Initialize database if not exists
echo
echo "Checking database..."
if ! docker volume inspect adam-database &> /dev/null; then
    echo "Creating database volume and initializing schema..."
    docker compose run --rm adam-cli sh -c "cd /home/adam && adam-init"
    echo "✓ Database initialized"
else
    echo "✓ Database volume exists"
fi

# Download embedding model (optional, can take a while)
echo
read -p "Download embedding model now? This adds ~500MB but speeds up first run. [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Downloading embedding model (BAAI/bge-base-en-v1.5)..."
    docker compose run --rm adam-cli python3 -c \
        "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('BAAI/bge-base-en-v1.5'); print(f'✓ Model loaded ({m.get_sentence_embedding_dimension()} dimensions)')"
fi

echo
echo "═══════════════════════════════════════════════════"
echo "  Setup complete!"
echo "═══════════════════════════════════════════════════"
echo
echo "  Next steps:"
echo
echo "  1. Configure Codex OAuth (uses your ChatGPT subscription):"
echo "     docker compose run --rm adam openclaw setup"
echo
echo "     - Select 'OpenAI Codex with ChatGPT OAuth'"
echo "     - Open the URL it gives you in your browser"
echo "     - Copy the redirect URL (even if it shows an error)"
echo "     - Paste it back into the terminal"
echo
echo "  2. Start Adam:"
echo "     docker compose up -d"
echo
echo "  3. View logs:"
echo "     docker compose logs -f"
echo
echo "  4. Access web UI:"
echo "     http://localhost:18789"
echo
echo "  5. Run adam-tools commands:"
echo "     docker compose exec adam adam-stats"
echo "     docker compose exec adam adam-fetch 41445"
echo
echo "  6. Stop Adam:"
echo "     docker compose down"
echo
