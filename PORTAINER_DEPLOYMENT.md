# Portainer Stack Template for Ski Marketplace Search Tool

This template can be copied directly into Portainer's Stack creation interface.

## Prerequisites

1. **Portainer installed** on your Proxmox instance
2. **Docker endpoint** configured in Portainer
3. **Environment variables** prepared (see below)

---

## Option 1: Deploy from Git Repository (Recommended)

### Steps in Portainer:

1. Navigate to **Stacks** → **Add Stack**
2. Name: `ski-marketplace-search`
3. Build method: **Repository**
4. Repository URL: `https://github.com/yourusername/SkiSearchTool`
5. Repository reference: `refs/heads/main`
6. Compose path: `docker-compose.yml`
7. Add environment variables (see below)
8. Click **Deploy the stack**

### Environment Variables to Add:

```env
GITHUB_REPO_URL=yourusername/ski-search-config
GITHUB_ACCESS_TOKEN=ghp_your_token_here
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
EBAY_APP_ID=your_ebay_app_id
EBAY_CERT_ID=your_ebay_cert_id
EBAY_DEV_ID=your_ebay_dev_id
LOG_LEVEL=INFO
SEARCH_INTERVAL_MINUTES=15
MAX_NOTIFICATIONS_PER_HOUR=20
TZ=America/Los_Angeles
```

---

## Option 2: Deploy via Web Editor (Manual)

### Steps in Portainer:

1. Navigate to **Stacks** → **Add Stack**
2. Name: `ski-marketplace-search`
3. Build method: **Web editor**
4. Copy and paste the stack definition below
5. Add environment variables
6. Click **Deploy the stack**

### Stack Definition:

```yaml
version: '3.8'

services:
  ski-search:
    image: ghcr.io/yourusername/ski-search-tool:latest
    # Or build from source:
    # build:
    #   context: https://github.com/yourusername/SkiSearchTool.git
    #   dockerfile: Dockerfile
    
    container_name: ski-marketplace-search
    restart: unless-stopped
    
    environment:
      # Configured via Portainer environment variables (see below)
      - GITHUB_REPO_URL=${GITHUB_REPO_URL}
      - GITHUB_ACCESS_TOKEN=${GITHUB_ACCESS_TOKEN}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
      - EBAY_APP_ID=${EBAY_APP_ID:-}
      - EBAY_CERT_ID=${EBAY_CERT_ID:-}
      - EBAY_DEV_ID=${EBAY_DEV_ID:-}
      - DATABASE_URL=sqlite:///data/ski_search.db
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - SEARCH_INTERVAL_MINUTES=${SEARCH_INTERVAL_MINUTES:-15}
      - MAX_NOTIFICATIONS_PER_HOUR=${MAX_NOTIFICATIONS_PER_HOUR:-20}
      - TZ=${TZ:-America/Los_Angeles}
    
    volumes:
      - ski-search-data:/app/data
      - ski-search-logs:/app/logs
      - ski-search-cache:/app/cache
    
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.1'
          memory: 128M
    
    healthcheck:
      test: ["CMD-SHELL", "python -c 'import sys; sys.exit(0)' || exit 1"]
      interval: 5m
      timeout: 10s
      retries: 3
      start_period: 30s
    
    labels:
      - "com.portainer.description=Automated ski marketplace search"
      - "com.portainer.group=monitoring"

volumes:
  ski-search-data:
    driver: local
  ski-search-logs:
    driver: local
  ski-search-cache:
    driver: local
```

---

## Proxmox-Specific Configuration

### Recommended LXC Container Specs (Debian/Ubuntu):

```
Container Type: Unprivileged
OS: Ubuntu 22.04 LTS
Cores: 1-2
RAM: 1GB (512MB minimum)
Storage: 8GB (for OS + Docker)
Network: DHCP or Static IP
Features: 
  - Nesting: Yes (required for Docker)
  - Keyctl: No
```

### LXC Container Setup:

```bash
# After creating LXC container in Proxmox:

# 1. Update and install Docker
apt update && apt upgrade -y
apt install -y docker.io docker-compose

# 2. Enable and start Docker
systemctl enable docker
systemctl start docker

# 3. Install Portainer (if not already on Proxmox)
docker run -d \
  --name=portainer \
  --restart=always \
  -p 9000:9000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest

# 4. Access Portainer at http://<LXC-IP>:9000
```

---

## Managing the Stack in Portainer

### Starting/Stopping:
1. Navigate to **Stacks** → `ski-marketplace-search`
2. Click **Stop** or **Start**

### Viewing Logs:
1. Navigate to **Containers** → `ski-marketplace-search`
2. Click **Logs**
3. View real-time or historical logs

### Updating Environment Variables:
1. Navigate to **Stacks** → `ski-marketplace-search`
2. Click **Editor**
3. Modify environment variables
4. Click **Update the stack**

### Viewing Resource Usage:
1. Navigate to **Containers** → `ski-marketplace-search`
2. Click **Stats**
3. View CPU, Memory, Network usage

