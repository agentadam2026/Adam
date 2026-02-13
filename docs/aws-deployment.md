# AWS Deployment Research

## Recommended Setup

### Instance
- **OS:** Ubuntu 24.04 LTS
- **Size:** t3.small (~$15/month) or t3.medium (~$30/month) if more RAM needed
- **Storage:** 20GB EBS (~$2/month)
- **Region:** us-east-1 (cheapest) or closest to user

### Security Hardening (Critical)

1. **Create dedicated user** (don't run as root):
   ```bash
   sudo adduser adam
   sudo usermod -aG sudo adam
   ```

2. **SSH hardening:**
   - Move SSH to non-standard port (e.g., 2222)
   - Disable password auth, require key-based SSH only
   - Disable root login
   - Set up UFW firewall
   
   ```bash
   # UFW setup
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow 2222/tcp
   sudo ufw enable
   ```

3. **AWS Security Groups:**
   - Allow inbound on SSH port (2222) from your IP only
   - No other inbound ports needed (Telegram is outbound only)

4. **Tailscale (recommended):**
   - Creates private mesh network
   - Access Control UI without exposing ports
   - Simple install: `curl -fsSL https://tailscale.com/install.sh | sh`

### Docker Setup

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker adam

# Clone and run
git clone https://github.com/agentadam2026/Adam.git
cd Adam
docker compose up -d
```

### Persistence (Critical)

All state must survive container restarts. Use host volume mounts:

| Data | Host Path | Container Path |
|------|-----------|----------------|
| OpenClaw config | `/home/adam/.openclaw/` | `/home/node/.openclaw/` |
| SQLite database | `/home/adam/Adam/packages/adam-agent/db/` | `/app/packages/adam-agent/db/` |
| Library (texts) | `/home/adam/Adam/library/` | `/app/library/` |

### Model Access

Three options:
1. **Codex OAuth** (current): Uses ChatGPT subscription (~$20/month flat)
2. **API keys**: Anthropic Claude or OpenAI (pay per token)
3. **Local models**: Requires GPU instance (expensive, not recommended)

### Update Workflow

Manual:
```bash
ssh -p 2222 adam@YOUR_VPS_IP
cd ~/Adam
git pull
docker compose build
docker compose up -d
```

Or configure GitHub Actions for CI/CD.

### Access Options

1. **SSH tunnel** (for Control UI):
   ```bash
   ssh -N -L 18789:127.0.0.1:18789 -p 2222 adam@YOUR_VPS_IP
   ```
   Then open `http://127.0.0.1:18789`

2. **Tailscale** (recommended):
   - Both machines on same tailnet
   - Access via Tailscale IP directly

3. **Telegram**: Works without port exposure (outbound only)

### Cost Estimate

| Item | Monthly Cost |
|------|--------------|
| EC2 t3.small | ~$15 |
| EC2 t3.medium | ~$30 |
| EBS storage (20GB) | ~$2 |
| Data transfer | minimal |
| **Total** | **~$17-35** |

Plus model costs if not using Codex OAuth (~$20/month for ChatGPT Pro).

## References

- [DEV.to: AWS EC2 + Docker + Tailscale](https://dev.to/aws-builders/deploy-your-own-247-ai-agent-on-aws-ec2-with-docker-tailscale-the-secure-way-53aa)
- [Pulumi: Deploy OpenClaw on AWS/Hetzner](https://www.pulumi.com/blog/deploy-openclaw-aws-hetzner/)
- [OpenClaw Docs: Hetzner/Docker VPS](/opt/homebrew/lib/node_modules/openclaw/docs/platforms/hetzner.md)
