# OpenClaw Docker Research

Research compiled 2026-02-13 for running Adam in Docker.

## Official Documentation

**Source:** docs.openclaw.ai/install/docker

### Quick Start
```bash
git clone https://github.com/openclaw/openclaw
cd openclaw
./docker-setup.sh
```

Builds the image, runs onboarding, starts gateway via Docker Compose, writes config to `~/.openclaw/`.

### Key Environment Variables
- `OPENCLAW_DOCKER_APT_PACKAGES` — bake system deps into image (e.g., `"ffmpeg build-essential python3"`)
- `OPENCLAW_EXTRA_MOUNTS` — mount additional host directories
- `OPENCLAW_HOME_VOLUME` — persist `/home/node` across container restarts

### Architecture Options
1. **Containerized Gateway** — full OpenClaw in Docker (what we want for Adam)
2. **Agent Sandbox** — host gateway + Docker-isolated tool execution per session

### Ports
- `18789` — Web UI / dashboard
- `18793` — Gateway API

---

## Simon Willison's Practical Notes

**Source:** til.simonwillison.net/llms/openclaw-docker

### Gotchas
1. Onboarding mode → select "manual"
2. Gateway type → "Local gateway (this machine)"
3. Tailscale → say "no" (caused issues)
4. OAuth callback shows error page → copy the localhost URL and paste back

### Useful Commands
```bash
# Get dashboard URL with token
docker compose run --rm openclaw-cli dashboard --no-open

# Telegram channel setup
docker compose run --rm openclaw-cli channels add --channel telegram --token "<token>"

# Approve pairing
docker compose run --rm openclaw-cli pairing approve telegram <CODE>

# Root shell to install packages
docker compose exec -u root openclaw-gateway bash
apt-get update && apt-get install -y ripgrep
```

---

## Twitter Best Practices

### @btibor91 (Tibor Blaho)
> "OpenClaw is now running on my Lenovo ThinkStation in a Docker container, and it has also learned how to use a local ComfyUI instance and created a skill itself"

- Running in Docker + connecting to local services (ComfyUI, local LLMs)

### @elliot_garreffa
> "OpenClaw on a $12/month VPS. Docker container."

- Basic setup: VPS + Docker is the standard deployment pattern

### @avysotsky (Artem Vysotsky)
> "Setup is painful. Docker permissions, API keys from three providers, OAuth callbacks to localhost that break"

- Pain points: permissions, API keys, OAuth flow

### @techie_piyush (AWS EC2 guide)
- Create folders manually and set permissions so both you AND Docker can write
- Do NOT select "Serve" for Tailscale — causes crashes
- The bot blocks browser on HTTP (need HTTPS proxy for production)

### @matthewjetthall
> "Inside Docker, the bot runs on Linux Node, which handles the Telegram handshake perfectly. It uses your existing config folder (.openclaw), so all your settings stay the same."

---

## Recommended Approach for Adam

### 1. Custom Dockerfile
```dockerfile
FROM openclaw:local

# Install Python tools for Adam
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv

# Copy Adam's agent files
COPY packages/adam-agent/ /home/node/adam-agent/

# Install adam-tools
WORKDIR /home/node/adam-agent/tools
RUN pip install -e .

WORKDIR /home/node
```

### 2. Mount Adam's Data
```bash
export OPENCLAW_EXTRA_MOUNTS="$HOME/projects/Adam/packages/adam-agent:/home/node/adam-agent:rw"
```

### 3. Persist Home Volume
```bash
export OPENCLAW_HOME_VOLUME="adam_home"
```

### 4. Use Telegram
Cleanest channel for container setup.

---

## Key Decisions

| Decision | Recommendation |
|----------|----------------|
| Gateway location | In container (isolated) |
| Channel | Telegram (easiest for Docker) |
| Model | Start with Anthropic Claude (existing API key) |
| Persistence | Named volume for `/home/node` |
| Extra packages | Python 3.11+, pip, sentence-transformers deps |

---

## Next Steps

1. [ ] Draft Dockerfile for Adam
2. [ ] Create docker-compose.yml
3. [ ] Test locally
4. [ ] Set up Telegram bot for Adam
5. [ ] Configure model/API access