### Accessing Container Shell:
1. Navigate to **Containers** → `ski-marketplace-search`
2. Click **Console**
3. Execute commands: `/bin/bash`

---

## Volume Management

Portainer makes it easy to manage persistent data:

### Backup Volumes:
1. Navigate to **Volumes** → `ski-search-data`
2. Click **Browse**
3. Download files or entire database

### View Database:
```bash
# From Portainer console:
sqlite3 /app/data/ski_search.db

# View recent searches:
SELECT * FROM search_runs ORDER BY started_at DESC LIMIT 10;

# View seen listings:
SELECT * FROM seen_listings ORDER BY first_seen DESC LIMIT 20;
```

### Clear Cache:
```bash
# From Portainer console:
rm -rf /app/cache/*
```

---

## Monitoring & Alerts

### Health Check Status:
- Portainer automatically monitors container health
- Failed health checks trigger alerts
- Configure in: **Settings** → **Notifications**

### Log Monitoring:
```bash
# View logs via Portainer or CLI:
docker logs -f ski-marketplace-search

# View specific log files:
docker exec ski-marketplace-search tail -f /app/logs/ski_search.log
```

### Resource Alerts:
Configure in Portainer → **Home** → Container → **Resource Limits**

---

## Updating the Application

### Method 1: Via Portainer (Git Repository)
1. Navigate to **Stacks** → `ski-marketplace-search`
2. Click **Pull and redeploy**
3. Confirm

### Method 2: Manual Update
```bash
# SSH into Proxmox LXC container
docker pull ghcr.io/yourusername/ski-search-tool:latest
docker-compose down
docker-compose up -d
```

### Method 3: Recreate Stack
1. Delete stack in Portainer
2. Redeploy with updated configuration
3. Volumes persist automatically

---

## Troubleshooting in Portainer

### Container Won't Start:
1. Check logs: **Containers** → **Logs**
2. Verify environment variables are set
3. Check resource limits
4. Verify Docker socket access

### Can't Access Logs:
1. Ensure logging driver is correct
2. Check disk space: `df -h`
3. Restart Docker: `systemctl restart docker`

### High Resource Usage:
1. Check **Stats** tab
2. Adjust resource limits in stack definition
3. Review scraper rate limits

### Database Locked:
1. Stop container
2. Backup database
3. Check file permissions
4. Restart container

---

## Security Best Practices

### Secrets Management in Portainer:
1. Don't hardcode secrets in stack definition
2. Use Portainer environment variables (hidden)
3. Or use Docker secrets for production

### Example with Docker Secrets:
```yaml
services:
  ski-search:
    secrets:
      - github_token
      - telegram_token
    environment:
      - GITHUB_ACCESS_TOKEN_FILE=/run/secrets/github_token
      - TELEGRAM_BOT_TOKEN_FILE=/run/secrets/telegram_token

secrets:
  github_token:
    external: true
  telegram_token:
    external: true
```

Create secrets in Portainer: **Secrets** → **Add secret**

---

## Backup Strategy

### Automated Backup Script:

```bash
#!/bin/bash
# backup-ski-search.sh

BACKUP_DIR="/backups/ski-search"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker exec ski-marketplace-search \
  sqlite3 /app/data/ski_search.db ".backup /app/data/backup_$DATE.db"

# Copy to backup location
docker cp ski-marketplace-search:/app/data/backup_$DATE.db \
  $BACKUP_DIR/

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "*.db" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/backup_$DATE.db"
```

Schedule in cron:
```bash
# Daily backup at 3 AM
0 3 * * * /path/to/backup-ski-search.sh
```

---

## Network Configuration

### Proxmox Bridge Network:
- Container can share Proxmox host network
- Access via Proxmox host IP

### Dedicated VLAN (Advanced):
1. Create VLAN in Proxmox
2. Assign to LXC container
3. Update Portainer endpoint
4. Access via VLAN IP

### Reverse Proxy (Optional):
If you want web dashboard in future:
- Nginx Proxy Manager (via Portainer)
- Traefik (via Docker Compose)
- Configure SSL/TLS

---

## Quick Deploy Checklist

- [ ] Proxmox LXC container created with nesting enabled
- [ ] Docker installed in container
- [ ] Portainer accessible
- [ ] GitHub config repo created
- [ ] Telegram bot created and token obtained
- [ ] Environment variables prepared
- [ ] Stack deployed via Portainer
- [ ] Container health check passing
- [ ] Test notification received
- [ ] Logs show successful GitHub sync
- [ ] First search completed successfully

---

## Support & Resources

- **Container Logs**: Portainer → Containers → Logs
- **Stack Logs**: Portainer → Stacks → Logs
- **Health Status**: Portainer → Containers → Stats
- **Database**: Access via Portainer Console
- **Documentation**: See DESIGN.md and SETUP.md

---

**Portainer Version Tested:** 2.19+  
**Docker Version Required:** 20.10+  
**Proxmox Version Tested:** 8.0+
