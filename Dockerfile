# Adam - Frankenstein's Agent
# A containerized OpenClaw agent for syntopic reading of the Western canon

FROM node:22-bookworm

# Labels
LABEL org.opencontainers.image.title="Adam - Frankenstein's Agent"
LABEL org.opencontainers.image.description="An autonomous AI agent that reads syntopically across the Western canon"
LABEL org.opencontainers.image.source="https://github.com/agentadam2026/Adam"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    jq \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@10.0.0 --activate

# Install OpenClaw globally
RUN npm install -g openclaw

# Create non-root user for security
RUN useradd -m -s /bin/bash adam
USER adam
WORKDIR /home/adam

# Set up Python virtual environment
RUN python3 -m venv /home/adam/.venv
ENV PATH="/home/adam/.venv/bin:$PATH"

# Copy adam-tools and install
COPY --chown=adam:adam packages/adam-agent/tools /home/adam/tools
WORKDIR /home/adam/tools
RUN pip install --no-cache-dir -e .

# Copy agent configuration files
COPY --chown=adam:adam packages/adam-agent/AGENTS.md /home/adam/.openclaw/workspace/AGENTS.md
COPY --chown=adam:adam packages/adam-agent/SOUL.md /home/adam/.openclaw/workspace/SOUL.md
COPY --chown=adam:adam packages/adam-agent/USER.md /home/adam/.openclaw/workspace/USER.md
COPY --chown=adam:adam packages/adam-agent/MEMORY.md /home/adam/.openclaw/workspace/MEMORY.md
COPY --chown=adam:adam packages/adam-agent/IDENTITY.md /home/adam/.openclaw/workspace/IDENTITY.md
COPY --chown=adam:adam packages/adam-agent/TOOLS.md /home/adam/.openclaw/workspace/TOOLS.md
COPY --chown=adam:adam packages/adam-agent/HEARTBEAT.md /home/adam/.openclaw/workspace/HEARTBEAT.md

# Copy library (CANON.md and any downloaded texts)
COPY --chown=adam:adam packages/adam-agent/library /home/adam/library

# Copy database schema
COPY --chown=adam:adam packages/adam-agent/db /home/adam/db

# Copy skills
COPY --chown=adam:adam packages/adam-agent/skills /home/adam/.openclaw/skills

# Create directories that will be mounted as volumes
RUN mkdir -p /home/adam/.openclaw/workspace/memory \
    /home/adam/library/gutenberg \
    /home/adam/library/other

WORKDIR /home/adam

# Download embedding model on build (optional, can be done at runtime)
# Uncomment to bake the model into the image (adds ~500MB)
# RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-base-en-v1.5')"

# Expose OpenClaw gateway port
EXPOSE 18789

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:18789/health || exit 1

# Default command - start OpenClaw gateway
CMD ["openclaw", "gateway"]
