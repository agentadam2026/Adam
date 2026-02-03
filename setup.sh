#!/bin/bash
# Setup script for Adam's workspace
# Run this once on Adam's machine to initialize everything.

set -e

echo "═══════════════════════════════════════════════════"
echo "  Setting up Adam's workspace"
echo "═══════════════════════════════════════════════════"
echo

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python $PYTHON_VERSION found"

# Create directory structure
echo
echo "Creating directories..."
mkdir -p library/gutenberg library/other db memory skills
echo "✓ Directories created"

# Install Python tools
echo
echo "Installing adam-tools..."
cd tools
pip install -e . 2>&1 | tail -5
cd ..
echo "✓ adam-tools installed"

# Initialize database
echo
echo "Initializing database..."
adam-init
echo "✓ Database ready"

# Download embedding model (this takes a while on first run)
echo
echo "Downloading embedding model (BAAI/bge-base-en-v1.5)..."
echo "This may take a few minutes on first run..."
python3 -c "
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('BAAI/bge-base-en-v1.5')
dims = model.get_sentence_embedding_dimension()
print(f'✓ Model loaded ({dims} dimensions)')
"

echo
echo "═══════════════════════════════════════════════════"
echo "  Setup complete!"
echo "═══════════════════════════════════════════════════"
echo
echo "  Available commands:"
echo "    adam-fetch <gutenberg_id>   Download a text"
echo "    adam-ingest <path>          Chunk + embed a text"
echo "    adam-search <query>         Semantic search"
echo "    adam-read <chunk_id>        Read a chunk"
echo "    adam-context <chunk_id>     Read with context"
echo "    adam-stats                  Corpus overview"
echo "    adam-library                Reading list"
echo "    adam-log                    Write daily log"
echo "    adam-note <source>          Write reading notes"
echo "    adam-trail                  Manage trails"
echo "    adam-essay                  Manage essays"
echo "    adam-tweet <text>           Save tweet draft"
echo "    adam-sync                   Push to Turso"
echo
echo "  Try: adam-fetch 41445  (downloads Frankenstein)"
echo
